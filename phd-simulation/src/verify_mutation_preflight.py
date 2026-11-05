"""Execute actual and synthetic negative-control tests for the preflight gate."""
import copy
import hashlib
import json
import platform
from datetime import datetime, timezone
from pathlib import Path

from preflight_mutation_pilot import actual_preflight, evaluate, load_manifest


ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "docs" / "mutation-preflight-manifest-v1.json"
SOURCE = ROOT / "src" / "preflight_mutation_pilot.py"
OUTPUT = ROOT / "results" / "2026-11-05-mutation-preflight.json"


def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    manifest = load_manifest(MANIFEST)
    actual = actual_preflight(manifest)
    exact_packages = dict(manifest["required_packages"])
    authorized = copy.deepcopy(manifest)
    authorized["execution_authorized"] = True

    controls = []

    def control(name, changed, expected_status):
        report = evaluate(changed, manifest["required_python"], exact_packages)
        controls.append({
            "name": name,
            "passed": report["status"] == expected_status,
            "observed_status": report["status"],
            "blockers": report["blockers"],
        })

    control("exact synthetic environment plus explicit authorization can reach baseline-only gate",
            authorized, "READY_FOR_BASELINE_ONLY")
    changed = copy.deepcopy(authorized)
    changed["required_packages"]["qiskit"] = "99.0"
    control("package-version mismatch blocks", changed,
            "BLOCKED_BEFORE_BASELINE_RESERVATION")
    changed = copy.deepcopy(authorized)
    changed["sources"][3]["git_blob_sha"] = "not-a-git-hash"
    control("malformed source identity blocks", changed,
            "BLOCKED_BEFORE_BASELINE_RESERVATION")
    changed = copy.deepcopy(authorized)
    changed["sources"].pop()
    control("missing scientific source blocks", changed,
            "BLOCKED_BEFORE_BASELINE_RESERVATION")
    changed = copy.deepcopy(authorized)
    changed["sources"].append({"path": "src/unapproved.py",
                               "git_blob_sha": "0" * 40})
    control("undeclared extra source blocks", changed,
            "BLOCKED_BEFORE_BASELINE_RESERVATION")
    changed = copy.deepcopy(authorized)
    changed["parent_commit"] = "main"
    control("mutable parent reference blocks", changed,
            "BLOCKED_BEFORE_BASELINE_RESERVATION")
    control("frozen authorization false blocks", manifest,
            "BLOCKED_BEFORE_BASELINE_RESERVATION")

    checks_passed = sum(row["passed"] for row in controls)
    output = {
        "schema_version": 1,
        "status": "PREFLIGHT_BLOCKED_AS_DESIGNED" if
                  actual["status"] == "BLOCKED_BEFORE_BASELINE_RESERVATION" and
                  checks_passed == len(controls) else "PREFLIGHT_TEST_FAILURE",
        "executed_at_utc": datetime.now(timezone.utc).isoformat(),
        "command": "python src/verify_mutation_preflight.py",
        "python": platform.python_version(),
        "provenance": {
            "parent_commit": manifest["parent_commit"],
            "manifest_sha256": sha256(MANIFEST),
            "preflight_source_sha256": sha256(SOURCE),
            "source_git_blob_identities": {
                row["path"]: row["git_blob_sha"] for row in manifest["sources"]
            },
        },
        "actual_environment_preflight": actual,
        "negative_controls": controls,
        "summary": {
            "negative_controls_passed": checks_passed,
            "negative_controls_total": len(controls),
            "baseline_reserved": False,
            "protocol_mutants_executed": 0,
            "formulation_passes_executed": 0,
            "sdk_statevectors_executed": 0,
            "search_evaluations": 0,
            "shots": 0,
            "hardware_jobs": 0,
        },
        "decision": "Do not create a pilot run directory. Keep execution_authorized false. Recreate the published lock or version an explicit replacement lock, then rerun preflight.",
        "limitations": [
            "Git blob identities were resolved from GitHub before execution; this local script validates the frozen manifest shape.",
            "Installed distributions are inspected through package metadata only; Qiskit and NumPy are not imported.",
            "A future READY result would authorize only the frozen baseline bundle, never M01-M12 automatically."
        ],
    }
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(json.dumps(output, indent=2, sort_keys=True) + "\n",
                      encoding="utf-8")
    print(json.dumps(output, indent=2, sort_keys=True))
    if output["status"] != "PREFLIGHT_BLOCKED_AS_DESIGNED":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
