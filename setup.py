# file: setup.py
from setuptools import setup
from Cython.Build import cythonize

setup(
    name="PyCFF",
    ext_modules=cythonize(
        ["widget.py", "form_ui.py", "resource_rc.py"]
    ),
    py_modules=["widget", "form_ui", "resource_rc"],
)
