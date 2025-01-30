"""Build executable with Nuitka."""
from pathlib import Path
from platform import system
from shutil import copytree, rmtree
import platform

import ui_to_py as uipy

# Build config and file paths
code_dir = Path("ibridgesgui")
icons_folder = Path.cwd().joinpath(code_dir, 'icons')
ui_folder = Path.cwd().joinpath(code_dir, 'ui_files')
venv = Path.cwd().joinpath('venv')
# Debug mode shows the console (command prompt with the logging)
debug_mode = True
# ---------------------------------------------------------#


def replace_folder(source: Path | str, destination: Path | str):
    """Replace the destination folder with the source folder."""
    copytree(source, destination, dirs_exist_ok=True)


def create_exe():
    """Create the exe file for the application."""
    (python, cmd_sep) = uipy.os_specific_settings()

    # Step 1: Setup
    # Step 1a, Ensure the folder for the venv exists
    if (not venv.exists()) or (not venv.is_dir()):
        venv.mkdir()

    # Step 1b, Create the venv if needed
    # windows
    if system()[0].upper() == "W":
        venv_activate = venv.joinpath('Scripts', 'activate.bat')
    else:  # Ubuntu/IOS
        venv_activate = venv.joinpath('bin', 'activate')
    if (not venv_activate.exists()) or (not venv_activate.is_file()):
        venv_activate = f"\"{str(venv_activate)}\""
        if system()[0].upper() != "W":
            venv_activate = f"source {venv_activate}"
        uipy.run_cmd(f"{python} -m venv {venv}")
        uipy.run_cmd(f"{venv_activate} {cmd_sep} python -m pip install --upgrade pip")
        uipy.run_cmd(f"{venv_activate} {cmd_sep} pip install .")
        uipy.run_cmd(f"{venv_activate} {cmd_sep} pip install .[deploy]")
    else:
        venv_activate = f"\"{str(venv_activate)}\""

    # Step 2 Convert .ui files to .py files
    # Recompiling is the best way to ensure they are up to date
    uipy.remove_pyui_files(ui_folder)
    uipy.ui_to_py(ui_folder, venv_activate, cmd_sep)

    # Step 3, Activate venv and run nuitka
    cmd = f"{venv_activate} {cmd_sep} python -m nuitka "
    if not debug_mode:
        cmd += "--disable-console "
    cmd += f"--standalone --include-package=irods --nofollow-import-to=irods.test\
        --remove-output --enable-plugin=pyside6 --include-qt-plugins=sensible,styles \
        --assume-yes-for-downloads --show-progress  \
        --windows-icon-from-ico=\"{icons_folder.joinpath('iBridges.ico')}\" \
        {code_dir.joinpath('__main__.py')} --quiet"
    uipy.run_cmd(cmd)

    # Step 4, move the icons folder to the distribution folder
    replace_folder(icons_folder,
                   icons_folder.parent.parent.joinpath('__main__.dist',
                                                       icons_folder.name))

    # Step 5, rename the distribution folder and file
    shipping_folder = Path('output/ibridgesgui')
    if Path(shipping_folder).exists():
        rmtree(shipping_folder, ignore_errors=True)
    shipping_folder.parent.mkdir(parents=True, exist_ok=True)
    Path('__main__.dist').rename(shipping_folder)
    if 'windows' in platform.system().lower():
        Path(f'{shipping_folder}/__main__.exe').rename(f'{shipping_folder}/ibridges.exe')
    elif 'darwin' in platform.system().lower():
        Path(f'{shipping_folder}/__main__.bin').rename(f'{shipping_folder}/ibridges.bin')

if __name__ == "__main__":
    create_exe()
