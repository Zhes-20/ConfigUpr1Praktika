"""Core shell logic including environment expansion and command dispatch."""

import getpass
import os
import re
import shlex
import socket


def _validate_env_syntax(text: str) -> None:
    """Validate syntax of braced environment variables in text."""
    pos = 0
    while True:
        idx = text.find("${", pos)
        if idx == -1:
            break
        close_idx = text.find("}", idx + 2)
        if close_idx == -1:
            raise ValueError("unclosed variable expansion: missing '}'")
        var_name = text[idx + 2 : close_idx]
        if not var_name:
            raise ValueError("empty variable name in expansion: '${}'")
        if not re.fullmatch(r"[A-Za-z0-9_]+", var_name):
            raise ValueError(
                f"bad substitution: invalid variable name '{var_name}'"
            )
        pos = close_idx + 1


def expand_env_vars(text: str) -> str:
    """Expand environment variables formatted as $VAR or ${VAR}."""
    _validate_env_syntax(text)
    pattern = re.compile(r"\$\{([A-Za-z0-9_]+)\}|\$([A-Za-z0-9_]+)")

    def replace_match(match: re.Match[str]) -> str:
        """Replace regex match with OS environment variable value."""
        var_name = match.group(1) or match.group(2)
        return os.environ.get(var_name, "")

    return pattern.sub(replace_match, text)


def parse_command_line(raw_line: str) -> list[str]:
    """Parse raw line into arguments after expanding environment variables."""
    expanded = expand_env_vars(raw_line)
    try:
        return shlex.split(expanded)
    except ValueError as parse_err:
        raise ValueError(
            f"unclosed quotation mark: {parse_err}"
        ) from parse_err


class ShellCore:
    """Shell emulator core handling execution and state."""

    def __init__(self) -> None:
        """Initialize shell core with user and host information."""
        self.username = getpass.getuser()
        self.hostname = socket.gethostname()
        self.cwd = "/"
        self.is_exit = False

    def get_title(self) -> str:
        """Return formatted window title based on OS user and hostname."""
        return f"Эмулятор - [{self.username}@{self.hostname}]"

    def get_prompt(self) -> str:
        """Return shell prompt string."""
        return f"[{self.username}@{self.hostname} {self.cwd}]$ "

    def _dispatch_command(
        self,
        cmd: str,
        args: list[str],
    ) -> tuple[int, str]:
        """Dispatch command name to stub or exit handler."""
        if cmd == "exit":
            if args:
                return 1, "exit: too many arguments"
            self.is_exit = True
            return 0, "logout"
        if cmd in ("ls", "cd"):
            args_repr = " ".join(args) if args else "(no arguments)"
            return 0, f"{cmd} (stub): called with args: {args_repr}"

        return 127, f"{cmd}: command not found"

    def execute_line(self, raw_line: str) -> tuple[int, str]:
        """Execute single command line and return exit code and output."""
        if not raw_line or raw_line in ("\n", "\r\n"):
            return 0, ""

        if raw_line.startswith((" ", "\t")):
            return 1, "syntax error: unexpected leading whitespace"

        line = raw_line.rstrip("\r\n")
        if not line or line.startswith("#"):
            return 0, ""

        try:
            tokens = parse_command_line(line)
        except ValueError as parse_err:
            return 1, f"syntax error: {parse_err}"

        if not tokens:
            return 0, ""

        cmd, *args = tokens
        return self._dispatch_command(cmd, args)
