"""Unit tests for Stage 3: Virtual File System loaded from JSON."""

import unittest

from src.vfs import Vfs

MINIMAL_DUMP_LINES = 2


class TestStage3Vfs(unittest.TestCase):
    """Test suite for in-memory virtual file system operations."""

    def test_load_minimal_vfs(self) -> None:
        """Verify loading minimal VFS containing a single file."""
        vfs = Vfs()
        vfs.load_from_json("vfs_data/vfs_minimal.json")
        items = vfs.list_dir("/")
        self.assertEqual(items, ["hello.txt"])
        content = vfs.read_file("/hello.txt")
        self.assertIn("Minimal VFS", content)

    def test_load_medium_vfs(self) -> None:
        """Verify loading medium VFS with subdirectories and files."""
        vfs = Vfs()
        vfs.load_from_json("vfs_data/vfs_medium.json")
        root_items = vfs.list_dir("/")
        self.assertEqual(root_items, ["docs", "readme.txt"])
        doc_items = vfs.list_dir("/docs")
        self.assertEqual(doc_items, ["notes.txt"])

    def test_load_deep_vfs(self) -> None:
        """Verify loading VFS with depth of at least 3 nested levels."""
        vfs = Vfs()
        vfs.load_from_json("vfs_data/vfs_deep.json")
        deep_file = "/level1/level2/level3/deep_file.txt"
        content = vfs.read_file(deep_file)
        self.assertIn("Deep nested file", content)

    def test_vfs_metadata_support(self) -> None:
        """Verify VFS nodes store metadata fields."""
        vfs = Vfs()
        vfs.load_from_json("vfs_data/vfs_medium.json")
        root_node = vfs.get_node("/")
        self.assertIsNotNone(root_node)
        if root_node is not None:
            self.assertEqual(root_node.owner, "root")
            self.assertEqual(root_node.permissions, "rwxr-xr-x")

        file_node = vfs.get_node("/readme.txt")
        self.assertIsNotNone(file_node)
        if file_node is not None:
            self.assertEqual(file_node.owner, "root")
            self.assertEqual(file_node.permissions, "rw-r--r--")
            self.assertTrue(file_node.size > 0)

    def test_file_not_found_error(self) -> None:
        """Verify error when VFS file path does not exist on disk."""
        vfs = Vfs()
        with self.assertRaises(FileNotFoundError):
            vfs.load_from_json("vfs_data/does_not_exist.json")

    def test_corrupted_json_error(self) -> None:
        """Verify error when VFS JSON file is malformed."""
        vfs = Vfs()
        with self.assertRaises(ValueError):
            vfs.load_from_json("vfs_data/vfs_corrupted.json")

    def test_read_directory_as_file_error(self) -> None:
        """Verify IsADirectoryError when reading directory as file."""
        vfs = Vfs()
        vfs.load_from_json("vfs_data/vfs_medium.json")
        with self.assertRaises(IsADirectoryError):
            vfs.read_file("/docs")

    def test_list_file_as_dir_error(self) -> None:
        """Verify NotADirectoryError when listing a file."""
        vfs = Vfs()
        vfs.load_from_json("vfs_data/vfs_minimal.json")
        with self.assertRaises(NotADirectoryError):
            vfs.list_dir("/hello.txt")

    def test_dump_structure(self) -> None:
        """Verify formatted tree structure output contains paths."""
        vfs = Vfs()
        vfs.load_from_json("vfs_data/vfs_minimal.json")
        dump = vfs.dump_structure()
        self.assertEqual(len(dump), MINIMAL_DUMP_LINES)
        self.assertIn("/ [dir", dump[0])
        self.assertIn("/hello.txt [file", dump[1])

    def test_resolve_path_navigation(self) -> None:
        """Verify canonical path resolution with dots and slashes."""
        vfs = Vfs()
        res1 = vfs.resolve_path("/a/b", "..")
        self.assertEqual(res1, "/a")

        res2 = vfs.resolve_path("/a/b", "../c/./d")
        self.assertEqual(res2, "/a/c/d")

        res3 = vfs.resolve_path("/a/b", "/root_dir")
        self.assertEqual(res3, "/root_dir")


if __name__ == "__main__":
    unittest.main()
