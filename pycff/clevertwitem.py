# -*- coding: utf-8 -*-

# Used for floating point formatting to separate display and data.

from PySide6.QtWidgets import (
    QTableWidgetItem,
)
from PySide6.QtCore import Qt, qDebug
import numpy as np
import re
from .cff import parse_expression, pi, e


class CleverTableWidgetItem(QTableWidgetItem):
    def __init__(self, text: str = ""):
        """
        初始化CleverTableWidgetItem
        Args:
            text (str): 初始文本，默认空字符串
        """
        super().__init__(text)
        self._raw_data: str = None
        self.is_formula: bool = False
        self.formula: str = None
        self.args: list[str] = None
        self.result: str = None
        self.value: float = None
        self.setText(text)

    def label2index(self, label: str) -> tuple[int, int] | None:
        """
        将Excel风格的单元格标签转换为行列索引
        Args:
            label (str): Excel风格的单元格标签，如"A1", "B2"
        Returns:
            tuple[int, int] | None: 对应的行列索引（行, 列），如果标签无效则返回None
        """
        match = re.match(r"([A-Za-z]+)(\d+)", label)
        if not match:
            return None
        col_str, row_str = match.groups()
        col = 0
        for char in col_str.upper():
            col = col * 26 + (ord(char) - ord("A") + 1)
        col -= 1
        row = int(row_str) - 1  # 转换为0基索引
        return row, col

    def index2label(self, row: int, col: int) -> str | None:
        """
        将行列索引转换为Excel风格的单元格标签
        Args:
            row (int): 行索引，从0开始
            col (int): 列索引，从0开始
        Returns:
            str | None: 对应的Excel风格的单元格标签，如果索引无效则返回None
        """
        if row < 0 or col < 0:
            return None
        col_str = ""
        while col >= 0:
            col_str = chr(col % 26 + ord("A")) + col_str
            col = col // 26 - 1
        return f"{col_str}{row + 1}"

    def _calc_formula(self, text: str) -> tuple[str, float]:
        """
        解析公式文本，设置公式和参数
        Args:
            text (str): 公式文本，如"=A1+B2"
        Returns:
            str: 公式求解输出的字符串和值
        """
        if self.is_formula is False:
            return None
        try:
            self.formula, self.args = parse_expression(text.strip()[1:], False)
            qDebug(f"Parsed formula: {self.formula}, args: {self.args}")
        except Exception as e:
            self.result = f"#ERR: {e}"
            self.value = None
            return self.result, self.value
        calc_formula = str(self.formula)
        for arg in self.args:
            a = arg.upper()
            table = self.tableWidget()
            try:
                row, col = self.label2index(a)
            except Exception:
                self.result = f"#ERR: {a} is invalid"
                self.value = None
                return self.result, self.value
            if row == self.row() and col == self.column():
                self.result = f"#ERR: {a} is self-referencing"
                self.value = None
                return self.result, self.value
            qDebug(f"label2index({a}) = ({row}, {col})")
            item = table.item(row, col) if table else None
            if item is None:
                self.result = f"#ERR: {a} is empty"
                self.value = None
                return self.result, self.value
            try:
                self.value = float(item.text())
            except ValueError:
                self.result = f"#ERR: {a} is not a value"
                self.value = None
                return self.result, self.value
            calc_formula = calc_formula.replace(arg, str(self.value))
        try:
            self.value = eval(calc_formula)
            self.result = str(self.value)
        except Exception as e:
            self.result = f"#ERR: {e}"
            self.value = None
        return self.result, self.value

    def setText(self, text: str):
        self._raw_data = text
        if text.strip().startswith("="):
            self.is_formula = True
            display_text, _ = self._calc_formula(text)
            self.setDisplayText(text, display_text)
        else:
            self.is_formula = False
            self.formula = None
            self.args = None
            self.result = None
            self.value = None
            self.setDisplayText(text, text)

    def setDisplayText(self, edit_text: str, display_text: str):
        """
        设置编辑文本和显示文本
        Args:
            edit_text (str): 可编辑文本
            display_text (str): 显示文本
        """
        # 注意次序，这两个方法要一起调用，不然显示出错
        # 不知道Qt底层是怎么实现的，目前只能这样处理╮(╯▽╰)╭
        self.setData(Qt.EditRole, edit_text)
        self.setData(Qt.DisplayRole, display_text)

    def formulaResult(self) -> tuple[str, float] | None:
        """
        获取公式的计算结果
        Returns:
            tuple[str, float] | None: 公式计算结果的文本和值，如果不是公式则返回None
        """
        if self.is_formula:
            return self.result, self.value
        else:
            return None

    def text(self) -> str:
        """
        重载父类的text方法，获取可编辑文本
        考虑兼容性，没有增加公式判断，需要手动判断并获取公式文本
        Returns:
            str: 编辑文本
        """
        if self.is_formula:
            return self.result
        else:
            return self._raw_data

    def editText(self) -> str:
        """
        获取编辑文本
        Returns:
            str: 编辑文本
        """
        return self.data(Qt.EditRole)

    def formulaText(self) -> str | None:
        """
        获取重整后的公式文本（不包含等号）
        可以直接通过eval方法计算取值（需要import numpy并且重命名为np）
        一般不建议使用，建议通过rawText获取原始文本，通过text方法获取计算结果
        Returns:
            str | None: 公式文本，如果不是公式则返回None
        """
        if self.is_formula:
            return self.formula
        else:
            return None

    def rawText(self) -> str:
        """
        获取原始文本
        可以直接获取公式，不建议通过formulaText获取转换后的公式文本
        Returns:
            str: 原始文本
        """
        return self._raw_data

    def displayText(self):
        """
        获取显示文本
        Returns:
            str: 显示文本
        """
        return self.data(Qt.DisplayRole)
