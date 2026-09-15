#!/usr/bin/env python3
"""Create a Testmo run from a reviewable JSON filter spec.

Reproduces the manual "filter cases -> create run" workflow via the API so it is repeatable.
Read-only unless --create is passed. The API key is read from the environment and never printed,
and never placed on a command line: argv is world-readable via `ps`. Requests go through urllib
in-process; on a network with TLS interception, where OpenSSL cannot verify the chain, they fall
back to curl with the header passed on stdin.

Filter model (all keys under "filters" are optional; a case must match every key present):
  tags                    list of Testmo tag names or ids. Applied server-side via the /cases API
                          (?tags=...), then combined with any other filters below. e.g. ["oldnew"].
  folder_paths            list of folder paths, e.g. "Web > Password Manager". Matched against the
                          project folder tree; each expands to that folder AND all descendants
                          (unless include_subfolders is false). Paths are OR'd together.
  folder_ids              list of folder ids, same subtree expansion as folder_paths. OR'd with them.
  include_subfolders      default true. When false, folder_paths/folder_ids match that exact folder only.
  test_type_ids           case matches if its Test Type set intersects this list (multiselect field).
  team_ids                case matches if its Team set intersects this list (multiselect field).
  case_state_ids          case state_id must be in this list (e.g. [4] = Active).
  automation_type_ids     case automation type must be in this list. Use null in the list to include
                          cases with no automation type set.
  exclude_automation_type_ids  case is dropped if its automation type is in this list
                          (e.g. [10, 23, 24] = Automated / Automated-Android / Automated-iOS).
  has_automation          bool; case has_automation flag must equal this.
"""
import argparse, json, os, shutil, ssl, subprocess, sys, tempfile, urllib.error, urllib.request

BASE = "https://bitwarden.testmo.net/api/v1"
KEY = os.environ.get("TESTMO_API_KEY")
TIMEOUT = 60

# Set once a TLS verification failure proves this Python cannot validate the chain (see _curl_call).
_USE_CURL = False

class TestmoAPIError(Exception):
    """A Testmo API request did not return a usable JSON response.

    Raised rather than exiting so callers can decide: the single-run script aborts, while the
    release orchestrator records the failed run and carries on to report a full tally.
    Messages are built from the request line and the response body only, never the API key.
    """

class _TLSVerificationError(Exception):
    """Internal: the certificate chain did not verify. Triggers the curl fallback."""

def _redact(text):
    """Strip the API key from anything before it is printed or raised."""
    return text.replace(KEY, "<redacted>") if KEY else text

def _decode(method, path, raw):
    try:
        return json.loads(raw)
    except json.JSONDecodeError as e:
        # A proxy or login-wall HTML page can arrive with a 200; don't let it become a traceback.
        raise TestmoAPIError(
            f"{method} {path} returned a non-JSON body ({e}). First 200 characters:\n{raw[:200]!r}"
        )

def _auth_hint(code):
    return "  (is TESTMO_API_KEY current?)" if code in (401, 403) else ""

def _urllib_call(method, path, body):
    """Preferred transport: the Authorization header never leaves this process."""
    data = json.dumps(body).encode() if body is not None else None
    req = urllib.request.Request(BASE + path, data=data, method=method)
    req.add_header("Authorization", f"Bearer {KEY}")
    req.add_header("Accept", "application/json")
    if data is not None:
        req.add_header("Content-Type", "application/json")
    try:
        with urllib.request.urlopen(req, timeout=TIMEOUT) as resp:
            raw = resp.read().decode(errors="replace")
    except urllib.error.HTTPError as e:
        # e.read() is the API's error body; it echoes the request but not the auth header.
        detail = e.read().decode(errors="replace").strip()
        raise TestmoAPIError(
            f"{method} {path} failed: HTTP {e.code} {e.reason}{_auth_hint(e.code)}\n{detail[:500]}"
        )
    except urllib.error.URLError as e:
        if isinstance(e.reason, ssl.SSLCertVerificationError):
            raise _TLSVerificationError(str(e.reason))
        raise TestmoAPIError(f"{method} {path} failed: {e.reason}")
    return _decode(method, path, raw)

