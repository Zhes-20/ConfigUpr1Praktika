"""Automated code style checker matching Sovetov's criteria.

Rules verified:
- Line length <= 80 characters (P2)
- Function length <= 40 lines (F1)
- Function arguments count <= 7 (A1)
- Docstrings present on modules, classes, and functions (K1)
- Cyclomatic complexity <= 10 (C1)
"""

import ast
import os
import sys

MAX_LINE_LENGTH = 80
MAX_FUNC_LINES = 40
MAX_FUNC_ARGS = 7
MAX_COMPLEXITY = 10


def calculate_complexity(node: ast.AST) -> int:
    """Calculate cyclomatic complexity of an AST node."""
    complexity = 1
    for child in ast.walk(node):
        if isinstance(
            child,
            (
                ast.If,
                ast.While,
                ast.For,
                ast.AsyncFor,
                ast.ExceptHandler,
                ast.With,
                ast.AsyncWith,
                ast.Assert,
            ),
        ):
            complexity += 1
        elif isinstance(child, ast.BoolOp):
            complexity += len(child.values) - 1
    return complexity


def check_file(filepath: str) -> list[str]:
    """Check a single python file against style criteria."""
    errors: list[str] = []
    with open(filepath, "r", encoding="utf-8") as file_handle:
        lines = file_handle.readlines()

    for idx, line in enumerate(lines, start=1):
        clean_line = line.rstrip("\r\n")
        if len(clean_line) > MAX_LINE_LENGTH:
            errors.append(
                f"{filepath}:{idx}: Line length {len(clean_line)} "
                f"> {MAX_LINE_LENGTH}"
            )

    content = "".join(lines)
    try:
        tree = ast.parse(content, filename=filepath)
    except SyntaxError as parse_error:
        errors.append(f"{filepath}: Syntax error: {parse_error}")
        return errors

    if not ast.get_docstring(tree):
        errors.append(f"{filepath}:1: Missing module docstring")

    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            func_name = node.name
            line_no = node.lineno
            end_line = getattr(node, "end_lineno", line_no)
            func_length = end_line - line_no + 1
            if func_length > MAX_FUNC_LINES:
                errors.append(
                    f"{filepath}:{line_no}: Function '{func_name}' length "
                    f"{func_length} > {MAX_FUNC_LINES} lines"
                )

            args_count = len(node.args.args)
            if args_count > MAX_FUNC_ARGS:
                errors.append(
                    f"{filepath}:{line_no}: Function '{func_name}' has "
                    f"{args_count} args > {MAX_FUNC_ARGS}"
                )

            if not ast.get_docstring(node):
                errors.append(
                    f"{filepath}:{line_no}: Function '{func_name}' "
                    "missing docstring"
                )

            complexity = calculate_complexity(node)
            if complexity > MAX_COMPLEXITY:
                errors.append(
                    f"{filepath}:{line_no}: Function '{func_name}' "
                    f"complexity {complexity} > {MAX_COMPLEXITY}"
                )

        elif isinstance(node, ast.ClassDef):
            class_name = node.name
            line_no = node.lineno
            if not ast.get_docstring(node):
                errors.append(
                    f"{filepath}:{line_no}: Class '{class_name}' "
                    "missing docstring"
                )

    return errors


def main() -> int:
    """Run code checks on src and tests directories."""
    all_errors: list[str] = []
    target_dirs = ["src", "tests"]
    for target in target_dirs:
        if not os.path.exists(target):
            continue
        for root, _, files in os.walk(target):
            for file in files:
                if file.endswith(".py"):
                    full_path = os.path.join(root, file)
                    all_errors.extend(check_file(full_path))

    if all_errors:
        print("Style violations found:")
        for error in all_errors:
            print("  -", error)
        return 1

    print("All Python style checks passed successfully!")
    return 0


if __name__ == "__main__":
    sys.exit(main())
