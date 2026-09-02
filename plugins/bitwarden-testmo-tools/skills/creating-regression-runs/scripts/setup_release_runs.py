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
  python3 setup_release_runs.py --release partial --milestone-name "2026.8.1 Manual Regression" \
      --exclude directory-connector-regression --create
"""
import argparse, json, re, sys
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

def load_specs(spec_names):
    """Load every spec up front, so a packaging error fails before any API call is made."""
    specs, missing = [], []
    for name in spec_names:
        path = SPECS_DIR / f"{name}.json"
        if not path.exists():
            missing.append(name)
            continue
        try:
            specs.append((name, json.loads(path.read_text())))
        except json.JSONDecodeError as e:
            sys.exit(f"{path.name} is not valid JSON: {e}")
    if missing:
        sys.exit(f"Profile references {len(missing)} spec(s) with no file in {SPECS_DIR}: "
                 f"{', '.join(missing)}")
    return specs


def resolve_project(specs):
    """Return the single project id every spec targets.

    The spec is the only source of truth for this — there is deliberately no --project override.
    A flag that silently outranked each spec's project_id meant one spec could be created into a
    project it was never written for, and the two entrypoints would disagree about the same file
    (testmo_create_run.py has always treated spec["project_id"] as authoritative).
    """
    missing = [name for name, spec in specs if spec.get("project_id") is None]
    if missing:
        sys.exit(f"{len(missing)} spec(s) have no \"project_id\": {', '.join(missing)}")
    by_project = {}
    for name, spec in specs:
        by_project.setdefault(spec["project_id"], []).append(name)
    if len(by_project) > 1:
        lines = "\n".join(f"  {pid}: {', '.join(names)}" for pid, names in sorted(by_project.items()))
        sys.exit(f"Specs in this profile disagree on project_id:\n{lines}\n"
                 f"Every spec in a release profile must target the same project.")
    return next(iter(by_project))


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
    ap.add_argument("--exclude", action="append", default=[], metavar="SPEC",
                    help="spec to skip this release, by spec name (file name in specs/ without .json). "
                         "Repeatable, or comma-separated. Must name a spec in the profile — a name that "
                         "is not in it is an error, so a typo cannot silently create the run anyway.")
    ap.add_argument("--create", action="store_true", help="actually POST the runs (omit for dry-run)")
    args = ap.parse_args()

    profile_specs = load_profile(args.release)
    excluded = [n.strip() for item in args.exclude for n in item.split(",") if n.strip()]
    unknown = [n for n in excluded if n not in profile_specs]
    if unknown:
        sys.exit(f"--exclude name(s) not in the {args.release!r} profile: {', '.join(unknown)}\n"
                 f"Profile specs: {', '.join(profile_specs)}")
    spec_names = [n for n in profile_specs if n not in excluded]
    if not spec_names:
        sys.exit(f"Every spec in the {args.release!r} profile is excluded — nothing to do.")

    specs = load_specs(spec_names)
    project = resolve_project(specs)
    milestone_id = resolve_milestone(project, args.milestone_name)
    period = args.period or derive_period(args.milestone_name)

    print(f"Release profile : {args.release}  ({len(spec_names)} runs)")
    if excluded:
        print(f"Excluded        : {', '.join(dict.fromkeys(excluded))}")
    print(f"Milestone       : {args.milestone_name!r} -> id {milestone_id}")
    print(f"Period          : {period or '(none — <period> left as-is)'}")
    print(f"Project         : {project}  (from the specs)")
    print(f"Mode            : {'CREATE' if args.create else 'DRY RUN'}")
    print()

    # Fetch shared data once so N specs don't trigger N full downloads.
    folders = core.fetch_all(project, "folders")
    all_cases = core.fetch_all(project, "cases")

    rows, results = [], []
    for name, spec in specs:
        spec["milestone_id"] = milestone_id
        if period:
            spec["run_name"] = spec.get("run_name", name).replace("<period>", period)
        filters = spec.get("filters", {})

        cases = core.fetch_cases(project, filters) if filters.get("tags") else all_cases
        folder_ids, notes = core.resolve_folders(filters, project, folders=folders)
        bad = [n for n in notes if n.startswith(("UNMATCHED", "UNKNOWN"))]
        if bad:
            rows.append((spec.get("run_name", name), "FOLDER ERROR", "; ".join(bad)))
            continue
        selected = [c for c in cases if core.matches(c, filters, folder_ids)]
        ids = [c["id"] for c in selected]
        # "config_id": null is an explicit placeholder — the run needs a Testmo Configuration that
        # has not been looked up yet. Surface it in the dry-run summary; block --create below.
        if "config_id" in spec and spec["config_id"] is None:
            rows.append((spec.get("run_name", name), str(len(ids)), "NEEDS CONFIG_ID"))
        else:
            rows.append((spec.get("run_name", name), str(len(ids)), "ready"))
        results.append((name, spec, ids))

    print(f"{'RUN NAME':<60}{'CASES':>7}  STATUS")
    print("-" * 86)
    for nm, cnt, status in rows:
        print(f"{nm[:59]:<60}{cnt:>7}  {status}")
    total = sum(len(ids) for _, _, ids in results)
    print("-" * 86)
    print(f"{'TOTAL':<60}{total:>7}  {len(results)}/{len(spec_names)} runs ready")

    errors = [r for r in rows if r[1] == "FOLDER ERROR"]
    if errors:
        sys.exit(f"\n{len(errors)} spec(s) have problems — fix before creating.")

    if not args.create:
        print("\nDRY RUN — no runs created. Re-run with --create to POST all of the above.")
        return

    needs_config = [r[0] for r in rows if r[2] == "NEEDS CONFIG_ID"]
    if needs_config:
        sys.exit(
            f"\nRefusing to create: {len(needs_config)} spec(s) have \"config_id\": null — "
            f"{', '.join(sorted(set(needs_config)))}.\nThese runs are distinguished from their "
            f"same-named siblings only by Configuration, so creating them without one would produce "
            f"indistinguishable runs.\nLook the ids up via GET /projects/"
            f"{project}/configs and set them in the specs."
        )

    # Create every run we can rather than aborting on the first failure: stopping midway through a
    # 14-run release leaves a half-populated milestone and no record of which runs made it. Each
    # failure is recorded and reported in the closing tally instead.
    print()
    created, skipped, failed = [], [], []
    for spec_name, spec, ids in results:
        name = spec["run_name"]
        # Multi-config runs share a run_name by design, so identify rows by spec file as well —
        # otherwise a tally of three "Extension" failures says nothing about which ones.
        label = f"{name}  [{spec_name}]"
        if not ids:
            print(f"  SKIP (0 cases): {label}")
            skipped.append(label)
            continue
        payload = {"name": name, "state_id": spec.get("run_state_id", 7),
                   "include_all": False, "cases": ids, "milestone_id": milestone_id}
        for k in ("config_id", "tags", "note"):
            if k in spec and spec[k] is not None:
                payload[k] = spec[k]
        try:
            res = core.call("POST", f"/projects/{project}/runs", payload)
        except core.TestmoAPIError as e:
            reason = str(e).splitlines()[0]
            print(f"  FAILED: {label}\n           {reason}")
            failed.append((label, reason))
            continue
        rid = (res.get("result") or {}).get("id")
        if rid is None:
            print(f"  FAILED: {label}\n           POST succeeded but the response carried no run id")
            failed.append((label, "response carried no run id"))
            continue
        created.append((rid, label))
        print(f"  CREATED run {rid}  ({len(ids)} cases)  {label}")

    print(f"\n{len(created)} created, {len(skipped)} skipped (0 cases), {len(failed)} failed "
          f"— of {len(results)} run(s) attempted.")
    if failed:
        print("\nNOT created:")
        for name, reason in failed:
            print(f"  {name} — {reason}")
        sys.exit(
            f"\n{len(failed)} run(s) were not created, so milestone {milestone_id} "
            f"({args.milestone_name}) is only partially populated. Fix the cause and re-run — the "
            f"{len(created)} run(s) above already exist, so exclude them or delete them first."
        )
    print(f"Done. All {len(created)} run(s) linked to milestone {milestone_id} ({args.milestone_name}).")

if __name__ == "__main__":
    try:
        main()
    except core.TestmoAPIError as e:
        # Reached only for the read phase (milestone/folder/case fetches); per-run write failures
        # are caught in the create loop so the tally still prints.
        sys.exit(str(e))
