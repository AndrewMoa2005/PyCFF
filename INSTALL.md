# Languages

- en [English](INSTALL.md)
- zh_CN [简体中文](INSTALL.zh_CN.md)

# PyCFF - Installation Instructions

## 1. Quick Installation

The software has been uploaded to PyPI and supports installation via pip command:
```bash
python -m pip install pycff
````

You can also find the binary package for the corresponding platform on the [Release](https://github.com/AndrewMoa2005/PyCFF/releases) page and decompress it to run it.

## 2. Build Environment

Build dependencies:
 - Python >= 3.12
 - Git (optional) : update version number when building
 - C/C++ Compiler (optional) : required when building pyd/so files

The source code provides a `build.py` script for quick and easy building. Users should create a virtual environment before building:
```bash
python -m venv myvenv # myvenv is the name of the virtual environment, which can be defined as needed
```

On Windows, use the following command to activate the virtual environment:
```powershell
./myvenv/Scripts/activate # in windows, it is recommended to run under posershell
```

On Linux and other Posix platforms, use the following command to activate the virtual environment:
```bash
source ./myvenv/bin/activate # in posix
```

After activating the virtual environment, the `(myvenv)` character will be displayed at the beginning of the command line, indicating that Python under the command line is running in the virtual environment `myvenv`. Install the dependencies using the following command:
```bash
pip install -r requirements.txt
```

After the build is complete, exit the virtual environment by deactivating it:
```bash
deactivate # The same command is used under windows and posix
```

## 3. Build Script

Run the following command to display help information for the build script:
```
python build.py -h
```

 - Option `-h`/`--help` displays command-line help.
 - Option `-v`/`--version` displays the software version information (Git is requirement).
 - Option `-d`/`--dir` specifies the build directory name, usually under the source code directory, defaults to `build`.
 - Option `-b`/`--build` generates `whl` file while running `pyinstaller` to package the source code into executable files, where `dir` means packaging into a directory (default), and `one` means packaging into a single executable file.
 - Option `-u`/`--update` compiles `.ui` and `.qrc` files in the source code into `.py` files for debugging purposes.
 - Option `-t`/`--translate` allows for multi-language translation. `up` updates `.ts` files in the source code, `gui` launches the `linguistgui` interface and opens `.ts` files, and `gen` compiles `.ts` files into `.qm` files. This switch is typically used for debugging purposes only.
 - Option `-p`/`--pyd`, whether to compile `.py` files into `.pyd`/`.so`.

In general, you can quickly build an executable program using the following command:
```bash
python build.py -b
```
The generated executable file/compressed package is located in the `[source_dir]/build/pkg` directory, and the whl file generated at the same time is located in the `[source_dir]/build/dist` path.

After generating the whl file, install it using the following command (The content in {} depends on the compiled output in the local environment):
```bash
pip install pycff-{version}-{python}-{abi}-{platform}_{machine}.whl
```
After the release package is installed, you can start the main program through `pycff` or `python -m pycff`.
