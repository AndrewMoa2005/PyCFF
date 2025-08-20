# -*- coding: utf-8 -*-

import os
import shutil
import subprocess
import argparse
import sys
import re
from glob import glob

pyexecutable = os.path.basename(sys.executable)
hd_list = [
    "PySide6.QtCharts",
    "PySide6.QtGui",
    "PySide6.QtSvg",
    "numpy",
    "scipy.optimize",
    "form_ui",
    "resource_rc",
    "clevertw",
    "cff",
]
locale = ["zh_CN", "en"]
trans_files = ["widget.py", "form.ui", "clevertw.py"]
script_dir = os.path.dirname(os.path.abspath(__file__))
files = [
    "setup.py",
    "pyproject.toml",
    "requirements.txt",
    "file-version-info.txt",
]
src_folders = ["pycff", "translations"]
build_dir = "py_build"


def copy_files(src_dir=script_dir, dir="py_build"):
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
    return target_dir


def gen_ui(dir=script_dir):
    """
    run:  pyside6-uic form.ui -o form_ui.py
    :param target_dir: pwd
    """
    cmd = ["pyside6-uic", "form.ui", "-o", "form_ui.py"]
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
    """
    cmd = [
        "pyinstaller",
        "--contents-directory",
        ".",
        "--windowed",
        "--add-data",
        "translations/*.qm:translations",
        "--icon",
        "image/curve.ico",
        "--name",
        "PyCFF",
        "--exclude",
        "PyQt6",
        "--version-file",
        "../file-version-info.txt",
        "application.py",
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
    """
    cmd = [
        "pyinstaller",
        "--onefile",
        "--windowed",
        "--add-data",
        "translations/*.qm:translations",
        "--icon",
        "image/curve.ico",
        "--name",
        "PyCFF",
        "--exclude",
        "PyQt6",
        "--version-file",
        "../file-version-info.txt",
        "application.py",
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
    run:  python setup.py build_ext --inplace
    :param target_dir: pwd
    """
    cmd = [
        pyexecutable,
        "setup.py",
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
            for pyd_file in glob(os.path.join(dir, f"*{pyd_ext}")):
                shutil.move(pyd_file, os.path.join(dir, src_folders[0]))
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


if __name__ == "__main__":
    print("current dir:", script_dir)
    parser = argparse.ArgumentParser(description="PyCFF build tool")
    parser.add_argument(
        "-c",
        "--copy",
        metavar="DIR",
        default=None,
        help="copy files to target build dir",
    )
    parser.add_argument(
        "-b",
        "--build",
        nargs="?",
        const="dir",
        choices=["dir", "one"],
        help="build program, default dir, one is single file",
    )
    parser.add_argument(
        "-u",
        "--update",
        action="store_true",
        help="generate/refresh qt interface and resource file",
    )
    parser.add_argument(
        "-t",
        "--translate",
        nargs="?",
        const="up",
        choices=["up", "gui", "gen"],
        help="generate/refresh translations file, up is update .ts files(default), ui is launch linguist ui, gen is generate *.qm files",
    )
    parser.add_argument(
        "-p",
        "--pyd",
        nargs="?",
        const="dir",
        choices=["dir", "one"],
        help="generate pyd file and build program, default dir, one is single file",
    )
    parser.add_argument(
        "-g",
        "--genpyd",
        action="store_true",
        help="generate/refresh pyd file in build dir (only test)",
    )
    args = parser.parse_args()

    def build_program(one=False, pyd=False, hd=False):
        dir = copy_files()
        if dir is None:
            print("error: copy files failed! ")
            exit(1)
        if gen_ui(os.path.join(dir, src_folders[0])) is False:
            print("error: gen ui failed! ")
            exit(1)
        if gen_rc(os.path.join(dir, src_folders[0])) is False:
            print("error: gen rc failed! ")
            exit(1)
        if translations_gen(os.path.join(dir, src_folders[0])) is False:
            print("error: gen translations failed! ")
            exit(1)
        if pyd:
            if gen_pyd(dir) is False:
                print("error: gen pyd failed! ")
                exit(1)
        if one:
            pybuild_one(os.path.join(dir, src_folders[0]), hd=hd)
        else:
            pybuild_dir(os.path.join(dir, src_folders[0]), hd=hd)

    if args.copy:
        # print("current dir:", script_dir)
        copy_files(dir=args.copy)
    elif args.build:
        if args.build == "one":
            build_program(one=True)
        else:
            build_program()
    elif args.update:
        gen_rc(os.path.join(script_dir, src_folders[0]))
        gen_ui(os.path.join(script_dir, src_folders[0]))
    elif args.translate:
        if args.translate == "up":
            translations_update(os.path.join(script_dir, src_folders[0]))
        elif args.translate == "gui":
            translations_linguist(os.path.join(script_dir, src_folders[0]))
        elif args.translate == "gen":
            translations_gen(os.path.join(script_dir, src_folders[0]))
    elif args.pyd:
        if args.pyd == "one":
            build_program(one=True, pyd=True, hd=True)
        else:
            build_program(pyd=True, hd=True)
    elif args.genpyd:
        dir = copy_files()
        if dir is None:
            print("error: copy files failed! ")
            exit(1)
        if gen_ui(os.path.join(dir, src_folders[0])) is False:
            print("error: gen ui failed! ")
            exit(1)
        if gen_rc(os.path.join(dir, src_folders[0])) is False:
            print("error: gen rc failed! ")
            exit(1)
        if translations_gen(os.path.join(dir, src_folders[0])) is False:
            print("error: gen translations failed! ")
            exit(1)
        if gen_pyd(dir) is False:
            print("error: gen pyd failed! ")
            exit(1)
    else:
        parser.print_help()
