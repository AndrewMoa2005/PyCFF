# -*- coding: utf-8 -*-
# compile specified python source (.py files) to binary module(.pyd files in windows or.so files in others)
# usage: python compile.py build_ext --inplace

from setuptools import setup
from Cython.Build import cythonize

setup(
    name="PyCFF",
    ext_modules=cythonize(
        [
            "pycff/widget.py",
            "pycff/form_ui.py",
            "pycff/resource_rc.py",
            "pycff/clevertw.py",
            "pycff/clevertwitem.py",
            "pycff/cff.py",
            "pycff/application.py",
        ]
    ),
    py_modules=[
        "pycff.widget",
        "pycff.form_ui",
        "pycff.resource_rc",
        "pycff.clevertw",
        "pycff.clevertwitem",
        "pycff.cff",
        "pycff.application",
    ],
)
