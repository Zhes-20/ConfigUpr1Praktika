"""Unit tests for Stage 4: ls, cd, cat, rev commands."""

import unittest

from src.config import Config
from src.shell_core import ShellCore


class TestStage4Commands(unittest.TestCase):
    """Test suite for basic UNIX-like shell commands with VFS."""

    def setUp(self) -> None:
        """Initialize shell instance loaded with medium VFS."""
        cfg = Config(vfs_path="vfs_data/vfs_medium.json")
        self.shell = ShellCore(config=cfg)

    def test_ls_current_directory(self) -> None:
        """Verify ls command listing current root directory."""
        code, out = self.shell.execute_line("ls")
        self.assertEqual(code, 0)
        self.assertIn("docs", out)
        self.assertIn("readme.txt", out)

    def test_ls_target_directory(self) -> None:
        """Verify ls command on specific subdirectory."""
        code, out = self.shell.execute_line("ls /docs")
        self.assertEqual(code, 0)
        self.assertEqual(out, "notes.txt")

    def test_ls_non_existent(self) -> None:
        """Verify ls error on non-existent path."""
        code, out = self.shell.execute_line("ls /no_such_dir")
        self.assertEqual(code, 1)
        self.assertIn("No such file or directory", out)

    def test_cd_navigation(self) -> None:
        """Verify cd into directory and cd back via dot-dot."""
        code, _ = self.shell.execute_line("cd docs")
        self.assertEqual(code, 0)
        self.assertEqual(self.shell.cwd, "/docs")

        code, _ = self.shell.execute_line("cd ..")
        self.assertEqual(code, 0)
        self.assertEqual(self.shell.cwd, "/")

    def test_cd_errors(self) -> None:
        """Verify cd errors for non-existent path and target being a file."""
        code1, out1 = self.shell.execute_line("cd /missing")
        self.assertEqual(code1, 1)
        self.assertIn("No such file", out1)

        code2, out2 = self.shell.execute_line("cd readme.txt")
        self.assertEqual(code2, 1)
        self.assertIn("Not a directory", out2)

    def test_cat_command(self) -> None:
        """Verify cat command reading file content."""
        code, out = self.shell.execute_line("cat readme.txt")
        self.assertEqual(code, 0)
        self.assertIn("UNIX Shell Emulator Project", out)

    def test_cat_errors(self) -> None:
        """Verify cat errors for missing operand and target is directory."""
        code1, out1 = self.shell.execute_line("cat")
        self.assertEqual(code1, 1)
        self.assertIn("missing file operand", out1)

        code2, out2 = self.shell.execute_line("cat docs")
        self.assertEqual(code2, 1)
        self.assertIn("Is a directory", out2)

    def test_rev_command(self) -> None:
        """Verify rev command reversing lines from file."""
        self.shell.vfs.load_from_json("vfs_data/vfs_minimal.json")
        code, out = self.shell.execute_line("rev hello.txt")
        self.assertEqual(code, 0)
        # Original: "Hello, Minimal VFS!" -> reversed: "!SFV laminiM ,olleH"
        self.assertEqual(out, "!SFV laminiM ,olleH")


if __name__ == "__main__":
    unittest.main()
