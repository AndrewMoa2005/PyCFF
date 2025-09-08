# -*- coding: utf-8 -*-

# Used for floating point formatting to separate display and data.

from PySide6.QtWidgets import (
    QTableWidgetItem,
)
from PySide6.QtCore import Qt


class CleverTableWidgetItem(QTableWidgetItem):
    def __init__(self, text: str = "", display_text: str = None):
        super().__init__(text)
        self._raw_data = text
        self.setData(Qt.EditRole, text)
        self.setData(Qt.DisplayRole, display_text if display_text is not None else text)

    def setText(self, text: str):
        self._raw_data = text
        self.setData(Qt.EditRole, text)

    def setDisplayText(self, text: str):
        self.setData(Qt.DisplayRole, text)

    def text(self):
        return self._raw_data

    def displayText(self):
        return self.data(Qt.DisplayRole)
