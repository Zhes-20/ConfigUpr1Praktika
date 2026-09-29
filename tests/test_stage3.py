"""Unit tests for Stage 3: Virtual File System loaded from JSON."""

import unittest

from src.vfs import Vfs


class TestStage3Vfs(unittest.TestCase):
    """Test suite for in-memory virtual file system operations."""

    def setUp(self) -> None:
        """Create fresh VFS instance before each test."""
        self.vfs = Vfs()

    def test_load_minimal_vfs(self) -> None:
        """Verify loading minimal VFS containing a single file."""
        self.vfs.load_from_json("vfs_data/vfs_minimal.json")
        items = self.vfs.list_dir("/")
        self.assertEqual(items, ["hello.txt"])
        content = self.vfs.read_file("/hello.txt")
        self.assertIn("Minimal VFS", content)

    def test_load_medium_vfs(self) -> None:
        """Verify loading medium VFS with subdirectories and files."""
        self.vfs.load_from_json("vfs_data/vfs_medium.json")
        root_items = self.vfs.list_dir("/")
        self.assertEqual(root_items, ["docs", "readme.txt"])
        doc_items = self.vfs.list_dir("/docs")
        self.assertEqual(doc_items, ["notes.txt"])

    def test_load_deep_vfs(self) -> None:
        """Verify loading VFS with depth of at least 3 nested levels."""
        self.vfs.load_from_json("vfs_data/vfs_deep.json")
        deep_file = "/level1/level2/level3/deep_file.txt"
        content = self.vfs.read_file(deep_file)
        self.assertIn("Deep nested file", content)

    def test_vfs_metadata_support(self) -> None:
        """Verify VFS nodes store metadata fields."""
        self.vfs.load_from_json("vfs_data/vfs_medium.json")
        root_node = self.vfs.get_node("/")
        self.assertIsNotNone(root_node)
        if root_node is not None:
            self.assertEqual(root_node.owner, "root")
            self.assertEqual(root_node.permissions, "rwxr-xr-x")

        file_node = self.vfs.get_node("/readme.txt")
        self.assertIsNotNone(file_node)
        if file_node is not None:
            self.assertEqual(file_node.owner, "root")
            self.assertEqual(file_node.permissions, "rw-r--r--")
            self.assertTrue(file_node.size > 0)

    def test_file_not_found_error(self) -> None:
        """Verify error when VFS file path does not exist on disk."""
        with self.assertRaises(FileNotFoundError):
            self.vfs.load_from_json("vfs_data/does_not_exist.json")

    def test_corrupted_json_error(self) -> None:
        """Verify error when VFS JSON file is malformed."""
        with self.assertRaises(ValueError):
            self.vfs.load_from_json("vfs_data/vfs_corrupted.json")

    def test_read_directory_as_file_error(self) -> None:
        """Verify IsADirectoryError when reading directory as file."""
        self.vfs.load_from_json("vfs_data/vfs_medium.json")
        with self.assertRaises(IsADirectoryError):
            self.vfs.read_file("/docs")

    def test_list_file_as_dir_error(self) -> None:
        """Verify NotADirectoryError when listing a file."""
        self.vfs.load_from_json("vfs_data/vfs_minimal.json")
        with self.assertRaises(NotADirectoryError):
            self.vfs.list_dir("/hello.txt")

    def test_dump_structure(self) -> None:
        """Verify formatted tree structure output contains paths."""
        self.vfs.load_from_json("vfs_data/vfs_minimal.json")
        dump = self.vfs.dump_structure()
        self.assertTrue(len(dump) >= 2)
        self.assertIn("/ [dir", dump[0])
        self.assertIn("/hello.txt [file", dump[1])

    def test_resolve_path_navigation(self) -> None:
        """Verify canonical path resolution with dots and slashes."""
        res1 = self.vfs.resolve_path("/a/b", "..")
        self.assertEqual(res1, "/a")

        res2 = self.vfs.resolve_path("/a/b", "../c/./d")
        self.assertEqual(res2, "/a/c/d")

        res3 = self.vfs.resolve_path("/a/b", "/root_dir")
        self.assertEqual(res3, "/root_dir")


if __name__ == "__main__":
    unittest.main()
