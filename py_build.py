import os
import shutil
import subprocess
import argparse
import sys
import re
from glob import glob

vcpkg_qt6_tools_path = r"D:/vcpkg/installed/x64-windows/tools/Qt6/bin"
pyexecutable = os.path.basename(sys.executable)
hd_list = [
    "PySide6.QtCharts",
    "PySide6.QtGui",
    "PySide6.QtSvg",
    "numpy",
    "scipy.optimize",
    "csv",
    "re",
    "form_ui",
    "resource_rc",
]
script_dir = os.path.dirname(os.path.abspath(__file__))
files = ["application.py", "widget.py", "setup.py", "form.ui", "resource.qrc"]
folders = ["image", "translations"]
build_dir = "py_build"


def copy_files(src_dir=script_dir, dir="py_build"):
    if os.getcwd() != src_dir:
        os.chdir(src_dir)
    target_dir = os.path.join(script_dir, dir)
    print("source dir:", os.getcwd())
    print("target dir:", target_dir)
    if os.path.exists(target_dir):
        print("found build dir, remove it")
        shutil.rmtree(target_dir)
        print("remove old build dir success")
    os.makedirs(target_dir)
    print("create new build dir success")
    for file in files:
        shutil.copy(file, target_dir)
        print(f"copy {file} to {target_dir} success")
    for folder in folders:
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


def update_translations(dir=script_dir):
    """
    run:  lupdate widget.py form.ui -ts translations/PyCFF_${locale}.ts
    :param target_dir: pwd
    """
    if shutil.which("lupdate") is None:
        os.environ["PATH"] = vcpkg_qt6_tools_path + ";" + os.environ["PATH"]
        print("add Qt6 bin path to PATH")
    else:
        print("lupdate already exists in PATH")
    files = ("widget.py", "form.ui")
    locale = ("zh_CN", "en")
    for loc in locale:
        cmd = []
        cmd.append("lupdate")
        for f in files:
            cmd.append(f)
        cmd.append("-ts")
        cmd.append(f"translations/PyCFF_{loc}.ts")
        p = subprocess.Popen(cmd, cwd=dir)
        p.wait()
        if p.returncode == 0:
            print(f"update translations for {loc} success")
            return True
        else:
            print(f"update translations for {loc} failed")
            return False


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
                match = re.match(
                    r"^(.*?)(?:\..*)?%s$" % re.escape(pyd_ext),
                    os.path.basename(pyd_file),
                )
                if match:
                    base = match.group(1)
                    py_file = os.path.join(dir, base + ".py")
                    c_file = os.path.join(dir, base + ".c")
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
        "-c", "--copy", metavar="DIR", default=None, help="copy files to dir"
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
        help="generate/refresh qt ui and resource file",
    )
    parser.add_argument(
        "-t",
        "--translate",
        action="store_true",
        help="generate/refresh translations file",
    )
    parser.add_argument(
        "-p",
        "--pyd",
        nargs="?",
        const="dir",
        choices=["dir", "one"],
        help="generate pyd file and build program, default dir, one is single file",
    )
    args = parser.parse_args()

    def build_program(one=False, pyd=False, hd=False):
        dir = copy_files()
        if dir is None:
            print("error: copy files failed! ")
            exit(1)
        gen_ui(dir)
        gen_rc(dir)
        if pyd:
            gen_pyd(dir)
        if one:
            pybuild_one(dir, hd=hd)
        else:
            pybuild_dir(dir, hd=hd)

    if args.copy:
        # print("current dir:", script_dir)
        copy_files(dir=args.copy)
    elif args.build:
        if args.build == "one":
            build_program(one=True)
        else:
            build_program()
    elif args.update:
        gen_ui()
        gen_rc()
    elif args.translate:
        update_translations()
    elif args.pyd:
        if args.pyd == "one":
            build_program(one=True, pyd=True, hd=True)
        else:
            build_program(pyd=True, hd=True)
    else:
        parser.print_help()
