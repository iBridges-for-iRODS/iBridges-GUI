# Build tools

Scripts to build the iBridges GUI as a standalone executable with [Nuitka](https://nuitka.net/).
They run the same way on your machine and in the GitHub Action.

| File | Purpose |
|------|---------|
| `build_script.py` | Full build: compile `.ui` files, run Nuitka, assemble and optionally zip |
| `ui_to_py.py` | Only convert the Qt Designer `.ui` files to `.py` files |

## Requirements

- Python 3.11 or newer (the CI uses 3.11)
- A C compiler. On Windows Nuitka downloads one for you (`--assume-yes-for-downloads`). On Linux install `gcc` and `patchelf`. On macOS install the Xcode command line tools.
- The project dependencies: `pip install .[deploy]` (includes PySide6 and Nuitka)

## Quick start

From the repository root, in an environment where `.[deploy]` is installed:

```
python build_tools/build_script.py
```

The result is in `ibridgesgui_dist/`; the executable is `ibridges_gui` (`.exe` on Windows).

The scripts locate the repository relative to their own path, so they also work when started from another directory.

## build_script.py

```
python build_tools/build_script.py [options]
```

| Option | Description |
|--------|-------------|
| `--venv PATH` | Build in this virtual environment. It is created and `.[deploy]` is installed if it does not exist. Default: the current interpreter. |
| `--rem-venv` | Delete and recreate the venv given by `--venv` (useful if files are locked or the venv is broken). |
| `--debug-exe` | Keep the console window (Windows), handy for seeing errors at start-up. |
| `--skip-ui` | Do not regenerate the `.py` files from the `.ui` files. |
| `--zip [NAME]` | Also create a zip of the distribution. Without `NAME` it is `ibridgesgui_<windows\|macos\|ubuntu>.zip` in the repository root. |
| `--code-folder`, `--ui-folder`, `--icons-folder`, `--mdschema-folder` | Override the default source folders inside `ibridgesgui/`. |
| `--build-dir` | Temporary Nuitka output folder (default `build_nuitka/`, removed after the build). |
| `--dist-dir` | Final output folder (default `ibridgesgui_dist/`). |

### What it does

1. Selects the interpreter (current one, or the venv, creating it if needed).
2. Regenerates the `.py` files from the `.ui` files, unless `--skip-ui`.
3. Runs Nuitka in standalone mode.
4. Moves the result to `ibridgesgui_dist/` and copies the `icons` and `md_schemas` folders into it.
5. Creates the zip if `--zip` was given.

### Examples

```
# Build in a separate venv, recreated from scratch
python build_tools/build_script.py --venv venv --rem-venv

# Debug build with a console window (Windows)
python build_tools/build_script.py --debug-exe

# Quick rebuild when no .ui files changed
python build_tools/build_script.py --skip-ui

# Build and create a zip with a custom name
python build_tools/build_script.py --zip my_release.zip
```

## ui_to_py.py

Converts every `.ui` file in the UI folder to a `.py` file next to it and fixes the icon paths so they resolve in the distribution. Only `.py` files that have a matching `.ui` file are replaced.

```
python build_tools/ui_to_py.py [--ui-folder PATH] [--venv PATH]
```

`--venv` makes it use that venv's Python (which must have PySide6 installed). Without it, the current interpreter is used.

## GitHub Action

`.github/workflows/build_executables.yml` builds on Windows, macOS and Linux.

- **On a release** (created): builds, then attaches `ibridgesgui_<os>.zip` to the release.
- **Manually** (Actions tab, *Run workflow*): builds and stores the zips as workflow artifacts, without touching a release.

The build step is just `python build_tools/build_script.py --zip`, so you can reproduce a CI build locally with the same command.