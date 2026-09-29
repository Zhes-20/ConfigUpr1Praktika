"""Implementations of shell commands operating on virtual file system."""

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from src.shell_core import ShellCore


def cmd_ls(shell: "ShellCore", args: list[str]) -> tuple[int, str]:
    """List directory contents or file info in virtual file system."""
    target = args[0] if args else shell.cwd
    resolved = shell.vfs.resolve_path(shell.cwd, target)
    node = shell.vfs.get_node(resolved)
    if node is None:
        return 1, f"ls: cannot access '{target}': No such file or directory"

    if not node.is_dir:
        return 0, node.name

    items = shell.vfs.list_dir(resolved)
    return 0, "  ".join(items)


def cmd_cd(shell: "ShellCore", args: list[str]) -> tuple[int, str]:
    """Change current working directory in virtual file system."""
    if len(args) > 1:
        return 1, "cd: too many arguments"

    target = args[0] if args else "/"
    resolved = shell.vfs.resolve_path(shell.cwd, target)
    node = shell.vfs.get_node(resolved)
    if node is None:
        return 1, f"cd: {target}: No such file or directory"
    if not node.is_dir:
        return 1, f"cd: {target}: Not a directory"

    shell.cwd = resolved
    return 0, ""


def cmd_cat(shell: "ShellCore", args: list[str]) -> tuple[int, str]:
    """Display contents of one or more files from virtual file system."""
    if not args:
        return 1, "cat: missing file operand"

    outputs: list[str] = []
    for path_arg in args:
        resolved = shell.vfs.resolve_path(shell.cwd, path_arg)
        node = shell.vfs.get_node(resolved)
        if node is None:
            return 1, f"cat: {path_arg}: No such file or directory"
        if node.is_dir:
            return 1, f"cat: {path_arg}: Is a directory"

        content = shell.vfs.read_file(resolved)
        outputs.append(content.rstrip("\r\n"))

    return 0, "\n".join(outputs)


def cmd_rev(shell: "ShellCore", args: list[str]) -> tuple[int, str]:
    """Reverse lines character by character from specified virtual files."""
    if not args:
        return 1, "rev: missing file operand"

    outputs: list[str] = []
    for path_arg in args:
        resolved = shell.vfs.resolve_path(shell.cwd, path_arg)
        node = shell.vfs.get_node(resolved)
        if node is None:
            return 1, f"rev: cannot open '{path_arg}': No such file"
        if node.is_dir:
            return 1, f"rev: {path_arg}: Is a directory"

        text = shell.vfs.read_file(resolved)
        reversed_lines = [line[::-1] for line in text.splitlines()]
        outputs.append("\n".join(reversed_lines))

    return 0, "\n".join(outputs)


def cmd_touch(shell: "ShellCore", args: list[str]) -> tuple[int, str]:
    """Create empty virtual files or update modification status."""
    if not args:
        return 1, "touch: missing file operand"

    for path_arg in args:
        resolved = shell.vfs.resolve_path(shell.cwd, path_arg)
        try:
            shell.vfs.touch(resolved)
        except (FileNotFoundError, IsADirectoryError, ValueError) as err:
            return 1, f"touch: cannot touch '{path_arg}': {err}"

    return 0, ""


def cmd_mv(shell: "ShellCore", args: list[str]) -> tuple[int, str]:
    """Move or rename files and directories in virtual file system."""
    if not args:
        return 1, "mv: missing file operand"
    if len(args) == 1:
        return 1, f"mv: missing destination file operand after '{args[0]}'"
    if len(args) > 2:
        return 1, "mv: too many arguments"

    src_arg, dst_arg = args[0], args[1]
    src_res = shell.vfs.resolve_path(shell.cwd, src_arg)
    dst_res = shell.vfs.resolve_path(shell.cwd, dst_arg)

    try:
        shell.vfs.move(src_res, dst_res)
    except (
        PermissionError,
        FileNotFoundError,
        ValueError,
    ) as err:
        return 1, f"mv: cannot move '{src_arg}': {err}"

    return 0, ""
