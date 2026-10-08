"""Unit tests for Stage 2: Configuration, CLI arguments, and scripts."""

import os
import tempfile
import unittest

from src.config import Config, format_conf_dump, parse_cli_args
from src.shell_core import ShellCore


class TestStage2Config(unittest.TestCase):
    """Test suite for stage 2 configuration parsing and script runner."""

    def test_default_config(self) -> None:
        """Verify default configuration values when no flags are given."""
        cfg = parse_cli_args([])
        self.assertEqual(cfg.vfs_path, "")
        self.assertEqual(cfg.script_path, "")
        self.assertTrue(len(cfg.username) > 0)
        self.assertTrue(len(cfg.hostname) > 0)

    def test_explicit_cli_arguments(self) -> None:
        """Verify parsing explicit flags for VFS and startup script."""
        args = ["--vfs", "/tmp/vfs.json", "--script", "/tmp/init.txt"]
        cfg = parse_cli_args(args)
        self.assertEqual(cfg.vfs_path, "/tmp/vfs.json")
        self.assertEqual(cfg.script_path, "/tmp/init.txt")

    def test_short_cli_arguments(self) -> None:
        """Verify short CLI options -v and -s."""
        args = ["-v", "vfs.json", "-s", "start.txt"]
        cfg = parse_cli_args(args)
        self.assertEqual(cfg.vfs_path, "vfs.json")
        self.assertEqual(cfg.script_path, "start.txt")

    def test_format_conf_dump(self) -> None:
        """Verify formatting config dictionary into key-value lines."""
        cfg = Config(
            vfs_path="disk.json",
            script_path="auto.txt",
            username="testuser",
            hostname="myhost",
        )
        dump_text = format_conf_dump(cfg)
        self.assertIn("vfs_path: disk.json", dump_text)
        self.assertIn("script_path: auto.txt", dump_text)
        self.assertIn("username: testuser", dump_text)
        self.assertIn("hostname: myhost", dump_text)

    def test_conf_dump_command_execution(self) -> None:
        """Verify shell core executes conf-dump successfully."""
        cfg = Config(
            vfs_path="disk.json",
            script_path="auto.txt",
            username="testuser",
            hostname="myhost",
        )
        shell = ShellCore(config=cfg)
        code, out = shell.execute_line("conf-dump")
        self.assertEqual(code, 0)
        self.assertIn("vfs_path: disk.json", out)

    def test_conf_dump_rejects_extra_args(self) -> None:
        """Verify conf-dump returns error if extraneous arguments given."""
        shell = ShellCore()
        code, out = shell.execute_line("conf-dump /etc/hosts")
        self.assertEqual(code, 1)
        self.assertIn("does not accept arguments", out)

    def test_script_execution_success(self) -> None:
        """Verify executing a valid script file sequentially."""
        shell = ShellCore()
        with tempfile.NamedTemporaryFile("w+", delete=False) as tmp_file:
            tmp_file.write("# Test script\nconf-dump\nls\n")
            tmp_path = tmp_file.name

        try:
            code, out = shell.execute_script_file(tmp_path)
            self.assertEqual(code, 0)
            self.assertIn("vfs_path:", out)
        finally:
            os.remove(tmp_path)

    def test_script_execution_nonexistent(self) -> None:
        """Verify executing nonexistent script reports error code."""
        shell = ShellCore()
        code, out = shell.execute_script_file("no_such_file_12345.txt")
        self.assertEqual(code, 1)
        self.assertIn("file not found", out)

    def test_script_execution_syntax_error(self) -> None:
        """Verify executing script with invalid syntax halts on error."""
        shell = ShellCore()
        with tempfile.NamedTemporaryFile("w+", delete=False) as tmp_file:
            tmp_file.write("conf-dump\n  bad_indent_cmd\nls\n")
            tmp_path = tmp_file.name

        try:
            code, out = shell.execute_script_file(tmp_path)
            self.assertEqual(code, 1)
            self.assertIn("unexpected leading whitespace", out)
        finally:
            os.remove(tmp_path)

    def test_user_input_source_command(self) -> None:
        """Verify running script via interactive source command."""
        shell = ShellCore()
        with tempfile.NamedTemporaryFile("w+", delete=False) as tmp_file:
            tmp_file.write("conf-dump\n")
            tmp_path = tmp_file.name

        try:
            code, out = shell.execute_line(f"source {tmp_path}")
            self.assertEqual(code, 0)
            self.assertIn("vfs_path:", out)
        finally:
            os.remove(tmp_path)


if __name__ == "__main__":
    unittest.main()
