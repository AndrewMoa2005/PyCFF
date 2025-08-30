# -*- coding: utf-8 -*-

import os
import shutil
import subprocess
import argparse
import sys
import re
import platform
import zipfile
import tarfile
import tomllib
from glob import glob

pyexecutable = os.path.basename(sys.executable)
hd_list = [
    "PySide6.QtCharts",
    "PySide6.QtGui",
    "PySide6.QtSvg",
    "numpy",
    "scipy.optimize",
    "pycff.form_ui",
    "pycff.resource_rc",
    "pycff.clevertw",
    "pycff.cff",
    "pycff.widget",
]
src_list = [
    "form_ui",
    "resource_rc",
    "clevertw",
    "cff",
    "widget",
    "application",
    "__init__",
    "__main__",
]
locale = ["zh_CN", "en"]
trans_files = ["widget.py", "form.ui", "clevertw.py"]
script_dir = os.path.dirname(os.path.abspath(__file__))
files = [
    "setup.py",
    "compile.py",
    "pyproject.toml",
    "requirements.txt",
    "file-version-info.txt",
    "README.md",
    "README.zh_CN.md",
    "LICENSE",
    "MANIFEST.in",
]
src_folders = ["pycff", "translations", "images"]
build_dir = "build"
app_name = "PyCFF"
if platform.system().lower() == "windows":
    exe_name = app_name + ".exe"
else:
    exe_name = app_name


def rename_whl(dir):
    """
    rename whl file in dir, add py version info
    Args:
        dir (str): dir to rename whl file
    """
    py_version = sys.version.split(".")[:2]
    py_version = "".join(py_version)
    for file in glob(os.path.join(dir, "*.whl")):
        os.rename(file, file.replace("none", f"cp{py_version}"))


def check_src_exists(dir=script_dir):
    dir_files = [f.split(".")[0] for f in os.listdir(dir)]
    for src in src_list:
        if src not in dir_files:
            print(f"error: source file {src} not exists in {dir}!")
            return False
    return True


def zip_dir(dirpath, outFullName):
    """
    compress special dir
    :param dirpath: dir to zip
    :param outFullName: zip file path
    """
    zip = zipfile.ZipFile(outFullName, "w", zipfile.ZIP_DEFLATED)
    for path, dirnames, filenames in os.walk(dirpath):
        # Remove the target root path and only compress the files and subfolders under the target folder
        fpath = path.replace(dirpath, "")
        for filename in filenames:
            zip.write(os.path.join(path, filename), os.path.join(fpath, filename))
    zip.close()
    print(f"compress {dirpath} to {outFullName} success")


def tar_xz_dir(dirpath, outFullName):
    """
    compress special dir
    :param dirpath: dir to tar.xz
    :param outFullName: tar.xz file path
    """
    tar = tarfile.open(outFullName, "w:xz")
    for path, dirnames, filenames in os.walk(dirpath):
        # Remove the target root path and only compress the files and subfolders under the target folder
        fpath = path.replace(dirpath, "")
        for filename in filenames:
            tar.add(os.path.join(path, filename), os.path.join(fpath, filename))
    tar.close()
    print(f"compress {dirpath} to {outFullName} success")


def remove_spec_files(dir, suffix, recursive=False):
    """
    remove spec files in dir
    Args:
        dir (str): dir to remove spec files
        suffix (str): suffix of spec files, like "ui", "qrc"
        recursive (bool, optional): whether to remove spec files in sub dirs. Defaults to False.
    """
    for file in glob(os.path.join(dir, f"*.{suffix}"), recursive=recursive):
        os.remove(file)
        if os.path.exists(file):
            print(f"remove {file} failed")
        else:
            print(f"remove {file} success")


def copy_files(src_dir=script_dir, dir=build_dir):
    if os.getcwd() != src_dir:
        os.chdir(src_dir)
    target_dir = os.path.join(script_dir, dir)
    print("source dir:", os.getcwd())
    print("target dir:", target_dir)
    if os.path.exists(target_dir):
        print(f"found {dir} dir, remove it")
        shutil.rmtree(target_dir)
        print(f"remove old {dir} dir success")
    os.makedirs(target_dir)
    print(f"create new {dir} dir success")
    for file in files:
        shutil.copy(file, target_dir)
        print(f"copy {file} to {target_dir} success")
    for folder in src_folders:
        if os.path.isdir(folder):
            shutil.copytree(folder, os.path.join(target_dir, folder))
            print(f"copy {folder} to {target_dir} dir success")
    reflush_txt_version(target_dir)
    return target_dir


def gen_ui(dir=script_dir):
    """
    run:  pyside6-uic form.ui -o form_ui.py
    :param target_dir: pwd
    """
    cmd = ["pyside6-uic", "--from-imports", "form.ui", "-o", "form_ui.py"]
    p = subprocess.Popen(cmd, cwd=dir)
    p.wait()
    if p.returncode == 0:
        print("generate qt ui file success")
        return True
    else:
        print("generate qt ui file failed")
        return False


