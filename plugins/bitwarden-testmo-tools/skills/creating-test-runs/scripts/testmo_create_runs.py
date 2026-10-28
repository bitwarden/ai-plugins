#!/usr/bin/env python3
"""Create Testmo runs from reviewable JSON filter specs.

Reproduces the manual "filter cases -> create run" workflow via the API so it is repeatable.
Pass --spec once per run; a batch fetches the folder tree and case list once, refuses --create
unless every run is ready, and links every run to one milestone when --milestone-id or
--milestone-name is given. Read-only unless --create is passed.

Example:
  python3 testmo_create_runs.py --spec a.json --spec b.json --milestone-name "2026.8.0 Manual Regression"
  python3 testmo_create_runs.py --spec a.json --spec b.json --milestone-name "2026.8.0 Manual Regression" --create

The API key is read from the environment and never printed,
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
import argparse, json, os, shutil, ssl, subprocess, sys, tempfile
from pathlib import Path
import http.client, urllib.error, urllib.parse, urllib.request

BASE = "https://bitwarden.testmo.net/api/v1"
KEY = os.environ.get("TESTMO_API_KEY")
TIMEOUT = 60
# Paging guard: project 1 holds ~13.7k cases, ~137 pages at the 100/page the API allows.
MAX_PAGES = 1000

# Set once a TLS verification failure proves this Python cannot validate the chain (see _curl_call).
_USE_CURL = False

class TestmoAPIError(Exception):
    """A Testmo API request did not return a usable JSON response.

    Raised rather than exiting so callers can decide: a read failure aborts the batch, while a
    failed write is recorded and the create loop carries on to report a full tally.
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

def _unknown_outcome_hint(method):
    """A write that timed out or lost its connection after sending may still have been applied."""
    if method == "GET":
        return ""
    return ("  The request was sent, so the server may still have applied it — check the milestone "
            "in Testmo before re-running.")

# curl exit codes for a failure after the request was sent: 18 partial transfer, 28 timeout,
# 52 empty reply, 56 receive error. A connect failure (6, 7) means nothing reached the server.
_CURL_AFTER_SEND_FAILURES = (18, 28, 52, 56)

class _NoRedirect(urllib.request.HTTPRedirectHandler):
    """Refuse every redirect, so a 3xx surfaces as an HTTPError instead of being followed.

    urllib's default handler copies the request headers — Authorization included — onto the
    redirected request, even when it points at another host. The Testmo API has no reason to
    redirect, so a 3xx here means a proxy or misconfiguration, and following it would hand the key
    to whatever host it names. curl, the fallback transport, does not follow redirects without -L.
    """
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None

_OPENER = urllib.request.build_opener(_NoRedirect)

