#!/usr/bin/env python3
"""Set up all regression runs for a release, linked to a milestone.

Given a release profile (partial/full) and the NAME of a milestone you have
already created in the Testmo UI, this resolves the milestone to its id, then
runs every spec in the profile linked to it. Dry-run by default; --create writes.

Milestones cannot be created via the Testmo API — create the period's milestone
in the UI first (e.g. "2026.8.0 Manual Regression"), then pass its name here.

Example:
  python3 setup_release_runs.py --release full --milestone-name "2026.8.0 Manual Regression"
  python3 setup_release_runs.py --release full --milestone-name "2026.8.0 Manual Regression" --create
"""
import argparse, json, os, re, sys
from pathlib import Path

import testmo_create_run as core  # reuse fetch/resolve/match/create logic

SKILL_DIR = Path(__file__).resolve().parent.parent
SPECS_DIR = SKILL_DIR / "specs"
PROFILES = SKILL_DIR / "release-profiles.json"

def load_profile(name):
    data = json.loads(PROFILES.read_text())
    profiles = data["profiles"]
    if name not in profiles:
        sys.exit(f"Unknown release profile {name!r}. Available: {', '.join(profiles)}")
    seen, order = set(), []
    def collect(pname):
        p = profiles[pname]
        parent = p.get("extends")
        if parent:
            collect(parent)
        for s in p.get("specs", []):
            if s not in seen:
                seen.add(s)
                order.append(s)
    collect(name)
    return order

def resolve_milestone(project, name):
    milestones = core.fetch_all(project, "milestones")
    hits = [m for m in milestones if m.get("name") == name]
    if not hits:
        sys.exit(f"No milestone named {name!r} in project {project}. "
                 f"Create it in the Testmo UI first (the API cannot create milestones).")
    if len(hits) > 1:
        ids = ", ".join(str(m["id"]) for m in hits)
        sys.exit(f"{len(hits)} milestones named {name!r} (ids: {ids}). Rename or use a unique name.")
    return hits[0]["id"]

def derive_period(milestone_name):
    m = re.search(r"\d{4}\.\d+(?:\.\d+)?", milestone_name)
    return m.group(0) if m else None

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--release", required=True, help="release profile name (e.g. partial, full)")
    ap.add_argument("--milestone-name", required=True,
                    help="name of an EXISTING milestone (create it in the Testmo UI first)")
    ap.add_argument("--period", default=None,
                    help="value for the <period> placeholder in run names; defaults to the version parsed "
                         "from the milestone name")
    ap.add_argument("--project", type=int, default=1, help="Testmo project id (default 1 = Bitwarden)")
    ap.add_argument("--create", action="store_true", help="actually POST the runs (omit for dry-run)")
    args = ap.parse_args()

    spec_names = load_profile(args.release)
    milestone_id = resolve_milestone(args.project, args.milestone_name)
    period = args.period or derive_period(args.milestone_name)

    print(f"Release profile : {args.release}  ({len(spec_names)} runs)")
    print(f"Milestone       : {args.milestone_name!r} -> id {milestone_id}")
    print(f"Period          : {period or '(none — <period> left as-is)'}")
    print(f"Project         : {args.project}")
    print(f"Mode            : {'CREATE' if args.create else 'DRY RUN'}")
    print()

    # Fetch shared data once so N specs don't trigger N full downloads.
    folders = core.fetch_all(args.project, "folders")
    all_cases = core.fetch_all(args.project, "cases")

    rows, results = [], []
    for name in spec_names:
        path = SPECS_DIR / f"{name}.json"
        if not path.exists():
            rows.append((name, "MISSING SPEC", "-"))
            continue
        spec = json.loads(path.read_text())
        spec["milestone_id"] = milestone_id
        if period:
            spec["run_name"] = spec.get("run_name", name).replace("<period>", period)
        filters = spec.get("filters", {})

        cases = core.fetch_cases(args.project, filters) if filters.get("tags") else all_cases
        folder_ids, notes = core.resolve_folders(filters, args.project, folders=folders)
        bad = [n for n in notes if n.startswith(("UNMATCHED", "UNKNOWN"))]
        if bad:
            rows.append((spec.get("run_name", name), "FOLDER ERROR", "; ".join(bad)))
            continue
        selected = [c for c in cases if core.matches(c, filters, folder_ids)]
        ids = [c["id"] for c in selected]
        rows.append((spec.get("run_name", name), str(len(ids)), "ready"))
        results.append((spec, ids))

    print(f"{'RUN NAME':<60}{'CASES':>7}  STATUS")
    print("-" * 86)
    for nm, cnt, status in rows:
        print(f"{nm[:59]:<60}{cnt:>7}  {status}")
    total = sum(len(ids) for _, ids in results)
    print("-" * 86)
    print(f"{'TOTAL':<60}{total:>7}  {len(results)}/{len(spec_names)} runs ready")

    errors = [r for r in rows if r[1] in ("MISSING SPEC", "FOLDER ERROR")]
    if errors:
        sys.exit(f"\n{len(errors)} spec(s) have problems — fix before creating.")

    if not args.create:
        print("\nDRY RUN — no runs created. Re-run with --create to POST all of the above.")
        return

    print()
    for spec, ids in results:
        if not ids:
            print(f"  SKIP (0 cases): {spec['run_name']}")
            continue
        payload = {"name": spec["run_name"], "state_id": spec.get("run_state_id", 7),
                   "include_all": False, "cases": ids, "milestone_id": milestone_id}
        for k in ("config_id", "tags", "note"):
            if k in spec:
                payload[k] = spec[k]
        res = core.call("POST", f"/projects/{args.project}/runs", payload)
        rid = res.get("result", {}).get("id")
        print(f"  CREATED run {rid}  ({len(ids)} cases)  {spec['run_name']}")
    print(f"\nDone. All runs linked to milestone {milestone_id} ({args.milestone_name}).")

if __name__ == "__main__":
    main()
