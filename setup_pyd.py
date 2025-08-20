# -*- coding: utf-8 -*-

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
            "pycff/cff.py",
            "pycff/application.py",
        ]
    ),
    py_modules=[
        "pycff.widget",
        "pycff.form_ui",
        "pycff.resource_rc",
        "pycff.clevertw",
        "pycff.cff",
        "pycff.application",
    ],
)
