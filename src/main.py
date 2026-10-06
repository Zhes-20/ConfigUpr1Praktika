import sys

from src.config import parse_cli_args
from src.gui import ShellGui
from src.shell_core import ShellCore


def main() -> int:
    cfg = parse_cli_args(sys.argv[1:])
    shell = ShellCore(config=cfg)
    gui = ShellGui(shell=shell)
    gui.run()
    return 0


if __name__ == "__main__":
    sys.exit(main())
