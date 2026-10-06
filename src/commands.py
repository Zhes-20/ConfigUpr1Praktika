from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from src.shell_core import ShellCore

MV_OPERANDS_COUNT = 2


def _list_target(shell: "ShellCore", target: str) -> tuple[int, str]:
    resolved = shell.vfs.resolve_path(shell.cwd, target)
    node = shell.vfs.get_node(resolved)
    if node is None:
        return 1, f"ls: cannot access '{target}': No such file or directory"
    if not node.is_dir:
        return 0, node.name
    return 0, "  ".join(shell.vfs.list_dir(resolved))


def cmd_ls(shell: "ShellCore", args: list[str]) -> tuple[int, str]:
    for arg in args:
        if arg.startswith("-"):
            return 1, f"ls: unsupported option '{arg}'"

    targets = args or [shell.cwd]
    outputs: list[str] = []
    for target in targets:
        code, out = _list_target(shell, target)
        if code != 0:
            return code, out
        outputs.append(f"{target}:\n{out}" if len(targets) > 1 else out)
    return 0, "\n\n".join(outputs)


def cmd_cd(shell: "ShellCore", args: list[str]) -> tuple[int, str]:
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
    if not args:
        return 1, "touch: missing file operand"

    for path_arg in args:
        resolved = shell.vfs.resolve_path(shell.cwd, path_arg)
        try:
            shell.vfs.touch(resolved)
        except (OSError, ValueError) as err:
            return 1, f"touch: cannot touch '{path_arg}': {err}"

    return 0, ""


def cmd_mv(shell: "ShellCore", args: list[str]) -> tuple[int, str]:
    if not args:
        return 1, "mv: missing file operand"
    if len(args) == 1:
        return 1, f"mv: missing destination file operand after '{args[0]}'"
    if len(args) > MV_OPERANDS_COUNT:
        return 1, "mv: too many arguments"

    src_arg, dst_arg = args[0], args[1]
    src_res = shell.vfs.resolve_path(shell.cwd, src_arg)
    dst_res = shell.vfs.resolve_path(shell.cwd, dst_arg)

    try:
        shell.vfs.move(src_res, dst_res)
    except (OSError, ValueError) as err:
        return 1, f"mv: cannot move '{src_arg}': {err}"

    return 0, ""
