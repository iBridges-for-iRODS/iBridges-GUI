"""Build the iBridges GUI executable with Nuitka.

Local, using your current (activated) environment:
    python build_tools/build_script.py

Local, in a dedicated venv (created and filled on first use):
    python build_tools/build_script.py --venv venv [--rem-venv]

CI (dependencies already installed), also create the release zip:
    python build_tools/build_script.py --zip
"""
from __future__ import annotations

import argparse
import platform
import shutil
import sys
from pathlib import Path

import ui_to_py as uipy

ROOT = uipy.ROOT
CODE_FOLDER = ROOT / "ibridgesgui"
PLATFORM_TAGS = {"Windows": "windows", "Darwin": "macos", "Linux": "ubuntu"}


def prepare_python(venv: Path | None, rem_venv: bool) -> Path:
    """Return the interpreter to build with, creating the venv if requested and needed."""
    if venv is None:
        return Path(sys.executable)
    if rem_venv:
        shutil.rmtree(venv, ignore_errors=True)
    python = uipy.venv_python(venv)
    if not python.is_file():
        uipy.run_cmd([sys.executable, "-m", "venv", venv])
        uipy.run_cmd([python, "-m", "pip", "install", "--upgrade", "pip"])
        uipy.run_cmd([python, "-m", "pip", "install", ".[deploy]"], cwd=ROOT)
    return python


def run_nuitka(python: Path, args: argparse.Namespace) -> Path:
    """Run Nuitka and return the folder it produced."""
    cmd = [
        python, "-m", "nuitka",
        "--standalone",
        "--include-package=irods",
        "--nofollow-import-to=irods.test",
        "--enable-plugin=pyside6",
        "--remove-output",
        "--assume-yes-for-downloads",
        "--show-progress", "--quiet",
        f"--output-dir={args.build_dir}",
        "--output-filename=ibridges_gui",
    ]
    if uipy.IS_WINDOWS:
        cmd.append(f"--windows-icon-from-ico={args.icons_folder / 'iBridges.ico'}")
        if not args.debug_exe:
            cmd.append("--windows-console-mode=disable")
    cmd.append(args.code_folder / "__main__.py")
    uipy.run_cmd(cmd, cwd=ROOT)
    return args.build_dir / "__main__.dist"


def assemble(nuitka_dist: Path, args: argparse.Namespace) -> Path:
    """Move the Nuitka output to its final folder and add the data folders."""
    final = args.dist_dir
    shutil.rmtree(final, ignore_errors=True)
    shutil.move(nuitka_dist, final)
    for folder in (args.icons_folder, args.mdschema_folder):
        print(f"Copying {folder} -> {final / folder.name}")
        shutil.copytree(folder, final / folder.name, dirs_exist_ok=True)
    shutil.rmtree(args.build_dir, ignore_errors=True)
    return final


def make_zip(folder: Path, zip_path: Path) -> Path:
    """Zip the contents of `folder` (no top-level directory in the archive)."""
    archive = shutil.make_archive(str(zip_path.with_suffix("")), "zip", root_dir=folder)
    print(f"Created {archive}")
    return Path(archive)


def build_parser() -> argparse.ArgumentParser:
    """Create the argument parser."""
    p = argparse.ArgumentParser(description="iBridges-GUI executable builder.")
    p.add_argument("--venv", type=Path, default=None,
                   help="Build in this virtual environment, created (and .[deploy] "
                        "installed) if missing. Default: current interpreter.")
    p.add_argument("--rem-venv", action="store_true",
                   help="Remove and recreate the venv given by --venv")
    p.add_argument("--debug-exe", action="store_true",
                   help="Keep the console window (Windows)")
    p.add_argument("--skip-ui", action="store_true",
                   help="Do not regenerate the .py files from the .ui files")
    p.add_argument("--zip", nargs="?", const="auto", default=None, metavar="NAME",
                   help="Also create a zip. Without NAME: ibridgesgui_<os>.zip")
    p.add_argument("--code-folder", type=Path, default=CODE_FOLDER)
    p.add_argument("--ui-folder", type=Path, default=CODE_FOLDER / "ui_files")
    p.add_argument("--icons-folder", type=Path, default=CODE_FOLDER / "icons")
    p.add_argument("--mdschema-folder", type=Path, default=CODE_FOLDER / "md_schemas")
    p.add_argument("--build-dir", type=Path, default=ROOT / "build_nuitka",
                   help="Temporary Nuitka output folder")
    p.add_argument("--dist-dir", type=Path, default=ROOT / "ibridgesgui_dist",
                   help="Final distribution folder")
    return p


def main(argv: list[str] | None = None) -> None:
    """CLI entry point."""
    args = build_parser().parse_args(argv)
    if args.rem_venv and not args.venv:
        sys.exit("--rem-venv needs --venv")

    python = prepare_python(args.venv, args.rem_venv)

    if not args.skip_ui:
        uipy.remove_pyui_files(args.ui_folder)
        uipy.ui_to_py(args.ui_folder, python)

    final = assemble(run_nuitka(python, args), args)
    print(f"Distribution ready in {final}")

    if args.zip:
        tag = PLATFORM_TAGS.get(platform.system(), platform.system().lower())
        name = f"ibridgesgui_{tag}.zip" if args.zip == "auto" else args.zip
        make_zip(final, ROOT / name)


if __name__ == "__main__":
    main()
