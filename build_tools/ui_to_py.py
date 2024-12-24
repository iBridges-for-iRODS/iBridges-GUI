"""Convert Ui file to PY file."""
from pathlib import Path
from platform import system
from subprocess import STDOUT, run


def run_cmd(cmd: str):
    """Run a commandline command and check if it was successful.

    Args:
        cmd : str
            Command to run.

    """
    if system()[0].upper() == "W":  # Windows
        ps = run(cmd, stderr=STDOUT, shell=True, universal_newlines=True)
    else:
        ps = run(cmd, stderr=STDOUT, shell=True, universal_newlines=True, executable="/bin/bash")
    # Print all errors
    if ps.stderr is not None or ps.returncode != 0:
        print(f"commandline error: {ps.stderr}")
        raise Exception("shell run error")


def os_specific_settings():
    """Get the settings for the operating system.

    Returns:
        python : str
            python version
        cmd_sep : str
            command separator

    """
    if system()[0].upper() == "W":  # windows
        cmd_sep = "&&"
        python = "python"  # python version
    else:  # Linux, ensure it uses python 3
        cmd_sep = ";"
        python = "python3"
    return (python, cmd_sep)


def ui_to_py(ui_folder: Path, venv_activate: str, cmd_sep: str):
    """Convert the .ui files to .py files.

    pyside6-uic gui/MainWindow.ui -o gui/MainWindow.py
    Args:
        ui_folder : Path
            folder containing the .ui files
        venv_activate : str
            command to activate the virtual environment
        cmd_sep : str
            command separator

    """
    for ui_file in ui_folder.glob('*.ui'):
        py_file = ui_file.with_suffix('.py')
        print(f"Converting {py_file.name} to .py")
        run_cmd(f"""{venv_activate} {cmd_sep} pyside6-uic "{ui_file}" -o "{py_file}" """)
        replace_icon_paths(py_file)


def replace_icon_paths(py_file: Path):
    """Replace the icon paths in the .py file.

    Args:
        py_file : Path
            .py file to update

    """
    # Read the content of the file
    with py_file.open('r', encoding='utf-8') as file:
        content = file.read()

    # Replace the icon paths
    content = content.replace('addFile(u"../icons/', 'addFile(u"icons/')
    # Write the modified content back to the file
    with py_file.open('w', encoding='utf-8') as file:
        file.write(content)


def remove_pyui_files(ui_folder: Path):
    """Remove the locally stored .py versions of the files.

    Args:
        ui_folder : Path
            folder containing the .ui files

    """
    pyuifiles = ui_folder.glob('*.py')
    for file in pyuifiles:
        # Skip __init__.py files
        if "__init__" in file.name:
            continue
        print(f"Removing {file}")
        file.unlink()


if __name__ == "__main__":
    code_dir = Path("ibridgesgui")
    icons_folder = Path.cwd().joinpath(code_dir, 'icons')
    ui_folder = Path.cwd().joinpath(code_dir, 'ui_files')

    # Step 1 Convert .ui files to .py files
    # Recompiling is the best way to ensure they are up to date
    remove_pyui_files(ui_folder)
    (python, cmd_sep) = os_specific_settings()
    venv_activate = Path.cwd().joinpath('venv').joinpath('Scripts', 'activate.bat')
    ui_to_py(ui_folder, venv_activate, cmd_sep)