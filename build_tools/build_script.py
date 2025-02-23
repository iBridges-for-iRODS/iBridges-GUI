"""Build executable with Nuitka."""
import argparse
from pathlib import Path
from platform import system
from shutil import copytree, rmtree

import ui_to_py as uipy


def replace_folder(source: Path | str, destination: Path | str):
    """Replace the destination folder with the source folder."""
    copytree(source, destination, dirs_exist_ok=True)


def create_exe(args):
    """Create the exe file for the application.

    args : argparse.Namespace
        arguments passed to the function
    """
    (python, cmd_sep) = uipy.os_specific_settings()

    # Step 1: Setup
    # Step 1a,(optional) remove the venv to prevent access issues.
    if args.rem_venv:
        rmtree(args.venv, ignore_errors=True)
    args.venv.mkdir(exist_ok=True)

    # Step 1b, Create the venv if needed
    # windows
    if "windows" in system().lower():
        venv_activate = args.venv.joinpath('Scripts', 'activate.bat')
    else:  # Ubuntu/Mac OS
        venv_activate = args.venv.joinpath('bin', 'activate')
    if (not venv_activate.exists()) or (not venv_activate.is_file()):
        venv_activate = f"\"{str(venv_activate)}\""
        if "windows" not in system().lower():
            venv_activate = f"source {venv_activate}"
        uipy.run_cmd(f"{python} -m venv {args.venv}")
        uipy.run_cmd(f"{venv_activate} {cmd_sep} python -m pip install --upgrade pip")
        uipy.run_cmd(f"{venv_activate} {cmd_sep} pip install .")
        uipy.run_cmd(f"{venv_activate} {cmd_sep} pip install .[deploy]")
    else:
        venv_activate = f"\"{str(venv_activate)}\""

    # Step 2 Convert .ui files to .py files
    # Recompiling is the best way to ensure they are up to date
    uipy.remove_pyui_files(args.ui_folder)
    uipy.ui_to_py(args.ui_folder, venv_activate, cmd_sep)

    # Step 3, Activate venv and run nuitka
    cmd = f"{venv_activate} {cmd_sep} python -m nuitka "
    if not args.debug_exe:
        cmd += "--disable-console "
    cmd += f"--standalone --include-package=irods --nofollow-import-to=irods.test\
        --remove-output --enable-plugin=pyside6 \
        --assume-yes-for-downloads --show-progress  \
        --windows-icon-from-ico=\"{args.icons_folder.joinpath('iBridges.ico')}\" \
        {args.code_folder.joinpath('__main__.py')} --quiet"
    uipy.run_cmd(cmd)

    # Step 4, move the icons folder to the distribution folder
    replace_folder(args.icons_folder,
                   args.icons_folder.parent.parent.joinpath('__main__.dist',
                                                            args.icons_folder.name))

    # Step 5, rename the distribution folder and file
    shipping_folder = Path('ibridgesgui_dist')
    if Path(shipping_folder).exists():
        rmtree(shipping_folder, ignore_errors=True)
    Path('__main__.dist').rename(shipping_folder)
    for file in Path(shipping_folder).glob('__main__.*'):
        suffix = file.suffix
        Path(f'{shipping_folder}/__main__{suffix}').rename(f'{shipping_folder}/ibridges_gui{suffix}')


if __name__ == "__main__":
    default_code_folder = Path.cwd().joinpath('ibridgesgui')
    parser = argparse.ArgumentParser(description="iBridges-Gui exe creator.")
    parser.add_argument('--debug_exe', action="store_true",
                        help='Build executable with debug console')
    parser.add_argument('--rem_venv', action="store_true",
                        help='remove virtual environment')
    parser.add_argument('--code_folder', default=default_code_folder, type=Path,
                        help='Full path to the directory with code')
    parser.add_argument('--ui_folder', default=default_code_folder.joinpath('ui_files'),
                        type=Path, required=False,
                        help='Full path to the directory with ui files')
    parser.add_argument('--icons_folder', default=default_code_folder.joinpath('icons'),
                        type=Path, required=False,
                        help='Full path to the directory with the icons')
    parser.add_argument('--venv', default=Path.cwd().joinpath('venv'),
                        type=Path, required=False,
                        help='Full path to virtual python environment')
    args = parser.parse_args()
    create_exe(args)