def gen_rc(dir=script_dir):
    """
    run:  pyside6-rcc resource.qrc -o resource_rc.py
    :param target_dir: pwd
    """
    cmd = ["pyside6-rcc", "resource.qrc", "-o", "resource_rc.py"]
    p = subprocess.Popen(cmd, cwd=dir)
    p.wait()
    if p.returncode == 0:
        print("generate qt rc file success")
        return True
    else:
        print("generate qt rc file failed")
        return False


def pybuild_dir(dir=os.path.join(script_dir, build_dir), hd=False):
    """
    run:  pyinstaller --contents-directory . --windowed --add-data "translations/*.qm:translations" --icon "image/curve.ico" --name PyCFF --exclude PyQt6 application.py
    :param target_dir: pwd
    :param hd: hidden import
    """
    cmd = [
        "pyinstaller",
        "--contents-directory",
        ".",
        "--windowed",
        "--add-data",
        "translations/*.qm:pycff/translations",
        "--icon",
        "image/curve.ico",
        "--name",
        app_name,
        "--exclude",
        "PyQt6",
        "--version-file",
        "../file-version-info.txt",
        "__main__.py",
    ]
    if hd:
        pyfile = cmd[-1]
        cmd = cmd[:-1]
        for hd in hd_list:
            cmd.append("--hidden-import")
            cmd.append(hd)
        cmd.append(pyfile)
    p = subprocess.Popen(cmd, cwd=dir)
    p.wait()
    if p.returncode == 0:
        print("pyinstaller build in one dir success")
        return True
    else:
        print("pyinstaller build in one dir failed")
        return False


def pybuild_one(dir=os.path.join(script_dir, build_dir), hd=False):
    """
    run:  pyinstaller --onefile --windowed --add-data "translations/*.qm:translations" --icon "image/curve.ico" --name PyCFF --exclude PyQt6 application.py
    :param target_dir: pwd
    :param hd: hidden import
    """
    cmd = [
        "pyinstaller",
        "--onefile",
        "--windowed",
        "--add-data",
        "translations/*.qm:pycff/translations",
        "--icon",
        "image/curve.ico",
        "--name",
        exe_name,
        "--exclude",
        "PyQt6",
        "--version-file",
        "../file-version-info.txt",
        "__main__.py",
    ]
    if hd:
        pyfile = cmd[-1]
        cmd = cmd[:-1]
        for hd in hd_list:
            cmd.append("--hidden-import")
            cmd.append(hd)
        cmd.append(pyfile)
    p = subprocess.Popen(cmd, cwd=dir)
    p.wait()
    if p.returncode == 0:
        print("pyinstaller build in one file success")
        return True
    else:
        print("pyinstaller build in one file failed")
        return False


def translations_update(dir=script_dir):
    """
    update translations(.ts) files
    run:  lupdate widget.py form.ui -ts translations/PyCFF_${locale}.ts -no-obsolete
    :param target_dir: pwd
    """
    r = False
    for loc in locale:
        cmd = []
        cmd.append("pyside6-lupdate")
        for f in trans_files:
            cmd.append(f)
        cmd.append("-ts")
        cmd.append(f"translations/PyCFF_{loc}.ts")
        cmd.append("-no-obsolete")
        p = subprocess.Popen(cmd, cwd=dir)
        p.wait()
        if p.returncode == 0:
            print(f"update translations for {loc} success")
            r = True
        else:
            print(f"update translations for {loc} failed")
            r = False
            return r
    return r


def translations_linguist(dir=script_dir):
    """
    open linguist to deal with translations(.ts) files
    run:  linguist translations/PyCFF_${locale}.ts
    :param target_dir: pwd
    """
    cmd = ["pyside6-linguist"]
    ts_files = glob(os.path.join(dir, "translations", "*.ts"))
    for ts_file in ts_files:
        cmd.append(ts_file)
        print(f"Found translation file: {ts_file}")
    p = subprocess.Popen(cmd, cwd=dir)
    p.wait()
    return p == 0


def translations_gen(dir=script_dir):
    """
    use lrelease to convert .ts files to *.qm files
    run:  lrelease translations/PyCFF_${locale}.ts -qm translations/PyCFF_${locale}.qm
    :param target_dir: pwd
    """
    ts_files = glob(os.path.join(dir, "translations", "*.ts"))
    r = False
    for ts_file in ts_files:
        cmd = ["pyside6-lrelease"]
        cmd.append(ts_file)
        cmd.append("-qm")
        cmd.append(ts_file.replace(".ts", ".qm"))
        print(f"Found translation file: {ts_file}")
        p = subprocess.Popen(cmd, cwd=dir)
        p.wait()
        if p.returncode == 0:
            print(f"generate translations for {ts_file} success")
            r = True
        else:
            print(f"generate translations for {ts_file} failed")
            r = False
            return r
    return r