def _curl_call(method, path, body):
    """Fallback transport for networks running TLS interception.

    A corporate proxy (Zscaler and friends) re-signs traffic with a root that is installed in the
    OS trust store but is absent from certifi, and whose Basic Constraints are not marked
    critical — which Python 3.13+ rejects outright, since it enables VERIFY_X509_STRICT by
    default. curl uses the platform trust store and is not strict, so it succeeds where urllib
    cannot.

    The key is still kept out of argv: the Authorization header is fed to `curl --config -` on
    stdin. Any request body goes to a 0600 temp file, referenced by path — the body is not
    secret, and this keeps stdin free for the config.
    """
    marker = "__TESTMO_HTTP_STATUS__"
    config = [
        "silent", "show-error", f"max-time = {TIMEOUT}",
        f'url = "{BASE + path}"',
        f'request = "{method}"',
        f'header = "Authorization: Bearer {KEY}"',
        'header = "Accept: application/json"',
        f'write-out = "\\n{marker}%{{http_code}}"',
    ]
    body_file = None
    try:
        if body is not None:
            fd, body_file = tempfile.mkstemp(prefix="testmo-body-", suffix=".json")
            with os.fdopen(fd, "w") as fh:
                json.dump(body, fh)
            config += ['header = "Content-Type: application/json"', f'data-binary = "@{body_file}"']
        proc = subprocess.run(["curl", "--config", "-"], input="\n".join(config) + "\n",
                              capture_output=True, text=True)
    finally:
        if body_file:
            os.unlink(body_file)
    if proc.returncode != 0:
        # Redact: a config parse error can echo the offending line back on stderr.
        raise TestmoAPIError(
            f"{method} {path} failed: curl exited {proc.returncode}\n{_redact(proc.stderr.strip())}"
        )
    raw, found, status = proc.stdout.rpartition(marker)
    if not found:
        raise TestmoAPIError(f"{method} {path} failed: curl returned no status code")
    try:
        code = int(status.strip())
    except ValueError:
        raise TestmoAPIError(f"{method} {path} failed: unreadable status {status.strip()!r}")
    if not 200 <= code < 300:
        raise TestmoAPIError(
            f"{method} {path} failed: HTTP {code}{_auth_hint(code)}\n{raw.strip()[:500]}"
        )
    return _decode(method, path, raw)

def call(method, path, body=None):
    """Issue a Testmo API request and return the decoded JSON body.

    Prefers urllib, so the Authorization header stays in this process — passing it as a curl
    argument would expose the key to any local user for the life of the request (`ps auxww`,
    /proc/<pid>/cmdline). Falls back to curl only when the TLS chain will not verify, which on a
    corporate network is not a fixable condition; that path keeps the key off argv too.

    Any non-2xx status raises, so an expired key (401) or a rejected write (403) surfaces as an
    error instead of an empty case list or a run "created" with id None.
    """
    global _USE_CURL
    if not KEY:
        sys.exit("TESTMO_API_KEY not set")
    if _USE_CURL:
        return _curl_call(method, path, body)
    try:
        return _urllib_call(method, path, body)
    except _TLSVerificationError as e:
        if not shutil.which("curl"):
            raise TestmoAPIError(
                f"{method} {path} failed: TLS certificate verification failed ({e}), and curl is "
                f"not on PATH to fall back to.\nThis usually means a TLS-inspecting proxy whose "
                f"root CA this Python does not trust. Try the system python3, or install curl."
            )
        print(f"NOTE: TLS verification failed ({e}).\n"
              f"      A TLS-inspecting proxy is likely in the path. Falling back to curl, which "
              f"uses the OS trust store, for this and all later requests.", file=sys.stderr)
        _USE_CURL = True
        return _curl_call(method, path, body)

def fetch_all(project, resource, query=""):
    out, page = [], 1
    sep = "&" if query else ""
    while True:
        d = call("GET", f"/projects/{project}/{resource}?{query}{sep}page={page}")
        out += d.get("result", [])
        if not d.get("next_page"):
            return out
        page += 1

def fetch_cases(project, filters):
    """Fetch repository cases, applying any tag filter server-side."""
    tags = filters.get("tags")
    query = ("tags=" + ",".join(str(t) for t in tags)) if tags else ""
    return fetch_all(project, "cases", query)

def build_folder_index(folders):
    by_id = {f["id"]: f for f in folders}
    children = {}
    for f in folders:
        children.setdefault(f.get("parent_id"), []).append(f["id"])
    def path(fid):
        parts, f = [], by_id.get(fid)
        while f:
            parts.append(f["name"])
            f = by_id.get(f.get("parent_id"))
        return " > ".join(reversed(parts))
    paths = {fid: path(fid) for fid in by_id}
    return by_id, children, paths

def subtree(root, children):
    seen, stack = set(), [root]
    while stack:
        n = stack.pop()
        seen.add(n)
        stack += children.get(n, [])
    return seen

def resolve_folders(spec_filters, project, folders=None):
    """Return (folder_id_set, notes). Empty set means 'no folder filter'.

    Pass a prefetched `folders` list to avoid refetching (e.g. when resolving many specs)."""
    want_paths = spec_filters.get("folder_paths") or []
    want_ids = spec_filters.get("folder_ids") or []
    if not want_paths and not want_ids:
        return None, []
    include_sub = spec_filters.get("include_subfolders", True)
    if folders is None:
        folders = fetch_all(project, "folders")
    by_id, children, paths = build_folder_index(folders)
    norm = {p.strip().lower(): fid for fid, p in paths.items()}
    roots, notes = [], []
    for p in want_paths:
        fid = norm.get(p.strip().lower())
        if fid is None:
            notes.append(f"UNMATCHED folder_path: {p!r}")
        else:
            roots.append(fid)
            notes.append(f"ok  {p}  -> id={fid}")
    for fid in want_ids:
        if fid in by_id:
            roots.append(fid)
            notes.append(f"ok  id={fid}  -> {paths[fid]}")
        else:
            notes.append(f"UNKNOWN folder_id: {fid}")
    result = set()
    for r in roots:
        result |= subtree(r, children) if include_sub else {r}
    return result, notes

