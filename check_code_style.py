import ast
import io
import os
import re
import sys
import tokenize

MAX_LINE_LENGTH = 80
MAX_FUNC_LINES = 40
MAX_FUNC_ARGS = 7
MAX_COMPLEXITY = 10
ALLOWED_NUMBERS = (0, 1)
TARGETS = ("src", "tests", "check_code_style.py")
SNAKE_CASE = re.compile(r"_*[a-z][a-z0-9_]*")
CAP_WORDS = re.compile(r"_*[A-Z][A-Za-z0-9]*")
FUNC_NODES = (ast.FunctionDef, ast.AsyncFunctionDef)
BRANCH_NODES = (
    ast.If,
    ast.While,
    ast.For,
    ast.AsyncFor,
    ast.ExceptHandler,
    ast.With,
    ast.AsyncWith,
    ast.Assert,
)


def calculate_complexity(node: ast.AST) -> int:
    complexity = 1
    for child in ast.walk(node):
        if isinstance(child, BRANCH_NODES):
            complexity += 1
        elif isinstance(child, ast.BoolOp):
            complexity += len(child.values) - 1
    return complexity


def check_line_lengths(filepath: str, lines: list[str]) -> list[str]:
    errors: list[str] = []
    for idx, line in enumerate(lines, start=1):
        length = len(line.rstrip("\r\n"))
        if length > MAX_LINE_LENGTH:
            errors.append(
                f"{filepath}:{idx}: Line length {length} > {MAX_LINE_LENGTH}"
            )
    return errors


def check_comments(filepath: str, source: str) -> list[str]:
    errors: list[str] = []
    reader = io.StringIO(source).readline
    for token in tokenize.generate_tokens(reader):
        if token.type == tokenize.COMMENT:
            errors.append(
                f"{filepath}:{token.start[0]}: Comment in code"
            )
    return errors


def check_function_size(filepath: str, node: ast.FunctionDef) -> list[str]:
    errors: list[str] = []
    where = f"{filepath}:{node.lineno}: Function '{node.name}'"
    length = getattr(node, "end_lineno", node.lineno) - node.lineno + 1
    if length > MAX_FUNC_LINES:
        errors.append(f"{where} length {length} > {MAX_FUNC_LINES} lines")

    args_count = len(node.args.args)
    if args_count > MAX_FUNC_ARGS:
        errors.append(f"{where} has {args_count} args > {MAX_FUNC_ARGS}")

    complexity = calculate_complexity(node)
    if complexity > MAX_COMPLEXITY:
        errors.append(f"{where} complexity {complexity} > {MAX_COMPLEXITY}")
    return errors


def check_function_names(filepath: str, node: ast.FunctionDef) -> list[str]:
    names = [node.name] + [arg.arg for arg in node.args.args]
    return [
        f"{filepath}:{node.lineno}: Name '{name}' is not snake_case"
        for name in names
        if not SNAKE_CASE.fullmatch(name)
    ]


def check_definitions(filepath: str, tree: ast.Module) -> list[str]:
    errors: list[str] = []
    for node in ast.walk(tree):
        if not isinstance(node, FUNC_NODES + (ast.ClassDef,)):
            continue
        where = f"{filepath}:{node.lineno}: '{node.name}'"
        if isinstance(node, FUNC_NODES):
            errors.extend(check_function_size(filepath, node))
            errors.extend(check_function_names(filepath, node))
        elif not CAP_WORDS.fullmatch(node.name):
            errors.append(f"{where} is not CapWords")
    return errors


def is_magic_number(node: ast.AST) -> bool:
    if not isinstance(node, ast.Constant):
        return False
    value = node.value
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        return False
    return value not in ALLOWED_NUMBERS


def check_magic_numbers(filepath: str, tree: ast.Module) -> list[str]:
    errors: list[str] = []
    for node in ast.walk(tree):
        if not isinstance(node, ast.Compare):
            continue
        for operand in [node.left] + node.comparators:
            if is_magic_number(operand):
                errors.append(
                    f"{filepath}:{node.lineno}: Magic number "
                    f"{operand.value} in comparison"
                )
    return errors


def check_file(filepath: str) -> list[str]:
    with open(filepath, "r", encoding="utf-8") as file_handle:
        source = file_handle.read()

    errors = check_line_lengths(filepath, source.splitlines())
    try:
        tree = ast.parse(source, filename=filepath)
    except SyntaxError as parse_error:
        errors.append(f"{filepath}: Syntax error: {parse_error}")
        return errors

    errors.extend(check_comments(filepath, source))
    errors.extend(check_definitions(filepath, tree))
    errors.extend(check_magic_numbers(filepath, tree))
    return errors


def collect_python_files() -> list[str]:
    found: list[str] = []
    for target in TARGETS:
        if os.path.isfile(target):
            found.append(target)
            continue
        for root, _, files in os.walk(target):
            found.extend(
                os.path.join(root, name)
                for name in files
                if name.endswith(".py")
            )
    return sorted(found)


def main() -> int:
    all_errors: list[str] = []
    for filepath in collect_python_files():
        all_errors.extend(check_file(filepath))

    if all_errors:
        print("Style violations found:")
        for error in all_errors:
            print("  -", error)
        return 1

    print("All Python style checks passed successfully!")
    return 0


if __name__ == "__main__":
    sys.exit(main())
