"""Bounded standard-library workflow tests; no SDK or parameter search."""
import concurrent.futures
import hashlib
import json
import platform
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from evidence_store import RunStore, create_json, execute, inventory, now


class RetentionTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.output = self.root/'synthetic.json'
        self.calls = 0

    def callback(self, event):
        self.calls += 1
        event('candidate_attempt', ordinal=0)
        event('candidate_complete', row=dict(ordinal=0, probabilities=[0.25, 0.75]))
        event('winner_validation_attempt', ordinal=0)
        return dict(status='SYNTHETIC_TEST_ONLY', counts=dict(search_attempted=1))

    def launch(self, output=None):
        return execute(output or self.output, self.callback, {'fixture':'synthetic callback, not a circuit'})

    def test_existing_bytes_preserved_before_callback(self):
        self.output.write_bytes(b'old evidence\x00')
        with self.assertRaises(FileExistsError): self.launch()
        self.assertEqual(self.calls, 0)
        self.assertEqual(self.output.read_bytes(), b'old evidence\x00')

    def test_existing_reservation_refused(self):
        RunStore(self.output, {})
        with self.assertRaises(FileExistsError): self.launch()
        self.assertEqual(self.calls, 0)

    def test_success_digest(self):
        self.launch()
        terminal = json.loads((self.root/'synthetic.json.run/terminal.json').read_text())
        self.assertEqual(terminal['output_sha256'], hashlib.sha256(self.output.read_bytes()).hexdigest())

    def test_candidate_raw_payload_retained(self):
        self.launch()
        row = json.loads((self.root/'synthetic.json.run/000001.json').read_text())
        self.assertEqual(row['payload']['row']['probabilities'], [0.25,0.75])

    def test_exception_retains_attempt(self):
        def fail(event):
            event('candidate_attempt', ordinal=0)
            raise RuntimeError('injected failure')
        with self.assertRaises(RuntimeError): execute(self.output, fail, {})
        counts = inventory(self.root)
        self.assertEqual(counts['totals']['search_attempted'], 1)
        self.assertEqual(counts['totals']['search_completed'], 0)
        self.assertFalse(counts['runs'][0]['terminal_present'])

    def test_interruption_cannot_reuse(self):
        def fail(event): raise KeyboardInterrupt('injected interrupt')
        with self.assertRaises(KeyboardInterrupt): execute(self.output, fail, {})
        with self.assertRaises(FileExistsError): self.launch()
        self.assertEqual(self.calls, 0)

    def test_late_output_collision_preserves_external_bytes(self):
        def late(event):
            self.output.write_bytes(b'concurrent external evidence')
            return {'status':'TEST'}
        with self.assertRaises(FileExistsError): execute(self.output, late, {})
        self.assertEqual(self.output.read_bytes(), b'concurrent external evidence')

    def test_event_collision_refused(self):
        store = RunStore(self.output, {})
        store.event('first')
        store.sequence = 0  # Inject sequence bug; prior evidence must survive.
        with self.assertRaises(FileExistsError): store.event('second')
        self.assertEqual(json.loads((store.directory/'000000.json').read_text())['kind'], 'first')

    def test_two_runs_aggregate_without_replacement(self):
        self.launch(); self.launch(self.root/'second.json')
        self.assertEqual(inventory(self.root)['totals'], dict(
            search_attempted=2, search_completed=2, winner_oracle_validations=2))

    def test_eight_concurrent_launches_only_one_callback(self):
        def launch(_):
            try: self.launch(); return True
            except FileExistsError: return False
        with concurrent.futures.ThreadPoolExecutor(max_workers=8) as pool:
            outcomes = list(pool.map(launch, range(8)))
        self.assertEqual(sum(outcomes), 1)
        self.assertEqual(self.calls, 1)

    def test_cli_collision_refused_without_sdk_execution(self):
        self.output.write_bytes(b'original')
        process = subprocess.run([sys.executable, str(Path(__file__).with_name('run_pilot_v1.py')),
            '--output', str(self.output), '--parent-commit', 'test-only'],
            capture_output=True, text=True, timeout=10)
        self.assertNotEqual(process.returncode, 0)
        self.assertIn('FileExistsError', process.stderr)
        self.assertNotIn('ModuleNotFoundError', process.stderr)
        self.assertEqual(self.output.read_bytes(), b'original')

    def test_failed_result_preserved(self):
        execute(self.output, lambda event: {'status':'FAILED','failure':'injected'}, {})
        self.assertEqual(json.loads(self.output.read_text())['failure'], 'injected')
        self.assertEqual(json.loads((self.root/'synthetic.json.run/terminal.json').read_text())['status'], 'FAILED')

    def test_symlink_target_untouched(self):
        target = self.root/'target'; target.write_bytes(b'protected')
        self.output.symlink_to(target)
        with self.assertRaises(FileExistsError): self.launch()
        self.assertEqual(target.read_bytes(), b'protected')

    def test_nonfinite_json_rejected(self):
        with self.assertRaises(ValueError):
            create_json(self.output, {'bad':float('nan')})
        # Partial file is deliberately not deleted or overwritten.
        self.assertTrue(self.output.exists())


class RecordingResult(unittest.TextTestResult):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs); self.passed = []
    def addSuccess(self, test):
        super().addSuccess(test); self.passed.append(test.id())


if __name__ == '__main__':
    started = now()
    suite = unittest.defaultTestLoader.loadTestsFromTestCase(RetentionTests)
    result = unittest.TextTestRunner(verbosity=2, resultclass=RecordingResult).run(suite)
    root = Path(__file__).resolve().parent
    report = dict(status='PASSED' if result.wasSuccessful() else 'FAILED',
        started_at_utc=started, finished_at_utc=now(), python=platform.python_version(),
        command='python src/verify_evidence_store.py', parent_commit='4397409396b7b15c60db18c80f7ebdbceeb6cfb2',
        test_count=result.testsRun, passed=result.passed,
        failures=[(t.id(), msg) for t,msg in result.failures+result.errors],
        source_sha256={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in
                       (root/'evidence_store.py', root/'run_pilot_v1.py', Path(__file__))},
        data='Synthetic file fixtures and stub callbacks in temporary directories',
        quantum_search_evaluations=0, sdk_circuits_executed=0,
        limitations=['No new quantum numerical regression or grid',
                     'No power-loss, disk-full, distributed filesystem or adversarial filesystem test',
                     'Inventory counts retained event directories only, not undiscovered historical runs'])
    create_json(root.parent/'results/2026-10-20-retention-audit.json', report)
    sys.exit(not result.wasSuccessful())
