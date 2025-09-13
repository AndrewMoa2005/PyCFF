# Languages

- en [English](README.md)
- zh_CN [简体中文](README.zh_CN.md)

# PyCFF
A Python-based curve fitting tool

---

## 1. Introduction

A simple program written in Python, which implements function fitting through numpy and scipy, and uses PySide to write the user interface. It implements the function of fitting function parameters from input data to output, and supports data prediction and custom function functions.

Repository：[PyCFF](https://github.com/AndrewMoa2005/PyCFF/)

## 2. User Interface

The software interface is implemented using Qt6 (PySide6). It supports function drawing, allowing users to customize drawing content and save output images.
![1.1-MainWindow-en.png](./images/1.1-MainWindow-en.png)

## 3. Input data

The software uses Excel spreadsheets for data input. Users select the independent variable (x) and dependent variable (y) to fit the function by specifying columns. Data can be entered manually or pasted from spreadsheet software like Excel. The **Paste Replace Column** method allows for rapid data entry. Tabular data supports formula operations and simple function calculations (see [Custom Function Description](#5.-Custom-Functions) for supported functions).
![1.2-Input-en.png](./images/1.2-Input-en.png)

## 4. Output Window

The software's output interface displays the coefficients and expressions of the output function in both table and text format. The software pre-defines some common functions. Selecting a function displays the function parameters in the table on the left and the complete function expression in the text box. Users can customize the precision of the output parameters and whether to use scientific notation. The default setting is scientific notation with six decimal places, which meets the needs of most engineering calculations.
![1.3-Output-en.png](./images/1.3-Output-en.png)

## 5. Custom Functions

The software includes predefined functions such as polynomials, exponentials, logarithms, and power functions. In addition to these predefined functions, the software also supports user-defined functions. Custom functions such as `a+b*x**1+c*x**2` and `-omega-alpha * exp(x)` automatically extract their parameters and fit them to the input data. 
Custom functions support not only the four arithmetic operations (+, -, *, /) and power operations (** or ^), but also common functions. See the table below for specific functions and their descriptions.

| Function | Usage | Description |
|---|---|---|
| exp | exp(x) | Calculates the exponential value of x |
| pow | pow(x, y) | Calculates x raised to the power of y |
| abs | abs(x) | Calculates the absolute value of x |
| sqrt | sqrt(x) | Calculates the square root of x |
| cbrt | cbrt(x) | Calculates the cube root of x |
| log | log(x) | Calculates the base e logarithm of x |
| log10 | log10(x) | Calculates the base 10 logarithm of x |
| log2 | log2(x) | Calculates the base 2 logarithm of x |
| min | min(x) | Calculates the minimum value of x |
| max | max(x) | Calculates the maximum value of x |
| sin | sin(x) | Calculates the sine of x |
| cos | cos(x) | Calculates the cosine of x |
| tan | tan(x) | Calculates the tangent of x |
| asin | asin(x) | Calculates the inverse sine of x |
| acos | acos(x) | Calculates the inverse cosine of x |
| atan | atan(x) | Calculates the inverse tangent of x |
| sinh | sinh(x) | Calculates the hyperbolic sine of x |
| cosh | cosh(x) | Calculates the hyperbolic cosine of x |
| tanh | tanh(x) | Calculates the hyperbolic tangent of x |
| asinh | asinh(x) | Calculates the inverse hyperbolic sine of x |
| acosh | acosh(x) | Calculates the inverse hyperbolic cosine of x |
| atanh | atanh(x) | Calculates the inverse hyperbolic tangent of x |
| pi | pi() | Pi |
| e | e() | Base of natural logarithms |

## 6. Release Notes

Currently, this application has been tested and verified on Windows amd64 and Linux x86-64 platforms, but has not yet been fully tested on MacOS and Linux Aarch64 platforms.

## 7. License

This software is open source under the LGPL license, and you are free to use, modify and distribute it under the terms of the license.

## 8. Acknowledgements

The development of this software relies on the following projects:

 - [PySide6](https://pypi.org/project/PySide6/)
 - [NumPy](https://numpy.org/)
 - [SciPy](https://scipy.org/)
 - [openpyxl](https://pypi.org/project/openpyxl/)
 - [xlrd](https://pypi.org/project/xlrd/)
 - [xlwt](https://pypi.org/project/xlwt/)

For more suggestions and feedback, please submit [Issues](https://github.com/AndrewMoa2005/PyCFF/issues). You can also contribute code via [Pull Requests](https://github.com/AndrewMoa2005/PyCFF/pulls).
