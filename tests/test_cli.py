import io
import types
import sys
from unittest import TestCase
from unittest.mock import patch

import womgr_cli

class CLITest(TestCase):
    def run_cli(self, args, ping_return=0, which_map=None):
        if which_map is None:
            which_map = {"reboot": "/sbin/reboot", "shutdown": "/sbin/shutdown"}

        def fake_run(cmd, stdout=None):
            return types.SimpleNamespace(returncode=ping_return)

        def fake_which(cmd):
            return which_map.get(cmd)

        out = io.StringIO()
        with (
            patch.object(sys, "argv", ["womgr_cli.py"] + args),
            patch("womgr.entities.subprocess.run", side_effect=fake_run),
            patch("womgr.entities.shutil.which", side_effect=fake_which),
            patch("womgr.entities.subprocess.Popen"),
            patch("sys.stdout", new=out),
        ):
            womgr_cli.main()
        return out.getvalue()

    def test_status_success(self):
        output = self.run_cli([
            "server",
            "00:11:22:33:44:55",
            "1.2.3.4",
            "Office",
            "linux",
            "status",
        ])
        assert "Device is reachable" in output
        assert "Restart available: True" in output
        assert "Shutdown available: True" in output

    def test_invalid_os(self):
        output = self.run_cli([
            "server",
            "00:11:22:33:44:55",
            "1.2.3.4",
            "Office",
            "foo",
            "ping",
        ])
        assert "Invalid OS type" in output

    def test_restart_missing_command(self):
        output = self.run_cli([
            "server",
            "00:11:22:33:44:55",
            "1.2.3.4",
            "Office",
            "linux",
            "restart",
        ], which_map={"shutdown": "/sbin/shutdown"})
        assert "reboot command not found" in output

