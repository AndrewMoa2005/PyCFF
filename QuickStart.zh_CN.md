# 语言

- zh_CN [简体中文](QuickStart.zh_CN.md)
- en [English](QuickStart.md)

# PyCFF - 快速上手

## 1. 输入

在`输入`标签进行数据输入操作。

 - 程序初始展示的是一个2×5大小的数据，除了可以通过顶部的输入栏输入数据以外，还可以通过双击单元格的方式输入数据。
   ![3.1-input-table](https://raw.githubusercontent.com/AndrewMoa2005/PyCFF/main/images/3.1-input-table.png)
 - 表格支持公式输入，通过类似Excel的标签"A1"、"B2"等方式索引其他单元格的数据，支持简单的函数运算。
 - 可以通过右键菜单拓展公式快速将公式拓展到其他单元格，避免重复手动录入带来的低效问题。
   ![3.1-input-expand-formula](https://raw.githubusercontent.com/AndrewMoa2005/PyCFF/main/images/3.1-input-expand-formula.png)
   ![3.1-input-expand-formula2](https://raw.githubusercontent.com/AndrewMoa2005/PyCFF/main/images/3.1-input-expand-formula2.png)
   ![3.1-input-expand-formula3](https://raw.githubusercontent.com/AndrewMoa2005/PyCFF/main/images/3.1-input-expand-formula3.png)
 - 可以通过复制粘贴excel表格获取数据，也可以通过读写文件(支持.csv、.xls及.xlsx格式)来加载/保存数据。
 - 可以通过右键菜单操作单元格，如复制、粘贴、删除、插入行/列等。
   ![3.1-input-right-clicked](https://raw.githubusercontent.com/AndrewMoa2005/PyCFF/main/images/3.1-input-right-clicked.png)
 - 可以通过右键菜单的“粘贴替换列”功能将剪贴板中的数据快速载入指定列中，自动按非数字字符分割，用于快速读取大量数据。
   ![3.1-input-right-clicked2](https://raw.githubusercontent.com/AndrewMoa2005/PyCFF/main/images/3.1-input-right-clicked2.png)
 - 数据录入完毕之后，通过右侧的复选框选择自变量(x)和因变量(y)对应的数据列，建议点击`刷新`按钮确保将表格数据载入。

## 2. 绘图

在`绘图`标签中进行简单的绘图操作。

 - 初始绘图展示的是前面2×5表格散点数据(红色实线段)和拟合曲线(黑色平滑虚线)。
 - 点击该标签中的`刷新`按钮，通过输入数据绘制散点图。
 - 可以自定义绘图标题、坐标轴标签和数字格式，以及曲线的标签、颜色、线型和粗细等参数。
   ![3.2-plot-setting](https://raw.githubusercontent.com/AndrewMoa2005/PyCFF/main/images/3.2-plot-setting.png)
 - 支持保存绘图，目前支持输出SVG和PNG格式文件。
 - 支持将绘图数据复制到剪贴板，可以快速粘贴到报告中。支持复制SVG和PNG格式的绘图数据。
   ![3.2-plot-copy](https://raw.githubusercontent.com/AndrewMoa2005/PyCFF/main/images/3.2-plot-copy.png)
 - 支持调整绘图大小，匹配报告文件要求。
   ![3.2-plot-size](https://raw.githubusercontent.com/AndrewMoa2005/PyCFF/main/images/3.2-plot-size.png)

## 3. 输出

在`输出`标签中进行函数拟合操作。

 - 在左侧顶部复选框中选择函数类型，预定义函数或者自定义函数。
   ![3.3-output-function](https://raw.githubusercontent.com/AndrewMoa2005/PyCFF/main/images/3.3-output-function.png)
 - 支持自定义函数，自动提取函数参数，通过非线性预测计算函数参数。
   ![3.3-output-custom-function](https://raw.githubusercontent.com/AndrewMoa2005/PyCFF/main/images/3.3-output-custom-function.png)
 - 点击右侧上方的`计算`按钮，在左侧表格中显示计算的函数参数和R<sup>2</sup>值，同时右侧文本框中显示完整的函数表达式。
 - 可以通过右侧顶部的复选框自定义显示参数的数字格式。
 - 计算出函数参数之后，点击`刷新`按钮，在`绘图`标签中绘制散点图和函数曲线对比，可以自定义函数曲线的细化程度。
 - 在底部的左右两组输入框，可以通过输入X值计算函数的Y值，或者通过给定Y值预测X值，用于数据预测。
   ![3.3-output-predict](https://raw.githubusercontent.com/AndrewMoa2005/PyCFF/main/images/3.3-output-predict.png)

## 4. 其他

增加了调整主题和配色的功能，不喜欢匹配系统默认主题和配色的小伙伴，可以通过这个功能选择自己喜欢的配色。
![3.4.change-theme](https://raw.githubusercontent.com/AndrewMoa2005/PyCFF/main/images/3.4-change-theme.png)

如果你喜欢这个软件，请不要吝啬您的小星星，请到[主页](https://github.com/AndrewMoa2005/PyCFF)里查看更多的信息。
