# -*- coding: utf-8 -*-

from setuptools import setup

# read the contents of your README file
from pathlib import Path

pwd = Path(__file__).parent
ld = (pwd / "README.md").read_text()

setup(
    name="PyCFF",
    version="1.1.5",
    packages=["pycff"],
    install_requires=[
        "numpy>=1.26.0",
        "scipy>=1.12.0",
        "pyside6>=6.6.0",
    ],
    description="A function fitting tool",
    # long_description=ld,
    # long_description_content_type="text/markdown",
    url="https://github.com/AndrewMoa2005/PyCFF",
    author="Andrew Moa",
    author_email="Andrew.Moa2005@163.com",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Software Development :: Applications :: Python",
    ],
    license="LGPL-3.0-or-later",
    keywords=["PySide6", "application", "widget"],
    include_package_data=True,
    entry_points={
        "gui_scripts": [
            "pycff = pycff.__main__:main",
        ]
    },
)
