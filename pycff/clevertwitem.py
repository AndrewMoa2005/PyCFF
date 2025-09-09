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
    def __init__(self, text: str = "", display_text: str = None):
        super().__init__(text)
        self._raw_data: str = None
        self.setRawText(text)
        self.formula: str = None
        self.args: list[str] = None
        self.result: str = None
        if self.rawText().strip().startswith("="):
            self.is_formula: bool = True
            display_text = self._set_formula(self.rawText())
        else:
            self.is_formula: bool = False
        self.setDisplayText(
            display_text if display_text is not None else self._raw_data
        )

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

    def _set_formula(self, text: str) -> str:
        from .clevertw import CleverTableWidget as CTW

        if self.is_formula is False:
            return None
        try:
            self.formula, self.args = parse_expression(text.strip()[1:], False)
            qDebug(f"Parsed formula: {self.formula}, args: {self.args}")
        except Exception as e:
            self.result = f"#ERR: {e}"
            return self.result
        for arg in self.args:
            a = arg.upper()
            table: CTW = self.tableWidget()
            row, col = self.label2index(a)
            if row == self.row() and col == self.column():
                self.result = f"#ERR: {a} is self-referencing"
                return self.result
            qDebug(f"label2index({a}) = ({row}, {col})")
            item = table.item(row, col) if table else None
            if item is None:
                self.result = f"#ERR: {a} is empty"
                return self.result
            val = item.text()
            try:
                val = float(val)
            except ValueError:
                self.result = f"#ERR: {a} is not a value"
                return self.result
            self.formula = self.formula.replace(arg, str(val))
        try:
            self.result = str(eval(self.formula))
            return self.result
        except Exception as e:
            self.result = f"#ERR: {e}"
            return self.result

    def setText(self, text: str):
        self.setRawText(text)
        if self.rawText().strip().startswith("="):
            self.is_formula = True
            display_text = self._set_formula(self.rawText())
            self.setDisplayText(display_text)
        else:
            self.is_formula = False
            self.formula = None
            self.args = None
            self.result = None
            self.setDisplayText(text)
        self.setData(Qt.EditRole, self._raw_data)

    def setRawText(self, text: str):
        self._raw_data = text
        self.setData(Qt.EditRole, self._raw_data)

    def rawText(self):
        return self._raw_data

    def setDisplayText(self, text: str):
        self.setData(Qt.DisplayRole, text)

    def text(self):
        if self.is_formula:
            return self.result
        else:
            return self._raw_data

    def displayText(self):
        return self.data(Qt.DisplayRole)
