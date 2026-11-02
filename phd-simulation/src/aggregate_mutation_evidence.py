"""Rebuild mutation-pilot bookkeeping from retained files only.

This module does not import Qiskit or run scientific callbacks. It verifies
record identity, attempt-ledger totals, terminal digests and file completeness.
"""
import hashlib
import json
from pathlib import Path

from mutation_harness import CAPS


def read_json(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def aggregate(root, plan):
    root = Path(root)
    issues = []
    expected = [row["id"] for row in plan["records"]]
    expected_set = set(expected)

    manifest_path = root / "manifest.json"
    if not manifest_path.exists():
        issues.append("missing manifest.json")
        manifest = {}
    else:
        try: manifest = read_json(manifest_path)
        except Exception as exc:
            issues.append(f"invalid manifest.json: {type(exc).__name__}")
            manifest = {}
    if manifest.get("mode") != "SYNTHETIC_DRY_RUN":
        issues.append("fixture mode is not SYNTHETIC_DRY_RUN")

    event_paths = sorted((root / "events").glob("[0-9]*.json"))
    expected_names = [f"{i:06d}.json" for i in range(len(event_paths))]
    if [p.name for p in event_paths] != expected_names:
        issues.append("event sequence is not contiguous from zero")
    events = []
    for path in event_paths:
        try: events.append(read_json(path))
        except Exception as exc: issues.append(f"invalid event {path.name}: {type(exc).__name__}")

    attempts = [row for row in events if row.get("kind") == "attempt"]
    completes = [row for row in events if row.get("kind") == "complete"]
    attempt_ids = [row.get("record_id") for row in attempts]
    complete_ids = [row.get("record_id") for row in completes]
    if attempt_ids != expected: issues.append("attempt identities/order do not match plan")
    if complete_ids != expected: issues.append("complete identities/order do not match plan")
    if len(attempt_ids) != len(set(attempt_ids)): issues.append("duplicate attempt identity")

    totals = {name: 0 for name in CAPS}
    for row in attempts:
        consumption = row.get("consumption", {})
        for name, amount in consumption.items():
            if name not in CAPS or not isinstance(amount, int) or amount < 0:
                issues.append(f"invalid consumption for {row.get('record_id')}: {name}")
            else: totals[name] += amount
    if totals != plan.get("declared_totals"): issues.append("ledger totals do not equal declared plan totals")
    if totals != CAPS: issues.append("ledger totals do not equal protocol caps")

    records_root = root / "records"
    actual_dirs = sorted(p.name for p in records_root.iterdir() if p.is_dir()) if records_root.exists() else []
    if set(actual_dirs) != expected_set:
        issues.append("retained record directories do not exactly match plan")

    records = []
    for record_id in expected:
        directory = records_root / record_id
        result_path = directory / "result.json"
        terminal_path = directory / "terminal.json"
        row = {"record_id": record_id, "result_present": result_path.exists(),
               "terminal_present": terminal_path.exists()}
        if not result_path.exists(): issues.append(f"{record_id}: missing result.json")
        if not terminal_path.exists(): issues.append(f"{record_id}: missing terminal.json")
        if result_path.exists():
            try:
                result = read_json(result_path)
                row["result_status"] = result.get("status")
                if result.get("record_id") != record_id:
                    issues.append(f"{record_id}: result identity mismatch")
            except Exception as exc: issues.append(f"{record_id}: invalid result.json: {type(exc).__name__}")
        if terminal_path.exists():
            try:
                terminal = read_json(terminal_path)
                row["terminal_status"] = terminal.get("status")
                if terminal.get("status") != "COMPLETE": issues.append(f"{record_id}: terminal not COMPLETE")
                if result_path.exists() and terminal.get("result_sha256") != digest(result_path):
                    issues.append(f"{record_id}: result digest mismatch")
            except Exception as exc: issues.append(f"{record_id}: invalid terminal.json: {type(exc).__name__}")
        records.append(row)

    return {
        "status": "VALID" if not issues else "INVALID",
        "mode": manifest.get("mode"),
        "issues": issues,
        "computed_totals": totals,
        "record_count": len(records),
        "records": records,
    }

