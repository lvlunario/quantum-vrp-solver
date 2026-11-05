"""Fail-closed environment and source-manifest gate for the mutation pilot.

The module imports no Qiskit/NumPy scientific APIs and reserves no pilot run.
Installed versions are read as metadata only.
"""
import importlib.metadata
import json
import platform
import re
from datetime import datetime, timezone
from pathlib import Path


EXPECTED_SOURCE_PATHS = {
    "requirements-sdk.txt",
    "docs/mutation-pilot-plan-v1.json",
    "docs/mutation-pilot-protocol-v1.md",
    "src/mutation_harness.py",
    "src/scientific_adapters.py",
    "src/verify_formulation.py",
    "src/verify_qiskit_mixer.py",
    "src/verify_readout.py",
}
HEX40 = re.compile(r"^[0-9a-f]{40}$")


def installed_versions(names):
    versions = {}
    for name in names:
        try:
            versions[name] = importlib.metadata.version(name)
        except importlib.metadata.PackageNotFoundError:
            versions[name] = None
    return versions


def evaluate(manifest, python_version, packages):
    """Return a gate report without executing or importing scientific code."""
    checks = []

    def check(name, passed, detail):
        checks.append({"name": name, "passed": bool(passed), "detail": detail})

    check("schema and frozen-input status",
          manifest.get("schema_version") == 1 and
          manifest.get("status") == "FROZEN_PREFLIGHT_INPUT",
          {"schema_version": manifest.get("schema_version"),
           "status": manifest.get("status")})
    parent = manifest.get("parent_commit")
    check("parent commit is an immutable Git identity",
          isinstance(parent, str) and HEX40.fullmatch(parent) is not None,
          {"parent_commit": parent})

    sources = manifest.get("sources", [])
    paths = [row.get("path") for row in sources if isinstance(row, dict)]
    check("source inventory is exact and unique",
          set(paths) == EXPECTED_SOURCE_PATHS and len(paths) == len(set(paths)) ==
          len(EXPECTED_SOURCE_PATHS),
          {"paths": paths})
    invalid_hashes = [row.get("path") for row in sources
                      if not isinstance(row.get("git_blob_sha"), str) or
                      HEX40.fullmatch(row["git_blob_sha"]) is None]
    check("every source has a valid content-addressed Git blob identity",
          not invalid_hashes, {"invalid_paths": invalid_hashes})

    required_python = manifest.get("required_python")
    check("Python version exactly matches lock", python_version == required_python,
          {"required": required_python, "observed": python_version})
    required_packages = manifest.get("required_packages", {})
    mismatches = {
        name: {"required": version, "observed": packages.get(name)}
        for name, version in required_packages.items()
        if packages.get(name) != version
    }
    check("installed package metadata exactly matches lock", not mismatches,
          {"mismatches": mismatches})
    check("scientific execution is explicitly authorized",
          manifest.get("execution_authorized") is True,
          {"execution_authorized": manifest.get("execution_authorized")})

    ready = all(row["passed"] for row in checks)
    return {
        "status": "READY_FOR_BASELINE_ONLY" if ready else
                  "BLOCKED_BEFORE_BASELINE_RESERVATION",
        "checked_at_utc": datetime.now(timezone.utc).isoformat(),
        "checks": checks,
        "blockers": [row["name"] for row in checks if not row["passed"]],
        "baseline_reserved": False,
        "protocol_mutants_executed": 0,
        "formulation_passes_executed": 0,
        "sdk_statevectors_executed": 0,
        "search_evaluations": 0,
        "shots": 0,
        "hardware_jobs": 0,
    }


def actual_preflight(manifest):
    required = manifest.get("required_packages", {})
    return evaluate(manifest, platform.python_version(),
                    installed_versions(required))


def load_manifest(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))
