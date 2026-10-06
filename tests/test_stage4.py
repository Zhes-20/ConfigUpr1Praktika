import unittest

from src.config import Config
from src.shell_core import ShellCore


def make_shell() -> ShellCore:
    cfg = Config(vfs_path="vfs_data/vfs_medium.json")
    return ShellCore(config=cfg)


class TestStage4Commands(unittest.TestCase):
    def test_ls_current_directory(self) -> None:
        shell = make_shell()
        code, out = shell.execute_line("ls")
        self.assertEqual(code, 0)
        self.assertIn("docs", out)
        self.assertIn("readme.txt", out)

    def test_ls_target_directory(self) -> None:
        shell = make_shell()
        code, out = shell.execute_line("ls /docs")
        self.assertEqual(code, 0)
        self.assertEqual(out, "notes.txt")

    def test_ls_non_existent(self) -> None:
        shell = make_shell()
        code, out = shell.execute_line("ls /no_such_dir")
        self.assertEqual(code, 1)
        self.assertIn("No such file or directory", out)

    def test_ls_multiple_targets(self) -> None:
        shell = make_shell()
        code, out = shell.execute_line("ls docs readme.txt")
        self.assertEqual(code, 0)
        self.assertIn("docs:\nnotes.txt", out)
        self.assertIn("readme.txt:\nreadme.txt", out)

    def test_ls_unsupported_option(self) -> None:
        shell = make_shell()
        code, out = shell.execute_line("ls -la")
        self.assertEqual(code, 1)
        self.assertIn("unsupported option", out)

    def test_cd_navigation(self) -> None:
        shell = make_shell()
        code, _ = shell.execute_line("cd docs")
        self.assertEqual(code, 0)
        self.assertEqual(shell.cwd, "/docs")

        code, _ = shell.execute_line("cd ..")
        self.assertEqual(code, 0)
        self.assertEqual(shell.cwd, "/")

    def test_cd_errors(self) -> None:
        shell = make_shell()
        code1, out1 = shell.execute_line("cd /missing")
        self.assertEqual(code1, 1)
        self.assertIn("No such file", out1)

        code2, out2 = shell.execute_line("cd readme.txt")
        self.assertEqual(code2, 1)
        self.assertIn("Not a directory", out2)

    def test_cat_command(self) -> None:
        shell = make_shell()
        code, out = shell.execute_line("cat readme.txt")
        self.assertEqual(code, 0)
        self.assertIn("UNIX Shell Emulator Project", out)

    def test_cat_errors(self) -> None:
        shell = make_shell()
        code1, out1 = shell.execute_line("cat")
        self.assertEqual(code1, 1)
        self.assertIn("missing file operand", out1)

        code2, out2 = shell.execute_line("cat docs")
        self.assertEqual(code2, 1)
        self.assertIn("Is a directory", out2)

    def test_rev_command(self) -> None:
        shell = make_shell()
        shell.vfs.load_from_json("vfs_data/vfs_minimal.json")
        code, out = shell.execute_line("rev hello.txt")
        self.assertEqual(code, 0)
        self.assertEqual(out, "!SFV laminiM ,olleH")


if __name__ == "__main__":
    unittest.main()
