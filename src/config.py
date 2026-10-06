import argparse
import getpass
import socket
from typing import Optional


class Config:
    def __init__(
        self,
        vfs_path: str = "",
        script_path: str = "",
        username: Optional[str] = None,
        hostname: Optional[str] = None,
    ) -> None:
        self.vfs_path = vfs_path
        self.script_path = script_path
        self.username = username or getpass.getuser()
        self.hostname = hostname or socket.gethostname()

    def to_dict(self) -> dict[str, str]:
        return {
            "vfs_path": self.vfs_path or "(none)",
            "script_path": self.script_path or "(none)",
            "username": self.username,
            "hostname": self.hostname,
        }

    def dump_debug_info(self) -> str:
        lines = [
            "[DEBUG] Заданные параметры эмулятора:",
            f"[DEBUG]   vfs_path: {self.vfs_path or '(not set)'}",
            f"[DEBUG]   script_path: {self.script_path or '(not set)'}",
            f"[DEBUG]   username: {self.username}",
            f"[DEBUG]   hostname: {self.hostname}",
        ]
        return "\n".join(lines)


def parse_cli_args(args: Optional[list[str]] = None) -> Config:
    parser = argparse.ArgumentParser(
        description="UNIX-like Shell Emulator for Configuration Management"
    )
    parser.add_argument(
        "-v",
        "--vfs",
        dest="vfs_path",
        default="",
        help="Path to virtual file system JSON file",
    )
    parser.add_argument(
        "-s",
        "--script",
        dest="script_path",
        default="",
        help="Path to startup script file",
    )

    parsed = parser.parse_args(args)
    return Config(
        vfs_path=parsed.vfs_path,
        script_path=parsed.script_path,
    )


def format_conf_dump(cfg: Config) -> str:
    pairs = cfg.to_dict()
    return "\n".join(f"{key}: {val}" for key, val in pairs.items())
