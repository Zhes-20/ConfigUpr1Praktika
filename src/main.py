"""Entry point for the shell emulator application."""

import sys

from src.gui import ShellGui
from src.shell_core import ShellCore


def main() -> int:
    """Initialize shell core and launch graphical user interface."""
    shell = ShellCore()
    gui = ShellGui(shell=shell)
    gui.run()
    return 0


if __name__ == "__main__":
    sys.exit(main())
