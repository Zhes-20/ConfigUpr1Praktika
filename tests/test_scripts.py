import glob
import unittest

from src.config import Config
from src.shell_core import ShellCore

SCRIPTS_DIR = "emulator_scripts"
SUCCESSFUL_SCRIPTS = {
    "stage2_demo.txt": "vfs_data/vfs_medium.json",
    "stage4_demo.txt": "vfs_data/vfs_medium.json",
    "stage5_demo.txt": "vfs_data/vfs_medium.json",
    "vfs_minimal_demo.txt": "vfs_data/vfs_minimal.json",
    "vfs_deep_demo.txt": "vfs_data/vfs_deep.json",
}
FAILING_SCRIPTS = (
    "stage1_demo.txt",
    "stage3_demo.txt",
    "script_syntax_error.txt",
)


def run_script(script_path: str, vfs_path: str) -> tuple[int, str, str]:
    shell = ShellCore(config=Config(vfs_path=vfs_path))
    code, out = shell.execute_script_file(script_path)
    with open(script_path, "r", encoding="utf-8") as file_handle:
        last_line = file_handle.read().splitlines()[-1]
    return code, out, last_line


class TestStartupScripts(unittest.TestCase):
    def test_successful_scripts_reach_exit(self) -> None:
        for name, vfs_path in SUCCESSFUL_SCRIPTS.items():
            code, out, _ = run_script(f"{SCRIPTS_DIR}/{name}", vfs_path)
            self.assertEqual(code, 0, name)
            self.assertTrue(out.endswith("logout"), name)

    def test_failing_scripts_stop_on_last_line(self) -> None:
        paths = [f"{SCRIPTS_DIR}/{name}" for name in FAILING_SCRIPTS[:2]]
        paths += sorted(glob.glob(f"{SCRIPTS_DIR}/errors/*.txt"))
        for path in paths:
            code, out, last_line = run_script(path, "vfs_data/vfs_medium.json")
            self.assertNotEqual(code, 0, path)
            self.assertTrue(out.endswith(f"aborted at: {last_line}"), path)

    def test_script_stops_at_first_error(self) -> None:
        path = f"{SCRIPTS_DIR}/{FAILING_SCRIPTS[-1]}"
        code, out, _ = run_script(path, "vfs_data/vfs_medium.json")
        self.assertEqual(code, 1)
        self.assertNotIn("logout", out)


if __name__ == "__main__":
    unittest.main()
