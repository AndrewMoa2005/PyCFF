# 语言

- zh_CN [简体中文](INSTALL.zh_CN.md)
- en [English](INSTALL.md)

# PyCFF - 安装说明

## 1. 快速安装

软件已经上传PyPI，支持通过pip命令安装:
```bash
python -m pip install pycff
````

也可以在[Release](https://github.com/AndrewMoa2005/PyCFF/releases)页面找到对应平台的二进制包，解压即可运行。

## 2. 构建环境

构建依赖：
 - Python >= 3.12
 - Git (可选) ： 构建时更新版本号
 - C/C++ Compiler (可选) ： 仅在构建pyd/so文件时需要

源代码提供了`build.py`脚本方便快速构建，用户构建前应先建立虚拟环境：
```bash
python -m venv myvenv # myvenv 为虚拟环境名称，根据需要自己定义
```

Windows平台下通过以下命令激活虚拟环境：
```powershell
./myvenv/Scripts/activate # win环境下激活虚拟环境，建议在posershell中运行
```

Linux及其他Posix平台下通过以下命令激活虚拟环境：
```bash
source ./myvenv/bin/activate # posix环境下激活虚拟环境
```

激活虚拟环境之后会在命令行开头显示`(myvenv)`字符，表明此时命令行下的python运行在虚拟环境`myvenv`中。通过以下命令安装依赖：
```bash
pip install -r requirements.txt
```

构建完成后通过deactivate退出虚拟环境：
```bash
deactivate # win、posix都是同一个命令
```

## 3. 运行脚本构建

运行以下命令显示构建脚本的帮助信息：
```
python build.py -h
```

 - 开关`-h`/`--help`显示命令行帮助信息。
 - 开关`-v`/`--version`显示软件版本信息(需要安装Git)。
 - 开关`-d`/`--dir`输入构建目录名称，通常在源码目录下，默认为`build`。
 - 开关`-b`/`--build`生成`whl`文件同时运行`pyinstaller`将源码打包成可执行文件，`dir`表示打包成目录(默认情况)，`one`表示打包成单独的可执行文件。
 - 开关`-u`/`--update`将源文件中的`.ui`和`.qrc`编译成`.py`文件，用于调试。
 - 开关`-t`/`--translate`用于多语言翻译，`up`表示更新源码中的`.ts`文件，`gui`表示启动`linguistgui`界面并打开`.ts`文件，`gen`表示将`.ts`文件编译成`.qm`文件，此开关一般单独用于调试。
 - 开关`-p`/`--pyd`，是否将`.py`文件编译成`.pyd`/`.so`。

一般情况下，使用以下命令即可快速构建可执行程序：
```bash
python build.py -b
```
生成的可执行文件/压缩包在`[source_dir]/build/pkg`路径下，同时生成的whl文件位于`[source_dir]/build/dist`路径下。

生成whl文件后，通过以下命令安装({}里的内容取决于本地环境下的编译输出)：
```bash
pip install pycff-{version}-{python}-{abi}-{platform}_{machine}.whl
```
发布包安装后，可以通过`pycff`或者`python -m pycff`启动主程序。
