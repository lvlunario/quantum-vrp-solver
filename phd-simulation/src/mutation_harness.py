"""Fail-closed orchestration contract for the bounded mutation pilot.

This module performs no quantum work.  It reserves append-only attempt records,
validates provenance, and refuses any action that would exceed protocol v1.
"""
import hashlib
import json
import os
from datetime import datetime, timezone
from pathlib import Path


CAPS = {
    "formulation_passes": 2,
    "sdk_statevectors": 15,
    "baseline_bundles": 1,
    "mutant_attempts": 12,
    "search_evaluations": 0,
    "shots": 0,
    "optimizer_calls": 0,
    "transpiler_runs": 0,
    "cloud_calls": 0,
    "hardware_jobs": 0,
}
REQUIRED_PROVENANCE = {
    "parent_commit", "source_sha256", "lock_sha256", "python", "command",
    "created_at_utc", "thresholds", "fixture",
}


def now():
    return datetime.now(timezone.utc).isoformat()


def create_json(path, value):
    with Path(path).open("x", encoding="utf-8", newline="\n") as stream:
        json.dump(value, stream, indent=2, allow_nan=False, sort_keys=True)
        stream.write("\n")
        stream.flush()
        os.fsync(stream.fileno())


class ProtocolViolation(RuntimeError):
    pass


class PilotHarness:
    """Append-only pilot ledger whose budgets are reconstructed from attempts."""

    def __init__(self, directory, provenance):
        missing = sorted(REQUIRED_PROVENANCE - set(provenance))
        if missing:
            raise ProtocolViolation(f"missing provenance: {', '.join(missing)}")
        self.directory = Path(directory)
        self.directory.mkdir(parents=True, exist_ok=False)
        self.events = self.directory / "events"
        self.records = self.directory / "records"
        self.events.mkdir()
        self.records.mkdir()
        create_json(self.directory / "manifest.json", {
            "schema_version": 1,
            "status": "STARTED",
            "protocol": "mutation-pilot-protocol-v1",
            "caps": CAPS,
            "provenance": provenance,
        })

    def _event_rows(self):
        return [json.loads(p.read_text(encoding="utf-8"))
                for p in sorted(self.events.glob("[0-9]*.json"))]

    def counts(self):
        totals = {name: 0 for name in CAPS}
        for row in self._event_rows():
            if row["kind"] == "attempt":
                for name, amount in row["consumption"].items():
                    totals[name] += amount
        return totals

    def _append(self, row):
        sequence = len(self._event_rows())
        create_json(self.events / f"{sequence:06d}.json",
                    {"at_utc": now(), **row})

    def _baseline_ok(self):
        terminal = self.records / "baseline" / "terminal.json"
        return terminal.exists() and json.loads(
            terminal.read_text(encoding="utf-8")).get("baseline_passed") is True

    def execute(self, record_id, kind, consumption, callback):
        if kind not in {"baseline", "mutant"}:
            raise ProtocolViolation(f"unsupported record kind: {kind}")
        if kind == "baseline" and record_id != "baseline":
            raise ProtocolViolation("baseline record id must be 'baseline'")
        if kind == "mutant" and (record_id not in {f"M{i:02d}" for i in range(1, 13)}):
            raise ProtocolViolation(f"unknown mutant id: {record_id}")
        if kind == "mutant" and not self._baseline_ok():
            raise ProtocolViolation("baseline has not passed")
        if any(name not in CAPS or not isinstance(amount, int) or amount < 0
               for name, amount in consumption.items()):
            raise ProtocolViolation("invalid budget consumption")
        proposed = self.counts()
        for name, amount in consumption.items():
            proposed[name] += amount
            if proposed[name] > CAPS[name]:
                raise ProtocolViolation(
                    f"budget exceeded for {name}: {proposed[name]} > {CAPS[name]}")

        record = self.records / record_id
        record.mkdir()  # Atomic reservation; duplicate IDs are refused.
        self._append({"kind": "attempt", "record_id": record_id,
                      "record_kind": kind, "consumption": consumption})
        try:
            result = callback()
            if not isinstance(result, dict):
                raise ProtocolViolation("callback result must be an object")
            if kind == "baseline" and result.get("baseline_passed") is not True:
                raise ProtocolViolation("baseline did not pass")
            create_json(record / "result.json", result)
            digest = hashlib.sha256((record / "result.json").read_bytes()).hexdigest()
            create_json(record / "terminal.json", {
                "status": "COMPLETE", "result_sha256": digest,
                "baseline_passed": result.get("baseline_passed"),
            })
            self._append({"kind": "complete", "record_id": record_id,
                          "result_sha256": digest})
            return result
        except BaseException as exc:
            create_json(record / "aborted.json", {
                "status": "ABORTED", "exception_type": type(exc).__name__,
                "message": str(exc), "at_utc": now(),
            })
            self._append({"kind": "aborted", "record_id": record_id,
                          "exception_type": type(exc).__name__})
            raise

