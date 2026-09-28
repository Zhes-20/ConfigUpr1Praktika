"""Entry point for the terminal shell emulator application."""

import sys

from src.config import parse_cli_args
from src.gui import ShellGui
from src.shell_core import ShellCore


def main() -> int:
    """Parse CLI options, initialize shell core and launch GUI."""
    cfg = parse_cli_args(sys.argv[1:])
    shell = ShellCore(config=cfg)
    gui = ShellGui(shell=shell)
    gui.run()
    return 0


if __name__ == "__main__":
    sys.exit(main())
