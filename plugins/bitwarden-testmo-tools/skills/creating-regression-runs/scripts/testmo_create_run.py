#!/usr/bin/env python3
"""Create a Testmo run from a reviewable JSON filter spec.

Reproduces the manual "filter cases -> create run" workflow via the API so it is repeatable.
Read-only unless --create is passed. Never prints the API key.

Filter model (all keys under "filters" are optional; a case must match every key present):
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
import argparse, json, os, subprocess, sys

BASE = "https://bitwarden.testmo.net/api/v1"
KEY = os.environ.get("TESTMO_API_KEY")

def call(method, path, body=None):
    if not KEY:
        sys.exit("TESTMO_API_KEY not set")
    cmd = ["curl", "-sS", "-m", "60", "-X", method, BASE + path,
           "-H", f"Authorization: Bearer {KEY}",
           "-H", "Accept: application/json"]
    if body is not None:
        cmd += ["-H", "Content-Type: application/json", "--data-binary", "@-"]
    out = subprocess.run(cmd, input=json.dumps(body) if body is not None else None,
                         capture_output=True, text=True)
    if out.returncode != 0:
        sys.exit(f"curl failed: {out.stderr.strip()}")
    return json.loads(out.stdout)

def fetch_all(project, resource):
    out, page = [], 1
    while True:
        d = call("GET", f"/projects/{project}/{resource}?page={page}")
        out += d.get("result", [])
        if not d.get("next_page"):
            return out
        page += 1

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

def resolve_folders(spec_filters, project):
    """Return (folder_id_set, notes). Empty set means 'no folder filter'."""
    want_paths = spec_filters.get("folder_paths") or []
    want_ids = spec_filters.get("folder_ids") or []
    if not want_paths and not want_ids:
        return None, []
    include_sub = spec_filters.get("include_subfolders", True)
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
    if "automation_type_ids" in spec and case.get("custom_automation_type") not in spec["automation_type_ids"]:
        return False
    if spec.get("exclude_automation_type_ids") and case.get("custom_automation_type") in spec["exclude_automation_type_ids"]:
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
    args = ap.parse_args()
    spec = json.load(open(args.spec))

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

    cases = fetch_all(project, "cases")
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
        if k in spec:
            payload[k] = spec[k]

    print("\n--- run payload (cases truncated) ---")
    print(json.dumps({**payload, "cases": f"[{len(ids)} ids]"}, indent=2))

    if not args.create:
        print("\nDRY RUN — no run created. Re-run with --create to POST.")
        return
    if not ids:
        sys.exit("Refusing to create a run with 0 cases.")
    res = call("POST", f"/projects/{project}/runs", payload)
    rid = res.get("result", {}).get("id")
    print(f"\nCREATED run id={rid}  https://bitwarden.testmo.net/run/{rid}")

if __name__ == "__main__":
    main()
