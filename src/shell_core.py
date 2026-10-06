import os
import re
import shlex
from typing import Callable, Optional

from src.commands import cmd_cat, cmd_cd, cmd_ls, cmd_mv, cmd_rev, cmd_touch
from src.config import Config, format_conf_dump
from src.vfs import Vfs


def _validate_env_syntax(text: str) -> None:
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
    _validate_env_syntax(text)
    pattern = re.compile(r"\$\{([A-Za-z0-9_]+)\}|\$([A-Za-z0-9_]+)")

    def replace_match(match: re.Match[str]) -> str:
        var_name = match.group(1) or match.group(2)
        return os.environ.get(var_name, "")

    return pattern.sub(replace_match, text)


def parse_command_line(raw_line: str) -> list[str]:
    expanded = expand_env_vars(raw_line)
    try:
        return shlex.split(expanded)
    except ValueError as parse_err:
        raise ValueError(
            f"unclosed quotation mark: {parse_err}"
        ) from parse_err


class ShellCore:
    def __init__(self, config: Optional[Config] = None) -> None:
        self.config = config or Config()
        self.username = self.config.username
        self.hostname = self.config.hostname
        self.cwd = "/"
        self.is_exit = False
        self.vfs = Vfs()
        self.vfs_error: Optional[str] = None
        self._load_vfs()

    def _load_vfs(self) -> None:
        if not self.config.vfs_path:
            return
        try:
            self.vfs.load_from_json(self.config.vfs_path)
        except (FileNotFoundError, ValueError) as load_err:
            self.vfs_error = str(load_err)

    def get_title(self) -> str:
        return f"Эмулятор - [{self.username}@{self.hostname}]"

    def get_prompt(self) -> str:
        return f"[{self.username}@{self.hostname} {self.cwd}]$ "

    def execute_script_file(self, script_path: str) -> tuple[int, str]:
        if not os.path.exists(script_path):
            return 1, f"script error: file not found: {script_path}"
        try:
            with open(script_path, "r", encoding="utf-8") as f_in:
                lines = [line.rstrip("\r\n") for line in f_in]
        except OSError as err:
            return 1, f"script error: failed to read {script_path}: {err}"

        outputs: list[str] = []
        for line in lines:
            stripped = line.strip()
            if not stripped or stripped.startswith("#"):
                continue
            code, out = self.execute_line(line)
            if out:
                outputs.append(out)
            if code != 0:
                outputs.append(f"script aborted at: {line}")
                return code, "\n".join(outputs)
            if self.is_exit:
                break
        return 0, "\n".join(outputs)

    def _dispatch_command(
        self,
        cmd: str,
        args: list[str],
    ) -> tuple[int, str]:
        if cmd == "exit":
            if args:
                return 1, "exit: too many arguments"
            self.is_exit = True
            return 0, "logout"
        if cmd == "conf-dump":
            if args:
                return 1, "conf-dump: does not accept arguments"
            return 0, format_conf_dump(self.config)
        if cmd in ("source", "run-script"):
            if len(args) != 1:
                return 1, f"{cmd}: exactly one script file argument required"
            return self.execute_script_file(args[0])

        table: dict[str, Callable[[list[str]], tuple[int, str]]] = {
            "ls": lambda a: cmd_ls(self, a),
            "cd": lambda a: cmd_cd(self, a),
            "cat": lambda a: cmd_cat(self, a),
            "rev": lambda a: cmd_rev(self, a),
            "touch": lambda a: cmd_touch(self, a),
            "mv": lambda a: cmd_mv(self, a),
        }
        handler = table.get(cmd)
        if handler is not None:
            return handler(args)

        return 127, f"{cmd}: command not found"

    def execute_line(self, raw_line: str) -> tuple[int, str]:
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
