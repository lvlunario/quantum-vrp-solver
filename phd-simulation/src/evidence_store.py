"""Fail-closed, local append-only run evidence. No quantum dependencies."""
import hashlib
import json
import os
from datetime import datetime, timezone
from pathlib import Path


def now():
    return datetime.now(timezone.utc).isoformat()


def create_json(path, value):
    # x refuses collisions; fsync flushes file data, not a power-loss guarantee.
    with Path(path).open('x', encoding='utf-8', newline='\n') as stream:
        json.dump(value, stream, indent=2, allow_nan=False)
        stream.write('\n')
        stream.flush()
        os.fsync(stream.fileno())


class RunStore:
    def __init__(self, output, metadata):
        self.output = Path(output).absolute()
        self.directory = self.output.with_name(self.output.name + '.run')
        if self.output.exists() or self.output.is_symlink():
            raise FileExistsError(self.output)
        self.output.parent.mkdir(parents=True, exist_ok=True)
        self.directory.mkdir()  # Atomic reservation; never reuse or delete it.
        if self.output.exists() or self.output.is_symlink():
            raise FileExistsError(self.output)
        self.sequence = 0
        create_json(self.directory/'manifest.json', dict(
            schema_version=1, started_at_utc=now(), output=str(self.output),
            metadata=metadata, status='STARTED'))

    def event(self, kind, **payload):
        create_json(self.directory/f'{self.sequence:06d}.json',
                    dict(kind=kind, at_utc=now(), payload=payload))
        self.sequence += 1

    def finish(self, result):
        create_json(self.output, result)  # Also refuses a late external collision.
        create_json(self.directory/'terminal.json', dict(
            status=result.get('status', 'UNKNOWN'), finished_at_utc=now(),
            output_sha256=hashlib.sha256(self.output.read_bytes()).hexdigest(),
            counts=result.get('counts', {})))


def execute(output, callback, metadata):
    store = RunStore(output, metadata)  # Refusal must precede callback/import/work.
    try:
        result = callback(store.event)
        result['execution'] = metadata
        store.finish(result)
        return result
    except BaseException as exc:
        # An interrupted reservation remains visible and cannot be reused.
        store.event('aborted', exception_type=type(exc).__name__, message=str(exc))
        raise


def inventory(parent):
    """Count persisted attempts, not inferred successes. Does not invent old runs."""
    rows = []
    for directory in sorted(Path(parent).glob('*.run')):
        kinds = [json.loads(p.read_text())['kind'] for p in sorted(directory.glob('[0-9]*.json'))]
        terminal = directory/'terminal.json'
        rows.append(dict(run=directory.name, search_attempted=kinds.count('candidate_attempt'),
                         search_completed=kinds.count('candidate_complete'),
                         winner_oracle_validations=kinds.count('winner_validation_attempt'),
                         terminal_present=terminal.exists()))
    return dict(runs=rows, totals={k:sum(r[k] for r in rows) for k in
                ('search_attempted', 'search_completed', 'winner_oracle_validations')})
