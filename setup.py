# -*- coding: utf-8 -*-

from setuptools import setup, find_packages

setup(
    name="PyCFF",
    version="1.1.4",
    packages=find_packages(),
    install_requires=[
        "numpy",
        "scipy",
        "pyside6",
    ],
    description="A function fitting tool",
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
)