def gen_pyd(
    dir=os.path.join(script_dir, build_dir), pyexecutable=sys.executable, del_src=True
):
    """
    run:  python compile.py build_ext --inplace
    :param target_dir: pwd
    :param pyexecutable: python executable
    :param del_src: delete source files
    """
    cmd = [
        pyexecutable,
        "compile.py",
        "build_ext",
        "--inplace",
    ]
    p = subprocess.Popen(cmd, cwd=dir)
    p.wait()

    if p.returncode == 0:
        print("generate pyd file success")
        if sys.platform.startswith("win"):
            pyd_ext = ".pyd"
        else:
            pyd_ext = ".so"
        if del_src:
            for pyd_file in glob(os.path.join(dir, src_folders[0], f"*{pyd_ext}")):
                match = re.match(
                    r"^(.*?)(?:\..*)?%s$" % re.escape(pyd_ext),
                    os.path.basename(pyd_file),
                )
                if match:
                    base = match.group(1)
                    py_file = os.path.join(dir, src_folders[0], base + ".py")
                    c_file = os.path.join(dir, src_folders[0], base + ".c")
                    for f in [py_file, c_file]:
                        if os.path.exists(f):
                            os.remove(f)
                            print(f"delete {f} success")
        return True
    else:
        print("generate pyd file failed")
        return False


def gen_whl(dir=os.path.join(script_dir, build_dir), pyexecutable=sys.executable):
    """
    run:  python setup.py bdist_wheel
    :param target_dir: pwd
    :param pyexecutable: python executable
    """
    # check platform
    system = platform.system().lower()
    machine = platform.machine().lower()
    if system == "windows":
        plat_name = f"win_{machine}"
    elif system == "darwin":
        plat_name = f"macosx_{machine}"
    elif system == "linux":
        plat_name = f"manylinux_{machine}"
    else:
        plat_name = "any"
    # create wheel
    cmd = [pyexecutable, "setup.py", "bdist_wheel", f"--plat-name={plat_name}"]
    p = subprocess.Popen(cmd, cwd=dir)
    p.wait()
    if p.returncode == 0:
        print("generate whl file success")
        return True
    else:
        print("generate whl file failed")
        return False


def get_version(dir=script_dir) -> str:
    """
    load version string from pyproject.toml
    """
    with open(os.path.join(dir, "pyproject.toml"), "rb") as f:
        data = tomllib.load(f)
    version = data["project"]["version"]
    return version


def reflush_txt_version(dir=script_dir, txtfile="file-version-info.txt"):
    """
    replace version string in file-version-info.txt
    """
    version = get_version(dir)
    with open(os.path.join(dir, txtfile), "r") as f:
        data = f.read()
    data = data.replace("AA.BB.CC.DD", version)
    v = version.split(".")
    if len(v) < 4:
        v.append("0")
    v_new = ",".join(v)
    data = data.replace("AA,BB,CC,DD", v_new)
    with open(os.path.join(dir, txtfile), "w") as f:
        f.write(data)
    print(f"replace version string in {txtfile} success")


