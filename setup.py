# -*- coding: utf-8 -*-

from setuptools import setup
from Cython.Build import cythonize

setup(
    name="PyCFF",
    ext_modules=cythonize(["widget.py", "form_ui.py", "resource_rc.py", "clevertw.py", "cff.py"]),
    py_modules=["widget", "form_ui", "resource_rc", "clevertw", "cff"],
)
