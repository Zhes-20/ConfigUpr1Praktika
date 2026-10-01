"""Unit tests for strict syntax validation and edge cases."""

import unittest

from src.config import Config
from src.shell_core import ShellCore


def make_shell() -> ShellCore:
    """Create shell instance loaded with medium VFS."""
    cfg = Config(vfs_path="vfs_data/vfs_medium.json")
    return ShellCore(config=cfg)


class TestEdgeCases(unittest.TestCase):
    """Test suite verifying parser edge cases and strict syntax errors."""

    def test_leading_space_error(self) -> None:
        """Verify command with leading spaces causes syntax error."""
        shell = make_shell()
        code, out = shell.execute_line("  ls")
        self.assertEqual(code, 1)
        self.assertIn("unexpected leading whitespace", out)

    def test_leading_tab_error(self) -> None:
        """Verify command with leading tab causes syntax error."""
        shell = make_shell()
        code, out = shell.execute_line("\tls")
        self.assertEqual(code, 1)
        self.assertIn("unexpected leading whitespace", out)

    def test_all_spaces_error(self) -> None:
        """Verify line consisting solely of spaces causes syntax error."""
        shell = make_shell()
        code, out = shell.execute_line("   ")
        self.assertEqual(code, 1)
        self.assertIn("unexpected leading whitespace", out)

    def test_empty_line_ignored(self) -> None:
        """Verify empty line executes cleanly with zero return code."""
        shell = make_shell()
        code, out = shell.execute_line("")
        self.assertEqual(code, 0)
        self.assertEqual(out, "")

    def test_unclosed_variable_expansion(self) -> None:
        """Verify unclosed braced variable causes syntax error."""
        shell = make_shell()
        code, out = shell.execute_line("echo ${HOME")
        self.assertEqual(code, 1)
        self.assertIn("unclosed variable expansion", out)

    def test_empty_variable_name(self) -> None:
        """Verify empty braced variable causes syntax error."""
        shell = make_shell()
        code, out = shell.execute_line("echo ${}")
        self.assertEqual(code, 1)
        self.assertIn("empty variable name", out)

    def test_invalid_variable_name_characters(self) -> None:
        """Verify invalid variable characters cause syntax error."""
        shell = make_shell()
        code, out = shell.execute_line("echo ${TEST-INVALID}")
        self.assertEqual(code, 1)
        self.assertIn("bad substitution", out)

    def test_unclosed_quote_error(self) -> None:
        """Verify unclosed quotes report syntax error."""
        shell = make_shell()
        code, out = shell.execute_line('cat "readme.txt')
        self.assertEqual(code, 1)
        self.assertIn("unclosed quotation mark", out)

    def test_cd_too_many_arguments(self) -> None:
        """Verify cd with multiple arguments reports error."""
        shell = make_shell()
        code, out = shell.execute_line("cd docs extra_dir")
        self.assertEqual(code, 1)
        self.assertIn("too many arguments", out)

    def test_exit_too_many_arguments(self) -> None:
        """Verify exit with arguments reports error."""
        shell = make_shell()
        code, out = shell.execute_line("exit 1 2 3")
        self.assertEqual(code, 1)
        self.assertIn("too many arguments", out)

    def test_conf_dump_extra_arguments(self) -> None:
        """Verify conf-dump rejecting arguments."""
        shell = make_shell()
        code, out = shell.execute_line("conf-dump /etc/cfg")
        self.assertEqual(code, 1)
        self.assertIn("does not accept arguments", out)

    def test_mv_missing_destination(self) -> None:
        """Verify mv with only one operand reports missing destination."""
        shell = make_shell()
        code, out = shell.execute_line("mv readme.txt")
        self.assertEqual(code, 1)
        self.assertIn("missing destination file operand", out)

    def test_mv_too_many_arguments(self) -> None:
        """Verify mv with more than two operands reports error."""
        shell = make_shell()
        code, out = shell.execute_line("mv file1 file2 file3")
        self.assertEqual(code, 1)
        self.assertIn("too many arguments", out)


if __name__ == "__main__":
    unittest.main()
