"""Convert Qt Designer .ui files to .py files.

Usable as a library (imported by build_script.py) and as a small CLI:

    python build_tools/ui_to_py.py                  # use the current interpreter
    python build_tools/ui_to_py.py --venv venv      # use the python of a venv
"""
from __future__ import annotations

import argparse
import shlex
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
IS_WINDOWS = sys.platform.startswith("win")
DEFAULT_UI_FOLDER = ROOT / "ibridgesgui" / "ui_files"

# Calls the same entry point as the `pyside6-uic` script, but through the given
# interpreter, no venv activation or PATH lookup is needed.
_UIC_SNIPPET = "import sys; from PySide6.scripts.pyside_tool import uic; sys.exit(uic())"


def venv_python(venv: Path) -> Path:
    """Return the python executable of a virtual environment."""
    return venv / ("Scripts/python.exe" if IS_WINDOWS else "bin/python")


def run_cmd(cmd: list, **kwargs) -> None:
    """Run a command and exit with its return code on failure.

    Output is streamed so progress is visible in the terminal and in CI logs.
    """
    cmd = [str(c) for c in cmd]
    print(f"$ {shlex.join(cmd)}", flush=True)
    try:
        subprocess.run(cmd, check=True, **kwargs)
    except subprocess.CalledProcessError as err:
        sys.exit(err.returncode)


def replace_icon_paths(py_file: Path) -> None:
    """Make icon paths relative to the distribution folder."""
    content = py_file.read_text(encoding="utf-8")
    content = content.replace('addFile(u"../icons/', 'addFile(u"icons/')
    py_file.write_text(content, encoding="utf-8")


def remove_pyui_files(ui_folder: Path) -> None:
    """Remove generated .py files (only those that have a matching .ui file)."""
    for ui_file in ui_folder.glob("*.ui"):
        py_file = ui_file.with_suffix(".py")
        if py_file.exists():
            print(f"Removing {py_file}")
            py_file.unlink()


def ui_to_py(ui_folder: Path, python: Path | str = sys.executable) -> None:
    """Convert all .ui files in `ui_folder` to .py files using `python` (needs PySide6)."""
    ui_files = sorted(ui_folder.glob("*.ui"))
    if not ui_files:
        sys.exit(f"No .ui files found in {ui_folder}")
    for ui_file in ui_files:
        py_file = ui_file.with_suffix(".py")
        print(f"Converting {ui_file.name} -> {py_file.name}")
        run_cmd([python, "-c", _UIC_SNIPPET, ui_file, "-o", py_file])
        replace_icon_paths(py_file)


def build_parser() -> argparse.ArgumentParser:
    """Create the argument parser."""
    parser = argparse.ArgumentParser(description="Convert .ui files to .py files.")
    parser.add_argument("--ui-folder", type=Path, default=DEFAULT_UI_FOLDER,
                        help="Folder with the .ui files (default: %(default)s)")
    parser.add_argument("--venv", type=Path, default=None,
                        help="Use the python of this virtual environment "
                             "(default: current interpreter)")
    return parser


def main(argv: list[str] | None = None) -> None:
    """CLI entry point."""
    args = build_parser().parse_args(argv)
    python = venv_python(args.venv) if args.venv else Path(sys.executable)
    remove_pyui_files(args.ui_folder)
    ui_to_py(args.ui_folder, python)


if __name__ == "__main__":
    main()
