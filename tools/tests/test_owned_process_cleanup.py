"""Exercise denied cleanup signals against small, owned POSIX process groups."""
import errno
import os
from pathlib import Path
import signal
import subprocess
import sys
import tempfile
import time
import unittest
from unittest.mock import patch

TOOLS = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(TOOLS))
from arena_macos import OwnedProcess


@unittest.skipUnless(os.name == "posix", "POSIX process-group cleanup")
class OwnedProcessCleanupTests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory(prefix="owned-process-cleanup-")
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name)
        self.real_killpg = os.killpg

    def denied(self, group, sig):
        raise PermissionError(errno.EPERM, "injected denied group signal")

    def reap(self, owned):
        try:
            self.real_killpg(owned.process.pid, signal.SIGKILL)
        except ProcessLookupError:
            pass
        owned.process.wait(timeout=3)
        owned.output.close()

    def test_denied_signal_after_real_group_exit_preserves_actual_status(self):
        for status in (0, 23):
            with self.subTest(status=status):
                owned = OwnedProcess([sys.executable, "-c", f"raise SystemExit({status})"], log=self.root / f"exit-{status}.log")
                self.addCleanup(self.reap, owned)
                self.assertEqual(owned.wait(3), status)
                # The group is really gone; inject the macOS late-signal errno
                # and let the production fallback inspect the real process table.
                with patch("arena_macos.os.killpg", side_effect=self.denied) as signals:
                    self.assertEqual(owned.stop(), status)
                self.assertTrue(owned.output.closed)
                self.assertEqual([call.args for call in signals.call_args_list],
                                 [(owned.process.pid, signal.SIGTERM), (owned.process.pid, signal.SIGKILL)])

    def test_live_leader_refusal_is_not_hidden_by_an_empty_snapshot(self):
        owned = OwnedProcess([sys.executable, "-c", "import time;time.sleep(60)"], log=self.root / "leader.log")
        self.addCleanup(self.reap, owned)
        with patch("arena_macos.os.killpg", side_effect=self.denied), \
                patch("arena_macos.subprocess.run") as snapshot:
            with self.assertRaises(PermissionError):
                owned.stop(grace=.01)
            snapshot.assert_not_called()
        self.assertIsNone(owned.process.poll())

    def test_live_orphan_refusal_remains_failure_after_leader_exits(self):
        ready = self.root / "orphan.pid"
        child = ("import os,signal,time;from pathlib import Path;"
                 "signal.signal(signal.SIGTERM,signal.SIG_IGN);"
                 f"Path({str(ready)!r}).write_text(str(os.getpid()));time.sleep(60)")
        parent = ("import subprocess,sys,time;from pathlib import Path;"
                  f"subprocess.Popen([sys.executable,'-c',{child!r}]);\n"
                  f"while not Path({str(ready)!r}).exists(): time.sleep(.01)\n")
        owned = OwnedProcess([sys.executable, "-c", parent], log=self.root / "orphan.log")
        self.addCleanup(self.reap, owned)
        self.assertEqual(owned.wait(3), 0)
        orphan = int(ready.read_text())

        def deny_kill(group, sig):
            self.assertEqual(group, owned.process.pid)
            if sig == signal.SIGKILL:
                return self.denied(group, sig)
            return self.real_killpg(group, sig)

        with patch("arena_macos.os.killpg", side_effect=deny_kill):
            with self.assertRaises(PermissionError):
                owned.stop(grace=.01)
        os.kill(orphan, 0)  # The live orphan was detected, not reported cleaned.
        self.reap(owned)
        deadline = time.monotonic() + 3
        while time.monotonic() < deadline:
            result = subprocess.run(["ps", "-p", str(orphan), "-o", "stat="], capture_output=True, text=True)
            if not result.stdout.strip() or result.stdout.strip().startswith("Z"):
                break
            time.sleep(.02)
        else:
            self.fail("owned orphan survived explicit test cleanup")

    def test_unavailable_or_malformed_process_table_cannot_prove_completion(self):
        probes = [subprocess.TimeoutExpired("ps", 2), OSError("ps unavailable"),
                  subprocess.CompletedProcess([], 0, ""),
                  subprocess.CompletedProcess([], 0, "unparseable\n")]
        for index, result in enumerate(probes):
            with self.subTest(index=index):
                owned = OwnedProcess([sys.executable, "-c", "pass"], log=self.root / f"probe-{index}.log")
                self.addCleanup(self.reap, owned)
                owned.wait(3)
                kwargs = {"side_effect": result} if isinstance(result, Exception) else {"return_value": result}
                with patch("arena_macos.os.killpg", side_effect=self.denied), \
                        patch("arena_macos.subprocess.run", **kwargs):
                    with self.assertRaises(PermissionError):
                        owned.stop()

    def test_only_zombie_or_dead_members_count_as_completed(self):
        owned = OwnedProcess([sys.executable, "-c", "pass"], log=self.root / "states.log")
        self.addCleanup(self.reap, owned)
        owned.wait(3)
        for state in ("Z", "Z+", "X", "S", "R", "T", "D"):
            with self.subTest(state=state), patch("arena_macos.subprocess.run", return_value=
                    subprocess.CompletedProcess([], 0, f"{owned.process.pid} {state}\n")):
                self.assertEqual(owned._group_finished(), state[0] in "ZX")


if __name__ == "__main__":
    unittest.main()
