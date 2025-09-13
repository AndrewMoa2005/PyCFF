# 语言

- zh_CN [简体中文](README.zh_CN.md)
- en [English](README.md)

# PyCFF
一款基于Python的曲线拟合函数工具

---

## 1. 软件简介

使用Python编写的一个简单程序，通过numpy和scipy实现函数拟合功能，用PySide编写了用户界面，实现了从输入数据到输出拟合函数参数的功能，并且支持数据预测和自定义函数功能。

源码地址：[PyCFF](https://github.com/AndrewMoa2005/PyCFF/)

## 2. 用户界面

软件界面通过Qt6(PySide6)实现。支持函数绘图功能，用户可以自定义绘图内容及输出保存图片。
![1.1-MainWindow-zh-cn.png](https://raw.githubusercontent.com/AndrewMoa2005/PyCFF/main/images/1.1-MainWindow-zh-cn.png)

## 3. 数据输入

软件通过Excel形式的表格输入数据，用户通过指定列来选择要拟合函数的自变量(x)和因变量(y)。用户不仅可以在表格中手动输入数据，也可以通过Excel等表格软件粘贴输入，还可以通过**粘贴替换列**的方式快速输入大量数据。表格数据支持公式运算，支持简单的函数运算(支持的函数见[自定义函数说明](#5.-自定义函数))。
![1.2-Input-zh-cn.png](https://raw.githubusercontent.com/AndrewMoa2005/PyCFF/main/images/1.2-Input-zh-cn.png)

## 4. 输出窗口

软件的输出界面通过表格和文本的形式展示输出函数的系数和表达式。软件预定义了一些常用函数，用户点击运算后在左侧表格中输出函数参数，并且在文本框中输出函数的完整表达式。用户可以自定义输出参数的精度和是否采用科学计数法，输出参数默认采用的是6位小数的科学计数法表示，满足大部分工程计算的需求。
![1.3-Output-zh-cn.png](https://raw.githubusercontent.com/AndrewMoa2005/PyCFF/main/images/1.3-Output-zh-cn.png)

## 5. 自定义函数

软件的预定义函数包括多项式、指数函数、对数函数及幂函数等，除了以上预定义函数也支持用户自定义函数。类似`a+b*x**1+c*x**2`、`-omega-alpha * exp(x)`等自定义函数，会自动提取其中的参数并通过输入数据进行拟合。
自定义函数除了四则运算(+、-、*、/)和幂运算(**或^)，还支持常用的函数运算，具体函数和相关说明见下表。

| 函数名 | 用法 | 说明 | 
|---|---|---|
| exp | exp(x) | 求x的指数值 |
| pow | pow(x, y) | 求x的y次幂 |
| abs | abs(x) | 求x的绝对值 |
| sqrt | sqrt(x) | 求x的平方根 |
| cbrt | cbrt(x) | 求x的立方根 |
| log | log(x) | 求x的对数(以e为底) |
| log10 | log10(x) | 求x的对数(以10为底) |
| log2 | log2(x) | 求x的对数(以2为底) |
| min | min(x) | 求x的最小值 |
| max | max(x) | 求x的最大值 |
| sin | sin(x) | 求x的正弦值 |
| cos | cos(x) | 求x的余弦值 |
| tan | tan(x) | 求x的正切值 |
| asin | asin(x) | 求x的反正弦 |
| acos | acos(x) | 求x的反余弦 |
| atan | atan(x) | 求x的反正切 |
| sinh | sinh(x) | 求x的双曲正弦值 |
| cosh | cosh(x) | 求x的双曲余弦值 |
| tanh | tanh(x) | 求x的双曲正切值 |
| asinh | asinh(x) | 求x的反双曲正弦 |
| acosh | acosh(x) | 求x的反双曲余弦 |
| atanh | atanh(x) | 求x的反双曲正切 |
| pi | pi() | 圆周率 |
| e | e() | 自然对数的底数 |

## 6. 发布说明

目前软件已经在Windows amd64和Linux x86-64平台通过测试和验证，MacOS和Linux Aarch64平台尚未经过完整测试。

## 7. 协议

本软件基于LGPL协议开源，您可以在遵守协议的前提下自由使用、修改和分发本软件。

## 8. 致谢

本软件的开发离不开以下项目的支持：

 - [PySide6](https://pypi.org/project/PySide6/)
 - [NumPy](https://numpy.org/)
 - [SciPy](https://scipy.org/)
 - [openpyxl](https://pypi.org/project/openpyxl/)
 - [xlrd](https://pypi.org/project/xlrd/)
 - [xlwt](https://pypi.org/project/xlwt/)

更多意见和建议，欢迎提交[Issues](https://github.com/AndrewMoa2005/PyCFF/issues)，也可以通过[Pull Requests](https://github.com/AndrewMoa2005/PyCFF/pulls)提交代码贡献。