if __name__ == "__main__":
    print("current dir:", script_dir)
    parser = argparse.ArgumentParser(description="PyCFF build tool")
    parser.add_argument(
        "-v",
        "--version",
        action="store_true",
        help="print app version.",
    )
    parser.add_argument(
        "-d",
        "--dir",
        metavar="DIR",
        # default=build_dir,
        help="specifying the working directory, default is [%s]." % build_dir,
    )
    parser.add_argument(
        "-b",
        "--build",
        nargs="?",
        const="dir",
        choices=["dir", "one"],
        help="build program, default [dir] means build in folder, [one] means build single executable file.",
    )
    parser.add_argument(
        "-u",
        "--update",
        action="store_true",
        help="generate/refresh qt interface(*.ui) and resource file(*.qrc) to python source.",
    )
    parser.add_argument(
        "-t",
        "--translate",
        nargs="?",
        const="up",
        choices=["up", "gui", "gen"],
        help="generate/refresh translations file, [up] means update .ts files(default), [ui] means launch linguist ui, [gen] means generate *.qm files.",
    )
    parser.add_argument(
        "-p",
        "--pyd",
        action="store_true",
        help="convert python source code to pyd file.",
    )
    args = parser.parse_args()

    if args.version:
        print(f"PyCFF version: {get_version()}")
        exit(0)

    def build_program(one=False, pyd=False, hd=False):
        dir = copy_files(dir=build_dir)
        if dir is None:
            print("error: copy files failed! ")
            exit(1)
        if gen_ui(os.path.join(dir, src_folders[0])) is False:
            print("error: gen ui failed! ")
            exit(1)
        else:
            remove_spec_files(os.path.join(dir, src_folders[0]), "ui")
        if gen_rc(os.path.join(dir, src_folders[0])) is False:
            print("error: gen rc failed! ")
            exit(1)
        else:
            remove_spec_files(os.path.join(dir, src_folders[0]), "qrc")
        if translations_gen(os.path.join(dir, src_folders[0])) is False:
            print("error: gen translations failed! ")
            exit(1)
        else:
            remove_spec_files(os.path.join(dir, src_folders[0], "translations"), "ts")
        if pyd:
            if gen_pyd(dir) is False:
                print("error: gen pyd failed! ")
                exit(1)
        if check_src_exists(os.path.join(dir, src_folders[0])) is False:
            print("error: check src files failed! ")
            exit(1)
        gen_whl(dir)
        if pyd:
            rename_whl(os.path.join(dir, "dist"))
        os.mkdir(os.path.join(dir, "pkg"))
        version = get_version(dir)
        system = platform.system().lower()
        machine = platform.machine().lower()
        if one:
            pybuild_one(os.path.join(dir, src_folders[0]), hd=hd)
            shutil.copy(
                os.path.join(dir, src_folders[0], "dist", exe_name),
                os.path.join(dir, "pkg", exe_name),
            )
            if system == "windows":
                shutil.move(
                    os.path.join(dir, "pkg", exe_name),
                    os.path.join(
                        dir, "pkg", app_name + f"-v{version}-{system}_{machine}.exe"
                    ),
                )
            else:
                shutil.move(
                    os.path.join(dir, "pkg", exe_name),
                    os.path.join(
                        dir, "pkg", app_name + f"-v{version}-{system}_{machine}.run"
                    ),
                )
        else:
            pybuild_dir(os.path.join(dir, src_folders[0]), hd=hd)
            if system == "windows":
                zip_dir(
                    os.path.join(dir, src_folders[0], "dist"),
                    os.path.join(
                        dir, "pkg", app_name + f"-v{version}-win_{machine}.zip"
                    ),
                )
            elif system == "linux":
                tar_xz_dir(
                    os.path.join(dir, src_folders[0], "dist"),
                    os.path.join(
                        dir, "pkg", app_name + f"-v{version}-linux_{machine}.tar.xz"
                    ),
                )
            elif system == "darwin":
                zip_dir(
                    os.path.join(dir, src_folders[0], "dist"),
                    os.path.join(
                        dir,
                        "pkg",
                        app_name + f"-v{version}-macosx_{machine}.zip",
                    ),
                )
            else:
                tar_xz_dir(
                    os.path.join(dir, src_folders[0], "dist"),
                    os.path.join(
                        dir,
                        "pkg",
                        app_name + f"-v{version}-unknown_{machine}.tar.xz",
                    ),
                )

    b_dir = args.dir is not None
    b_build = args.build is not None
    b_update = args.update
    b_translate = args.translate is not None
    b_pyd = args.pyd

    if b_update and b_translate:
        print("error: -u/--update and -t/--translate can not be used at the same time!")
        sys.exit(1)

    if b_build and (b_update or b_translate):
        print(
            "error: -b/--build and -u/--update or -t/--translate can not be used at the same time!"
        )
        sys.exit(1)

    if b_pyd and (not b_build):
        print("error: -p/--pyd can only be used with -b/--build!")
        sys.exit(1)

    if b_dir and (b_update or b_translate):
        print(
            "error: -d/--dir and -u/--update or -t/--translate can not be used at the same time!"
        )
        sys.exit(1)

    if b_dir and (not b_build):
        print("error: -d/--dir must be used with -b/--build!")
        sys.exit(1)

    if b_dir:
        if args.dir == build_dir:
            if os.path.exists(os.path.join(script_dir, args.dir)):
                shutil.rmtree(os.path.join(script_dir, args.dir))
                print(f"delete folder '{args.dir}' success")
        elif os.path.exists(args.dir):
            print(f"error: folder '{args.dir}' already exists!")
            sys.exit(1)
        else:
            build_dir = args.dir

    if b_translate:
        if args.translate == "up":
            translations_update(os.path.join(script_dir, src_folders[0]))
        elif args.translate == "gui":
            translations_linguist(os.path.join(script_dir, src_folders[0]))
        elif args.translate == "gen":
            translations_gen(os.path.join(script_dir, src_folders[0]))

    if b_update:
        gen_rc(os.path.join(script_dir, src_folders[0]))
        gen_ui(os.path.join(script_dir, src_folders[0]))

    if b_build:
        if args.build == "one":
            build_program(one=True, pyd=b_pyd, hd=b_pyd)
        else:
            build_program(one=False, pyd=b_pyd, hd=b_pyd)

    if not b_build and not b_translate and not b_update:
        parser.print_help()
