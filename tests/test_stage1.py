"""Unit tests for Stage 1: REPL, parser, title and exit."""

import os
import unittest

from src.shell_core import ShellCore, expand_env_vars, parse_command_line

os.environ["TEST_USER"] = "alice"
os.environ["TEST_DIR"] = "/tmp/demo"


class TestStage1Repl(unittest.TestCase):
    """Test suite for stage 1 parser and shell core functionality."""

    def test_expand_simple_env_var(self) -> None:
        """Verify simple $VAR expansion."""
        result = expand_env_vars("echo $TEST_USER")
        self.assertEqual(result, "echo alice")

    def test_expand_braced_env_var(self) -> None:
        """Verify braced ${VAR} expansion."""
        result = expand_env_vars("ls ${TEST_DIR}/sub")
        self.assertEqual(result, "ls /tmp/demo/sub")

    def test_expand_missing_env_var(self) -> None:
        """Verify expansion of non-existent variables to empty string."""
        result = expand_env_vars("echo $NON_EXISTENT_VAR_12345")
        self.assertEqual(result, "echo ")

    def test_parse_quotes_with_vars(self) -> None:
        """Verify parsing command lines with quotes and variables."""
        tokens = parse_command_line('ls "$TEST_DIR"')
        self.assertEqual(tokens, ["ls", "/tmp/demo"])

    def test_parse_syntax_error_quotes(self) -> None:
        """Verify error handling on unclosed quotations."""
        shell = ShellCore()
        code, out = shell.execute_line('ls "unclosed string')
        self.assertEqual(code, 1)
        self.assertIn("syntax error", out)

    def test_leading_whitespace_syntax_error(self) -> None:
        """Verify error handling on leading whitespace before command."""
        shell = ShellCore()
        code, out = shell.execute_line("  ls")
        self.assertEqual(code, 1)
        self.assertIn("unexpected leading whitespace", out)

    def test_title_contains_user_and_host(self) -> None:
        """Verify window title contains system username and hostname."""
        shell = ShellCore()
        title = shell.get_title()
        self.assertIn(shell.username, title)
        self.assertIn(shell.hostname, title)

    def test_ls_invocation(self) -> None:
        """Verify ls command responds on root directory."""
        shell = ShellCore()
        code, _ = shell.execute_line("ls")
        self.assertEqual(code, 0)

    def test_cd_invocation(self) -> None:
        """Verify cd command responds on root directory."""
        shell = ShellCore()
        code, _ = shell.execute_line("cd /")
        self.assertEqual(code, 0)

    def test_exit_command(self) -> None:
        """Verify exit command sets is_exit flag."""
        shell = ShellCore()
        self.assertFalse(shell.is_exit)
        code, out = shell.execute_line("exit")
        self.assertEqual(code, 0)
        self.assertTrue(shell.is_exit)
        self.assertEqual(out, "logout")


if __name__ == "__main__":
    unittest.main()