def matches(case, spec, folder_ids):
    if folder_ids is not None and case.get("folder_id") not in folder_ids:
        return False
    if spec.get("test_type_ids"):
        ids = {t["id"] for t in (case.get("custom_test_type") or [])}
        if not ids & set(spec["test_type_ids"]):
            return False
    if spec.get("team_ids"):
        ids = {t["id"] for t in (case.get("custom_team") or [])}
        if not ids & set(spec["team_ids"]):
            return False
    # custom_automation_type is a single {"id", "name"} object, or null when unset.
    # Compare on the id so specs can list plain ints (and null for "no type set").
    auto = case.get("custom_automation_type")
    auto_id = auto["id"] if auto else None
    if "automation_type_ids" in spec and auto_id not in spec["automation_type_ids"]:
        return False
    if spec.get("exclude_automation_type_ids") and auto_id in spec["exclude_automation_type_ids"]:
        return False
    if spec.get("case_state_ids") and case.get("state_id") not in spec["case_state_ids"]:
        return False
    if "has_automation" in spec and bool(case.get("has_automation")) != bool(spec["has_automation"]):
        return False
    return True

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--spec", required=True, help="path to JSON filter spec")
    ap.add_argument("--create", action="store_true", help="actually POST the run (omit for dry-run)")
    ap.add_argument("--milestone-id", type=int, default=None,
                    help="link the run to this existing milestone id (overrides the spec). "
                         "Milestones must be created in the Testmo UI first — the API cannot create them.")
    ap.add_argument("--period", default=None,
                    help="substitute this string for the literal <period> in run_name, e.g. 2026.8.0")
    args = ap.parse_args()
    spec = json.load(open(args.spec))
    if args.milestone_id is not None:
        spec["milestone_id"] = args.milestone_id
    if args.period is not None:
        spec["run_name"] = spec["run_name"].replace("<period>", args.period)

    project = spec["project_id"]
    filters = spec.get("filters", {})

    folder_ids, notes = resolve_folders(filters, project)
    if notes:
        print("--- folder resolution ---")
        for n in notes:
            print(f"  {n}")
        unmatched = [n for n in notes if n.startswith(("UNMATCHED", "UNKNOWN"))]
        if unmatched:
            sys.exit(f"\n{len(unmatched)} folder reference(s) did not resolve — fix the spec before continuing.")
        print(f"  => {len(folder_ids)} folders in scope\n")

    cases = fetch_cases(project, filters)
    selected = [c for c in cases if matches(c, filters, folder_ids)]
    ids = [c["id"] for c in selected]

    print(f"Project {project}: {len(cases)} total cases -> {len(ids)} match filter")
    for c in selected[:10]:
        tt = ",".join(t["name"] for t in (c.get("custom_test_type") or [])) or "-"
        print(f'  id={c["id"]} folder={c.get("folder_id")} type={tt} auto={c.get("custom_automation_type")} state={c.get("state_id")}')
    if len(ids) > 10:
        print(f"  ... +{len(ids)-10} more")

    payload = {
        "name": spec["run_name"],
        "state_id": spec.get("run_state_id", 7),
        "include_all": False,
        "cases": ids,
    }
    for k in ("milestone_id", "config_id", "tags", "note"):
        if k in spec and spec[k] is not None:
            payload[k] = spec[k]

    # A spec may ship `"config_id": null` as an explicit placeholder when the run is one of
    # several same-named variants distinguished only by Testmo Configuration (e.g. the three
    # Desktop runs). Dry-runs still work so case counts can be validated, but creating the run
    # would produce indistinguishable runs, so that is refused.
    needs_config = "config_id" in spec and spec["config_id"] is None

    print("\n--- run payload (cases truncated) ---")
    print(json.dumps({**payload, "cases": f"[{len(ids)} ids]"}, indent=2))

    if needs_config:
        print(
            f"\nWARNING: this spec has \"config_id\": null — a placeholder that must be filled in "
            f"before the run can be created.\n"
            f"         Look up the id via GET /projects/{project}/configs and set it in the spec."
        )

    if not args.create:
        print("\nDRY RUN — no run created. Re-run with --create to POST.")
        return
    if needs_config:
        sys.exit(
            "Refusing to create: \"config_id\" is null in this spec. This run is distinguished from "
            f"its same-named siblings only by Configuration, so creating it without one would produce "
            f"indistinguishable runs. Look it up via GET /projects/{project}/configs."
        )
    if not ids:
        sys.exit("Refusing to create a run with 0 cases.")
    res = call("POST", f"/projects/{project}/runs", payload)
    rid = (res.get("result") or {}).get("id")
    if rid is None:
        sys.exit(f"POST succeeded but the response carried no run id — nothing to link to. Response:\n{res}")
    print(f"\nCREATED run id={rid}  https://bitwarden.testmo.net/run/{rid}")

if __name__ == "__main__":
    try:
        main()
    except TestmoAPIError as e:
        sys.exit(str(e))