def _urllib_call(method, path, body):
    """Preferred transport: the Authorization header never leaves this process."""
    data = json.dumps(body).encode() if body is not None else None
    req = urllib.request.Request(BASE + path, data=data, method=method)
    req.add_header("Authorization", f"Bearer {KEY}")
    req.add_header("Accept", "application/json")
    if data is not None:
        req.add_header("Content-Type", "application/json")
    try:
        with _OPENER.open(req, timeout=TIMEOUT) as resp:
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
    except (OSError, http.client.HTTPException) as e:
        # urllib wraps only connect/send errors in URLError. A read timeout or a reset raised by
        # getresponse() or resp.read() arrives bare (TimeoutError, RemoteDisconnected,
        # IncompleteRead), and must still become TestmoAPIError so the create loop records
        # the failure and carries on to its tally instead of dying with a traceback.
        raise TestmoAPIError(
            f"{method} {path} failed: {type(e).__name__}: {e}.{_unknown_outcome_hint(method)}"
        )
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

    *Only* the Authorization header goes through the config; every other directive is an argv
    element. curl's config format is one directive per line, so a value carrying a `"` and a
    newline would inject further directives onto the same config that holds the key — a second
    `url =` would send the authenticated request to an attacker-chosen host. On argv each value is
    one token no matter what it contains, so nothing spec-derived can reach the config parser. The
    remaining interpolation is the key itself, which `_check_key` rejects if it holds a quote or a
    newline.
    """
    marker = "__TESTMO_HTTP_STATUS__"
    argv = [
        "curl", "--silent", "--show-error", "--max-time", str(TIMEOUT),
        "--request", method,
        "--header", "Accept: application/json",
        "--write-out", f"\n{marker}%{{http_code}}",
        "--url", BASE + path,
    ]
    config = [f'header = "Authorization: Bearer {KEY}"']
    body_file = None
    try:
        if body is not None:
            fd, body_file = tempfile.mkstemp(prefix="testmo-body-", suffix=".json")
            with os.fdopen(fd, "w") as fh:
                json.dump(body, fh)
            argv += ["--header", "Content-Type: application/json",
                     "--data-binary", f"@{body_file}"]
        proc = subprocess.run(argv + ["--config", "-"], input="\n".join(config) + "\n",
                              capture_output=True, text=True)
    finally:
        if body_file:
            os.unlink(body_file)
    if proc.returncode != 0:
        # Redact: a config parse error can echo the offending line back on stderr.
        hint = _unknown_outcome_hint(method) if proc.returncode in _CURL_AFTER_SEND_FAILURES else ""
        raise TestmoAPIError(
            f"{method} {path} failed: curl exited {proc.returncode}.{hint}\n"
            f"{_redact(proc.stderr.strip())}"
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

def _check_key():
    """Exit unless TESTMO_API_KEY is set and safe to interpolate into a curl config line."""
    if not KEY:
        sys.exit("TESTMO_API_KEY not set")
    # A backslash cannot inject a directive (that needs a raw newline), but curl processes escapes
    # inside a quoted config value, so it would silently alter the header that is sent.
    if any(c in KEY for c in '"\\\r\n'):
        sys.exit("TESTMO_API_KEY contains a quote, a backslash, or a newline, which cannot be carried "
                 "safely in an HTTP header. Re-copy the key from Testmo (no surrounding quotes).")

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
    _check_key()
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

def project_path_id(value):
    """Return `value` as an int, for interpolation into a request path.

    Every path is built as f"/projects/{project}/…" from the spec's `project_id`, so a non-integer
    value would let a spec steer the URL itself (`1/../..`, a whole `https://…`) rather than just
    name a project. Reject anything that is not an integer id — including `True` and `1.9`, which
    int() would otherwise quietly turn into project 1.
    """
    if isinstance(value, bool):
        raise TestmoAPIError(f'"project_id" must be an integer project id, got {value!r}')
    if isinstance(value, int):
        return value
    if isinstance(value, str) and value.strip().isdigit():
        return int(value)
    raise TestmoAPIError(f'"project_id" must be an integer project id, got {value!r}')

def fetch_all(project, resource, query=""):
    project_id = project_path_id(project)
    out, page = [], 1
    sep = "&" if query else ""
    while True:
        d = call("GET", f"/projects/{project_id}/{resource}?{query}{sep}page={page:d}")
        out += d.get("result", [])
        if not d.get("next_page"):
            return out
        page += 1
        if page > MAX_PAGES:
            raise TestmoAPIError(
                f"GET /projects/{project_id}/{resource} kept reporting next_page past {MAX_PAGES} "
                f"pages ({len(out)} records so far). Aborting rather than paging forever — check "
                f"the query above for an unencoded character that truncated it."
            )

# A tag name no case can carry. verify_tag_filter() asks /cases for it and expects nothing back.
_SENTINEL_TAG = "testmo-tools-probe-no-such-tag"
_TAG_FILTER_VERIFIED = set()

def verify_tag_filter(project):
    """Prove /cases actually applies `?tags=` before any tag filter is trusted.

    This API ignores query parameters it does not recognize — 0.6.1 found `?milestone=240` returning
    every run in the project. A tag-only spec has no other constraint, so were `?tags=` renamed or
    dropped, /cases would return all ~13.7k project-1 cases, every one would pass matches(), and
    --create would post a 13k-case run. Asking for a tag that cannot exist separates the two:
    an honored parameter yields zero cases, an ignored one yields the whole repository.
    """
    project = project_path_id(project)
    if project in _TAG_FILTER_VERIFIED:
        return
    probe = f"/projects/{project}/cases?tags={_SENTINEL_TAG}&page=1"
    try:
        result = call("GET", probe).get("result") or []
    except TestmoAPIError:
        # The API rejected the value outright, which still shows it parses `?tags=`.
        _TAG_FILTER_VERIFIED.add(project)
        return
    if result:
        raise TestmoAPIError(
            f"Refusing to trust filters.tags: GET {probe} returned {len(result)} case(s) for a tag "
            f"no case can carry, so /cases is not applying `?tags=`. A tag filter would therefore "
            f"select every case in project {project}. Confirm the current tag-filter parameter name "
            f"against the Testmo API before creating any tag-driven run."
        )
    _TAG_FILTER_VERIFIED.add(project)

def fetch_cases(project, filters):
    """Fetch repository cases, applying any tag filter server-side."""
    tags = filters.get("tags")
    if not tags:
        return fetch_all(project, "cases")
    verify_tag_filter(project)
    # Percent-encode each tag but keep the commas that separate them: Testmo tag names are free
    # text, and a raw space raises http.client.InvalidURL, a non-ASCII character raises
    # UnicodeEncodeError, `&` appends a parameter, and `#` truncates the URL at the fragment —
    # dropping `page=` so fetch_all would re-request page 1 forever.
    query = "tags=" + ",".join(urllib.parse.quote(str(t), safe="") for t in tags)
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

# Keys main() indexes directly. Checked when a spec is loaded, before any API call: a KeyError
# raised later — mid-way through the create loop — fires after earlier runs have already been
# POSTed, producing a half-populated milestone.
REQUIRED_SPEC_KEYS = ("project_id", "run_name")

class SpecError(Exception):
    """A spec file is missing, is not valid JSON, or lacks a required key."""

def load_spec(path):
    """Load and validate one spec file. Raises SpecError naming the file and the problem."""
    try:
        with open(path) as fh:
            spec = json.load(fh)
    except FileNotFoundError:
        raise SpecError(f"Spec file not found: {path}")
    except json.JSONDecodeError as e:
        raise SpecError(f"{path} is not valid JSON: {e}")
    if not isinstance(spec, dict):
        raise SpecError(f"{path} must contain a JSON object, got {type(spec).__name__}")
    absent = [k for k in REQUIRED_SPEC_KEYS if spec.get(k) is None]
    if absent:
        raise SpecError(f"{path} is missing {', '.join(repr(k) for k in absent)} "
                        f"(every spec needs {', '.join(REQUIRED_SPEC_KEYS)})")
    return spec

def existing_runs_for_milestone(project, milestone_id):
    """Find runs already linked to this milestone, for the duplicate-run guards.

    Returns (runs, checked). `checked` is False when the runs payload carries no milestone_id
    field at all: the guard then cannot tell "no duplicates" from "cannot see the link", and the
    caller must say so rather than report a clean result — a guardrail that quietly no-ops is
    worse than none.
    """
    # ?milestone_id= is honoured server-side (verified 2026-09-02: project 1 pages from 20 down to 4
    # for a busy milestone). The client-side filter below is kept regardless, because the API ignores
    # query parameters it does not recognize — were the name ever to change, that would silently return
    # every run in the project, and this guard must not widen into a false positive.
    runs = fetch_all(project, "runs", f"milestone_id={milestone_id:d}")
    if runs and not any("milestone_id" in r for r in runs):
        return [], False
    return [r for r in runs if r.get("milestone_id") == milestone_id], True

def same_run(existing, spec):
    """True when an existing run is (or cannot be told apart from) the run this spec creates.

    Multi-configuration runs share a run name by design, so the name alone is not enough: a run
    with a different config_id is a sibling, not a duplicate. When the run object exposes no
    config_id, the two cannot be told apart, so it counts — the guard errs toward refusing.
    """
    if existing.get("name") != spec["run_name"]:
        return False
    if spec.get("config_id") is None or "config_id" not in existing:
        return True
    return existing.get("config_id") == spec["config_id"]


def load_specs(paths):
    """Load every spec up front, so a bad file fails before any API call is made.

    Problems are collected rather than raised one at a time, so several bad specs are reported in a
    single pass. Each spec is labelled by its file name, since multi-configuration runs share a
    run_name by design and the name alone would not say which spec a row belongs to.
    """
    specs, invalid = [], []
    for path in paths:
        try:
            specs.append((Path(path).stem, load_spec(path)))
        except SpecError as e:
            invalid.append(str(e))
    if invalid:
        detail = "\n".join(f"  {line}" for line in invalid)
        sys.exit(f"{len(invalid)} spec(s) are invalid:\n{detail}")
    return specs

def resolve_project(specs):
    """Return the single project id every spec targets.

    The spec is the only source of truth for this — there is deliberately no --project override,
    since a flag that outranked each spec's project_id could create a spec into a project it was
    never written for. One invocation fetches one project's cases, so the specs must agree.
    """
    by_project = {}
    for name, spec in specs:
        by_project.setdefault(spec["project_id"], []).append(name)
    if len(by_project) > 1:
        lines = "\n".join(f"  {pid}: {', '.join(names)}" for pid, names in by_project.items())
        sys.exit(f"Specs disagree on project_id:\n{lines}\n"
                 f"Every spec in one invocation must target the same project.")
    try:
        # Request paths interpolate this, so it has to be an integer id and nothing else.
        return project_path_id(next(iter(by_project)))
    except TestmoAPIError as e:
        sys.exit(str(e))

def resolve_milestone(project, name):
    """Return the id of the one milestone with this exact name. The API cannot create milestones."""
    hits = [m for m in fetch_all(project, "milestones") if m.get("name") == name]
    if not hits:
        sys.exit(f"No milestone named {name!r} in project {project}. "
                 f"Create it in the Testmo UI first (the API cannot create milestones).")
    if len(hits) > 1:
        ids = ", ".join(str(m["id"]) for m in hits)
        sys.exit(f"{len(hits)} milestones named {name!r} (ids: {ids}). Rename or use a unique name.")
    return hits[0]["id"]

def needs_manual_step_2(spec):
    """True when this run cannot be finished by the API alone.

    A `config_id` marks a run that is one of several same-named variants distinguished only by
    Testmo Configuration. /cases cannot filter by configuration and exposes no per-case config
    assignment, so the script only ever reproduces step 1 — removing the other configurations'
    cases is a manual UI pass. Each spec's `_comment` spells out its own step 2, and `_comment` is
    never displayed, so the reminder has to come from here.
    """
    return spec.get("config_id") is not None

def print_step_2_reminder(labels, created):
    """Name every run that still needs its manual Testmo UI pass."""
    if not labels:
        return
    verb = "need" if created else "will need"
    print(f"\nMANUAL STEP 2 REQUIRED — {len(labels)} run(s) {verb} a Testmo UI pass:")
    for label in labels:
        print(f"  {label}")
    print("  These are multi-configuration runs: the API reproduced step 1 only. In the Testmo UI, "
          "remove\n  the cases belonging to the other configurations. Each spec's \"_comment\" gives "
          "its own step 2.\n  Until that pass is done these runs hold the wrong case set.")

def build_payload(spec, ids):
    payload = {"name": spec["run_name"], "state_id": spec.get("run_state_id", 7),
               "include_all": False, "cases": ids}
    for k in ("milestone_id", "config_id", "tags", "note"):
        if k in spec and spec[k] is not None:
            payload[k] = spec[k]
    return payload

def print_details(notes, cases, selected, payload):
    """Single-spec dry-run detail: folder resolution, a sample of the matched cases, the payload."""
    if notes:
        print("--- folder resolution ---")
        for n in notes:
            print(f"  {n}")
        print()
    print(f"{len(cases)} cases fetched -> {len(selected)} match filter")
    for c in selected[:10]:
        tt = ",".join(t["name"] for t in (c.get("custom_test_type") or [])) or "-"
        print(f'  id={c["id"]} folder={c.get("folder_id")} type={tt} '
              f'auto={c.get("custom_automation_type")} state={c.get("state_id")}')
    if len(selected) > 10:
        print(f"  ... +{len(selected) - 10} more")
    print("\n--- run payload (cases truncated) ---")
    print(json.dumps({**payload, "cases": f"[{len(payload['cases'])} ids]"}, indent=2))
    print()

# Why each non-ready status blocks --create, keyed by the status text before any " — " detail.
_BLOCKED_HINTS = {
    "NEEDS CONFIG_ID": "these runs are distinguished from their same-named siblings only by "
                       "Configuration — look the ids up via GET /projects/{project}/configs and set "
                       "them in the specs",
    "EMPTY": "0 cases is almost always a renamed tag or folder — check the spec's filters against "
             "the live repository",
    "DUPLICATE": "the run already exists in the milestone, or another spec in this batch creates the "
                 "same run — drop that spec, or pass --allow-existing if the duplicate is intended",
}

def main():
    ap = argparse.ArgumentParser(
        description="Create Testmo runs from JSON filter specs. Dry-run unless --create is passed.")
    ap.add_argument("--spec", action="append", required=True, metavar="PATH",
                    help="path to a JSON filter spec. Repeat to create several runs in one pass; the "
                         "folder tree and case list are fetched once for all of them.")
    milestone = ap.add_mutually_exclusive_group()
    milestone.add_argument("--milestone-id", type=int, default=None,
                           help="link every run to this existing milestone id (overrides the specs)")
    milestone.add_argument("--milestone-name", default=None,
                           help="link every run to the existing milestone with this exact name. "
                                "Milestones must be created in the Testmo UI first.")
    ap.add_argument("--create", action="store_true", help="actually POST the runs (omit for dry-run)")
    ap.add_argument("--allow-existing", action="store_true",
                    help="create runs even when a run with the same name (and config) is already "
                         "linked to the milestone. Without this, --create refuses.")
    args = ap.parse_args()

    specs = load_specs(args.spec)
    project = resolve_project(specs)
    override = args.milestone_id
    if args.milestone_name is not None:
        override = resolve_milestone(project, args.milestone_name)
    for name, spec in specs:
        if override is not None:
            spec["milestone_id"] = override
        mid = spec.get("milestone_id")
        # bool is a subclass of int, so `true` would otherwise pass as milestone 1.
        if mid is not None and (not isinstance(mid, int) or isinstance(mid, bool)):
            sys.exit(f'{name}: "milestone_id" must be an integer milestone id, got {mid!r}')

    print(f"Specs     : {len(specs)}")
    print(f"Project   : {project}  (from the specs)")
    if args.milestone_name is not None:
        print(f"Milestone : {args.milestone_name!r} -> id {override}")
    elif override is not None:
        print(f"Milestone : id {override}")
    print(f"Mode      : {'CREATE' if args.create else 'DRY RUN'}")

    # Idempotency is checked per spec, against the runs already linked to its milestone. It needs a
    # milestone to scope the lookup — run names like "Mobile" recur every cycle, so a project-wide
    # name match means nothing.
    linked = {}
    for mid in dict.fromkeys(s.get("milestone_id") for _, s in specs):
        if mid is None:
            print("Existing  : NOT CHECKED for specs with no milestone — pass --milestone-id or "
                  "--milestone-name to check for duplicates")
            continue
        runs, checked = existing_runs_for_milestone(project, mid)
        linked[mid] = (runs, checked)
        if not checked:
            print(f"Existing  : CANNOT CHECK milestone {mid} — the runs API returned no "
                  f"milestone_id field, so duplicates cannot be ruled out")
        else:
            print(f"Existing  : {len(runs)} run(s) already linked to milestone {mid}")
    print()

    # Fetch shared data once so N specs don't trigger N full downloads. Tag-driven specs each issue
    # their own server-side filtered fetch instead of using the full case list.
    all_filters = [s.get("filters") or {} for _, s in specs]
    folders = (fetch_all(project, "folders")
               if any(f.get("folder_paths") or f.get("folder_ids") for f in all_filters) else None)
    all_cases = fetch_all(project, "cases") if any(not f.get("tags") for f in all_filters) else None

    rows, results, batch = [], [], {}
    for i, (name, spec) in enumerate(specs):
        filters = spec.get("filters") or {}
        label = f"{spec['run_name']}  [{name}]"
        folder_ids, notes = resolve_folders(filters, project, folders=folders)
        bad = [n for n in notes if n.startswith(("UNMATCHED", "UNKNOWN"))]
        if bad:
            rows.append((label, "FOLDER ERROR", "; ".join(bad)))
            continue
        cases = fetch_cases(project, filters) if filters.get("tags") else all_cases
        selected = [c for c in cases if matches(c, filters, folder_ids)]
        ids = [c["id"] for c in selected]

        mid = spec.get("milestone_id")
        existing = [r for r in linked.get(mid, ([], None))[0] if same_run(r, spec)]
        # Index by position, not file name: the same spec passed twice is still a duplicate.
        twin = batch.setdefault((mid, spec["run_name"], spec.get("config_id")), i)
        # "config_id": null is an explicit placeholder — the run needs a Testmo Configuration that
        # has not been looked up yet, and creating it would produce indistinguishable runs.
        if "config_id" in spec and spec["config_id"] is None:
            status = "NEEDS CONFIG_ID"
        elif not ids:
            status = "EMPTY — 0 cases"
        elif existing and not args.allow_existing:
            status = f"DUPLICATE — run {', '.join(str(r.get('id')) for r in existing)} exists"
        elif twin != i and not args.allow_existing:
            status = f"DUPLICATE — same run as [{specs[twin][0]}]"
        else:
            status = "ready"
        rows.append((label, str(len(ids)), status))
        results.append((name, spec, ids))
        if len(specs) == 1:
            print_details(notes, cases, selected, build_payload(spec, ids))

    print(f"{'RUN NAME  [SPEC]':<60}{'CASES':>7}  STATUS")
    print("-" * 86)
    for label, count, status in rows:
        print(f"{label[:59]:<60}{count:>7}  {status}")
    ready = sum(1 for r in rows if r[2] == "ready")
    print("-" * 86)
    print(f"{'TOTAL':<60}{sum(len(ids) for _, _, ids in results):>7}  "
          f"{ready}/{len(specs)} runs ready")

    errors = [r for r in rows if r[1] == "FOLDER ERROR"]
    if errors:
        sys.exit(f"\n{len(errors)} spec(s) reference folders that did not resolve — fix them before "
                 f"continuing.")
    blocked = [r for r in rows if r[2] != "ready"]
    step_2 = [f"{spec['run_name']}  [{name}]" for name, spec, _ in results if needs_manual_step_2(spec)]

    if not args.create:
        print("\nDRY RUN — no runs created. Re-run with --create to POST the above.")
        print_step_2_reminder(step_2, created=False)
        if blocked:
            print(f"NOTE: {len(blocked)} run(s) are not ready (see STATUS above); --create would "
                  f"refuse until they are fixed or dropped.")
        return

    if blocked:
        # Refuse the whole batch rather than create the ready runs and skip the rest: a skipped run
        # leaves the milestone incomplete, and the dry-run is the place to have noticed.
        detail = "\n".join(f"  {label} — {status}" for label, _, status in blocked)
        kinds = dict.fromkeys(status.split(" — ")[0] for _, _, status in blocked)
        reasons = "\n".join(f"  {k}: {_BLOCKED_HINTS[k].format(project=project)}" for k in kinds)
        sys.exit(f"\nRefusing to create: {len(blocked)} run(s) are not ready:\n{detail}\n{reasons}")
    if any(checked is False for _, checked in linked.values()):
        print("WARNING: could not verify whether these runs already exist — the runs API returned no "
              "milestone_id field. Check the Testmo UI before continuing.")

    # Create every run we can rather than aborting on the first failure: stopping midway through a
    # batch leaves a half-populated milestone and no record of which runs made it.
    print()
    created, failed, step_2 = [], [], []
    for name, spec, ids in results:
        label = f"{spec['run_name']}  [{name}]"
        try:
            res = call("POST", f"/projects/{project}/runs", build_payload(spec, ids))
        except TestmoAPIError as e:
            reason = str(e).splitlines()[0]
            print(f"  FAILED: {label}\n           {reason}")
            failed.append((label, reason))
            continue
        rid = (res.get("result") or {}).get("id")
        if rid is None:
            print(f"  FAILED: {label}\n           POST succeeded but the response carried no run id")
            failed.append((label, "response carried no run id"))
            continue
        created.append(rid)
        if needs_manual_step_2(spec):
            step_2.append(f"{label}  -> https://bitwarden.testmo.net/run/{rid}")
        print(f"  CREATED run {rid}  ({len(ids)} cases)  {label}  https://bitwarden.testmo.net/run/{rid}")

    print(f"\n{len(created)} created, {len(failed)} failed — of {len(results)} run(s) attempted.")
    print_step_2_reminder(step_2, created=True)
    if failed:
        print("\nNOT created:")
        for label, reason in failed:
            print(f"  {label} — {reason}")
        sys.exit(f"\n{len(failed)} run(s) were not created. Fix the cause and re-run with only those "
                 f"specs — the {len(created)} run(s) above already exist.")

if __name__ == "__main__":
    try:
        main()
    except TestmoAPIError as e:
        sys.exit(str(e))
