"""Unit tests for Stage 5: in-memory touch and mv commands."""

import unittest

from src.config import Config
from src.shell_core import ShellCore


def make_shell() -> ShellCore:
    """Create shell instance loaded with medium VFS."""
    cfg = Config(vfs_path="vfs_data/vfs_medium.json")
    return ShellCore(config=cfg)


class TestStage5Mutations(unittest.TestCase):
    """Test suite for touch and mv commands modifying VFS in memory."""

    def test_touch_new_file(self) -> None:
        """Verify touch creates new empty file in memory."""
        shell = make_shell()
        code, _ = shell.execute_line("touch test_created.txt")
        self.assertEqual(code, 0)
        items = shell.vfs.list_dir("/")
        self.assertIn("test_created.txt", items)

    def test_touch_existing_file(self) -> None:
        """Verify touch on existing file succeeds without error."""
        shell = make_shell()
        code, _ = shell.execute_line("touch readme.txt")
        self.assertEqual(code, 0)

    def test_touch_updates_mtime(self) -> None:
        """Verify touch refreshes modification time of existing file."""
        shell = make_shell()
        node = shell.vfs.get_node("/readme.txt")
        old_mtime = node.mtime
        shell.execute_line("touch readme.txt")
        self.assertNotEqual(node.mtime, old_mtime)

    def test_touch_parent_is_file_error(self) -> None:
        """Verify touch returns error if parent path is a file."""
        shell = make_shell()
        code, out = shell.execute_line("touch readme.txt/child.txt")
        self.assertEqual(code, 1)
        self.assertIn("cannot touch", out)

    def test_mv_dir_over_file_error(self) -> None:
        """Verify mv refuses to replace file with directory."""
        shell = make_shell()
        code, out = shell.execute_line("mv docs readme.txt")
        self.assertEqual(code, 1)
        self.assertIn("cannot move", out)
        self.assertIn("docs", shell.vfs.list_dir("/"))

    def test_touch_missing_parent_error(self) -> None:
        """Verify touch returns error if parent directory is missing."""
        shell = make_shell()
        code, out = shell.execute_line("touch /non_dir/test.txt")
        self.assertEqual(code, 1)
        self.assertIn("cannot touch", out)

    def test_mv_rename_file(self) -> None:
        """Verify mv renames file in the same directory."""
        shell = make_shell()
        code, _ = shell.execute_line("mv readme.txt manual.txt")
        self.assertEqual(code, 0)
        items = shell.vfs.list_dir("/")
        self.assertNotIn("readme.txt", items)
        self.assertIn("manual.txt", items)

    def test_mv_into_directory(self) -> None:
        """Verify mv moves file into an existing directory."""
        shell = make_shell()
        code, _ = shell.execute_line("mv readme.txt docs")
        self.assertEqual(code, 0)
        doc_items = shell.vfs.list_dir("/docs")
        self.assertIn("readme.txt", doc_items)

    def test_mv_missing_source_error(self) -> None:
        """Verify mv returns error when source file is not found."""
        shell = make_shell()
        code, out = shell.execute_line("mv ghost.txt docs")
        self.assertEqual(code, 1)
        self.assertIn("cannot move", out)

    def test_mv_root_error(self) -> None:
        """Verify mv returns error when attempting to move root."""
        shell = make_shell()
        code, out = shell.execute_line("mv / /docs")
        self.assertEqual(code, 1)
        self.assertIn("cannot move", out)

    def test_mv_dir_into_subfolder_error(self) -> None:
        """Verify error when moving directory into its own descendant."""
        shell = make_shell()
        code, out = shell.execute_line("mv docs docs/sub")
        self.assertEqual(code, 1)
        self.assertIn("cannot move", out)


if __name__ == "__main__":
    unittest.main()
