# -*- coding: utf-8 -*-

# reference: https://blog.csdn.net/weixin_40134371/article/details/138843448

import re
from PySide6.QtCore import Qt, Signal, Slot, qDebug
from PySide6.QtGui import QAction, QKeySequence, QShortcut, QColor
from PySide6.QtWidgets import (
    QTableWidget,
    QTableWidgetItem,
    QTableWidgetSelectionRange,
    QDialog,
    QVBoxLayout,
    QApplication,
    QMenu,
    QMessageBox,
    QGroupBox,
    QRadioButton,
    QPushButton,
    QHBoxLayout,
    QLabel,
    QSpinBox,
    QCheckBox,
    QInputDialog,
    QLineEdit,
)


class CleverTableWidget(QTableWidget):
    # 构造函数
    def __init__(self, parent=None, rowCount=0, columnCount=0, editable=True):
        super().__init__(parent, rowCount=rowCount, columnCount=columnCount)
        self.editable = editable
        if not self.editable:
            self.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.copy_action = QAction(self.tr("复制"), self)
        self.paste_action = QAction(self.tr("粘贴"), self)
        self.clear_action = QAction(self.tr("清空"), self)
        self.delete_action = QAction(self.tr("删除"), self)
        self.align_left_action = QAction(self.tr("左对齐"), self)
        self.align_right_action = QAction(self.tr("右对齐"), self)
        self.align_center_action = QAction(self.tr("居中对齐"), self)
        self.highlight_action = QAction(self.tr("高亮"), self)
        self.cancle_highlight_action = QAction(self.tr("取消高亮"), self)
        self.bold_action = QAction(self.tr("加粗"), self)
        self.cancle_bold_action = QAction(self.tr("取消加粗"), self)
        self.copy_action.triggered.connect(self.copy_selection)
        self.paste_action.triggered.connect(self.paste_selection)
        self.clear_action.triggered.connect(self.clear_selection)
        self.delete_action.triggered.connect(self.delete_selection)
        self.align_left_action.triggered.connect(self.align_left)
        self.align_right_action.triggered.connect(self.align_right)
        self.align_center_action.triggered.connect(self.align_center)
        self.highlight_action.triggered.connect(self.highlight_background(choice="Y"))
        self.cancle_highlight_action.triggered.connect(
            self.highlight_background(choice="T")
        )
        self.bold_action.triggered.connect(self.bold_text(choice="Y"))
        self.cancle_bold_action.triggered.connect(self.bold_text(choice="N"))
        # 移动操作
        self.move_up_action = QAction(self.tr("上移"), self)
        self.move_down_action = QAction(self.tr("下移"), self)
        self.move_left_action = QAction(self.tr("左移"), self)
        self.move_right_action = QAction(self.tr("右移"), self)
        self.move_up_action.triggered.connect(self.move_up)
        self.move_down_action.triggered.connect(self.move_down)
        self.move_left_action.triggered.connect(self.move_left)
        self.move_right_action.triggered.connect(self.move_right)
        if self.editable:
            self.move_up_action.setShortcut("Alt+Up")
            self.move_down_action.setShortcut("Alt+Down")
            self.move_left_action.setShortcut("Alt+Left")
            self.move_right_action.setShortcut("Alt+Right")
            QShortcut(QKeySequence("Alt+Up"), self).activated.connect(self.move_up)
            QShortcut(QKeySequence("Alt+Down"), self).activated.connect(self.move_down)
            QShortcut(QKeySequence("Alt+Left"), self).activated.connect(self.move_left)
            QShortcut(QKeySequence("Alt+Right"), self).activated.connect(
                self.move_right
            )
        # 排序、替换相关操作
        self.ascending_clo_action = QAction(self.tr("列升序"), self)
        self.descending_clo_action = QAction(self.tr("列降序"), self)
        self.reverse_clo_action = QAction(self.tr("列逆序"), self)
        self.paste_clo_action = QAction(self.tr("粘贴替换列"), self)
        self.float_clo_action = QAction(self.tr("上浮数字"), self)
        self.ascending_clo_action.triggered.connect(self.sort_clo_ascending)
        self.descending_clo_action.triggered.connect(self.sort_clo_descending)
        self.reverse_clo_action.triggered.connect(self.reverse_clo)
        self.paste_clo_action.triggered.connect(self.paste_clo)
        self.float_clo_action.triggered.connect(self.float_clo)
        if self.editable:
            self.ascending_clo_action.setShortcut("Alt+A")
            self.descending_clo_action.setShortcut("Alt+D")
            self.reverse_clo_action.setShortcut("Alt+R")
            self.paste_clo_action.setShortcut("Alt+V")
            self.float_clo_action.setShortcut("Alt+U")
            QShortcut(QKeySequence("Alt+A"), self).activated.connect(
                self.sort_clo_ascending
            )
            QShortcut(QKeySequence("Alt+D"), self).activated.connect(
                self.sort_clo_descending
            )
            QShortcut(QKeySequence("Alt+R"), self).activated.connect(self.reverse_clo)
            QShortcut(QKeySequence("Alt+V"), self).activated.connect(self.paste_clo)
            QShortcut(QKeySequence("Alt+U"), self).activated.connect(self.float_clo)
        # 设置浮点数的显示格式
        self.digital_format_action = QAction(self.tr("设置数字格式"), self)
        self.digital_format_action.triggered.connect(self.digital_format)
        # 列表转置
        self.transpose_action = QAction(self.tr("列表转置"), self)
        self.transpose_action.triggered.connect(self.transpose_table)
        # 设置快捷键
        self.copy_action.setShortcut("Ctrl+C")
        if self.editable:
            self.paste_action.setShortcut("Ctrl+V")
            self.clear_action.setShortcut("Ctrl+0")
            self.delete_action.setShortcut("Del")
        self.align_left_action.setShortcut("Ctrl+L")
        self.align_right_action.setShortcut("Ctrl+R")
        self.align_center_action.setShortcut("Ctrl+E")
        QShortcut(QKeySequence("Ctrl+C"), self).activated.connect(self.copy_selection)
        if self.editable:
            QShortcut(QKeySequence("Ctrl+V"), self).activated.connect(
                self.paste_selection
            )
            QShortcut(QKeySequence("Ctrl+0"), self).activated.connect(
                self.clear_selection
            )
            QShortcut(QKeySequence("Del"), self).activated.connect(
                self.delete_selection
            )
        QShortcut(QKeySequence("Ctrl+L"), self).activated.connect(self.align_left)
        QShortcut(QKeySequence("Ctrl+R"), self).activated.connect(self.align_right)
        QShortcut(QKeySequence("Ctrl+E"), self).activated.connect(self.align_center)
        self.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.customContextMenuRequested.connect(self.showContextMenu)
        if self.editable:
            # 设置双击可编辑表头
            self.horizontalHeader().sectionDoubleClicked.connect(
                self.change_horizontal_header
            )
            self.verticalHeader().sectionDoubleClicked.connect(
                self.change_vertical_header
            )

    def disable_editing(self):
        self.editable = False
        self.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)

    def enable_editing(self):
        self.editable = True
        self.setEditTriggers(QTableWidget.EditTrigger.DoubleClicked)

    def change_horizontal_header(self, index):
        if self.editable is False:
            return
        item = self.horizontalHeaderItem(index)
        if item is None:
            val = self.model().headerData(index, Qt.Orientation.Horizontal)
            item = QTableWidgetItem(str(val))
            self.setHorizontalHeaderItem(index, item)
        old_header = item.text()
        new_header, ok_pressed = QInputDialog.getText(
            self,
            self.tr("设置列标题"),
            self.tr("请输入第%s列标题") % (index + 1),
            QLineEdit.EchoMode.Normal,
            old_header,
        )
        if ok_pressed:
            item.setText(new_header)

    def change_vertical_header(self, index):
        if self.editable is False:
            return
        item = self.verticalHeaderItem(index)
        if item is None:
            val = self.model().headerData(index, Qt.Orientation.Vertical)
            item = QTableWidgetItem(str(val))
            self.setVerticalHeaderItem(index, item)
        old_header = item.text()
        new_header, ok_pressed = QInputDialog.getText(
            self,
            self.tr("设置行标题"),
            self.tr("请输入第%s行标题") % (index + 1),
            QLineEdit.EchoMode.Normal,
            old_header,
        )
        if ok_pressed:
            item.setText(new_header)

    def showContextMenu(self, pos):
        menu = QMenu(self)
        align_menu = QMenu(self.tr("对齐方式"), self)
        insert_action = QAction(self.tr("插入"), self)
        insert_action_common = QAction(self.tr("插入"), self)
        insert_action_common.triggered.connect(self.insert_base_on_selection)
        menu.addAction(self.copy_action)
        if self.editable:
            menu.addAction(self.paste_action)
            menu.addAction(self.clear_action)
            menu.addAction(self.delete_action)
        align_menu.addAction(self.align_center_action)
        align_menu.addAction(self.align_left_action)
        align_menu.addAction(self.align_right_action)
        if self.editable:
            # 移动操作
            move_menu = QMenu(self.tr("移动单元格"), self)
            move_menu.addAction(self.move_up_action)
            move_menu.addAction(self.move_down_action)
            move_menu.addAction(self.move_left_action)
            move_menu.addAction(self.move_right_action)
            menu.addMenu(move_menu)
            # 插入操作
            selected = self.selectedRanges()
            if len(selected) == 0:
                return
            elif len(selected) > 1:  # 不支持多重选择场景
                return
            else:
                s = selected[0]
                srn = s.bottomRow() - s.topRow() + 1
                scn = s.rightColumn() - s.leftColumn() + 1
                if (
                    srn == self.rowCount()
                ):  # 选中区域行数等于表格最大行数, 选中整列, 向左侧插入新列
                    insert_action.triggered.connect(
                        self.insert_whole_base_on_selection(insert_type="C")
                    )
                    menu.addAction(insert_action)
                elif (
                    scn == self.columnCount()
                ):  # 选中区域列数等于表格最大列数, 选中整行, 向上方插入新行
                    insert_action.triggered.connect(
                        self.insert_whole_base_on_selection(insert_type="R")
                    )
                    menu.addAction(insert_action)
                else:
                    menu.addAction(insert_action_common)
        if self.editable:
            menu.addSeparator()
            menu.addAction(self.ascending_clo_action)
            menu.addAction(self.descending_clo_action)
            menu.addAction(self.reverse_clo_action)
            menu.addAction(self.paste_clo_action)
            menu.addAction(self.float_clo_action)
        menu.addSeparator()
        menu.addMenu(align_menu)
        menu.addAction(self.highlight_action)
        menu.addAction(self.bold_action)
        menu.addAction(self.cancle_highlight_action)
        menu.addAction(self.cancle_bold_action)
        menu.addSeparator()
        if self.editable:
            menu.addAction(self.digital_format_action)
        menu.addAction(self.transpose_action)
        menu.exec(self.viewport().mapToGlobal(pos))

    def move_up(self):
        if self.editable is False:
            return
        selected_ranges = self.selectedRanges()
        if not selected_ranges:
            return
        if len(selected_ranges) > 1:
            return
        top = selected_ranges[0].topRow()
        if top == 0:
            QMessageBox.warning(
                self,
                self.tr("警告"),
                self.tr("已到达顶部，无法向上移动"),
            )
            return
        left = selected_ranges[0].leftColumn()
        right = selected_ranges[0].rightColumn()
        bottom = selected_ranges[0].bottomRow()
        for clo in range(left, right + 1):
            for row in range(top, bottom + 1):
                item = self.takeItem(row, clo)
                if not item:
                    item = QTableWidgetItem().setText("")
                item_prev = self.takeItem(row - 1, clo)
                if not item_prev:
                    item_prev = QTableWidgetItem().setText("")
                self.setItem(row - 1, clo, item)
                self.setItem(row, clo, item_prev)
        self.clearSelection()
        self.setRangeSelected(
            QTableWidgetSelectionRange(top - 1, left, bottom - 1, right), True
        )

    def move_down(self):
        if self.editable is False:
            return
        selected_ranges = self.selectedRanges()
        if not selected_ranges:
            return
        if len(selected_ranges) > 1:
            return
        bottom = selected_ranges[0].bottomRow()
        if bottom == self.rowCount() - 1:
            self.insertRow(self.rowCount())
        top = selected_ranges[0].topRow()
        left = selected_ranges[0].leftColumn()
        right = selected_ranges[0].rightColumn()
        for clo in range(left, right + 1):
            for row in range(bottom, top - 1, -1):
                item = self.takeItem(row, clo)
                if not item:
                    item = QTableWidgetItem().setText("")
                item_next = self.takeItem(row + 1, clo)
                if not item_next:
                    item_next = QTableWidgetItem().setText("")
                self.setItem(row + 1, clo, item)
                self.setItem(row, clo, item_next)
        self.clearSelection()
        self.setRangeSelected(
            QTableWidgetSelectionRange(top + 1, left, bottom + 1, right), True
        )

    def move_left(self):
        if self.editable is False:
            return
        selected_ranges = self.selectedRanges()
        if not selected_ranges:
            return
        if len(selected_ranges) > 1:
            return
        left = selected_ranges[0].leftColumn()
        if left == 0:
            QMessageBox.warning(
                self,
                self.tr("警告"),
                self.tr("已到达最左侧，无法向左移动"),
            )
            return
        top = selected_ranges[0].topRow()
        right = selected_ranges[0].rightColumn()
        bottom = selected_ranges[0].bottomRow()
        for row in range(top, bottom + 1):
            for clo in range(left, right + 1):
                item = self.takeItem(row, clo)
                if not item:
                    item = QTableWidgetItem().setText("")
                item_prev = self.takeItem(row, clo - 1)
                if not item_prev:
                    item_prev = QTableWidgetItem().setText("")
                self.setItem(row, clo - 1, item)
                self.setItem(row, clo, item_prev)
        self.clearSelection()
        self.setRangeSelected(
            QTableWidgetSelectionRange(top, left - 1, bottom, right - 1), True
        )

    def move_right(self):
        if self.editable is False:
            return
        selected_ranges = self.selectedRanges()
        if not selected_ranges:
            return
        if len(selected_ranges) > 1:
            return
        right = selected_ranges[0].rightColumn()
        if right == self.columnCount() - 1:
            self.insertColumn(self.columnCount())
        top = selected_ranges[0].topRow()
        left = selected_ranges[0].leftColumn()
        bottom = selected_ranges[0].bottomRow()
        for row in range(top, bottom + 1):
            for clo in range(right, left - 1, -1):
                item = self.takeItem(row, clo)
                if not item:
                    item = QTableWidgetItem().setText("")
                item_next = self.takeItem(row, clo + 1)
                if not item_next:
                    item_next = QTableWidgetItem().setText("")
                self.setItem(row, clo + 1, item)
                self.setItem(row, clo, item_next)
        self.clearSelection()
        self.setRangeSelected(
            QTableWidgetSelectionRange(top, left + 1, bottom, right + 1), True
        )

    def digital_format(self):
        """
        在弹出对话框设置选中单元格的数字格式
        """

        class FormatDialog(QDialog):
            def __init__(self, parent=None):
                super().__init__(parent)
                self.setWindowTitle(self.tr("设置数字格式"))
                self.resize(300, 150)
                layout = QVBoxLayout(self)
                # 小数点位数
                hbox1 = QHBoxLayout()
                hbox1.addWidget(QLabel(self.tr("小数点位数:")))
                self.decimal_spin = QSpinBox()
                self.decimal_spin.setRange(0, 15)
                self.decimal_spin.setValue(2)
                hbox1.addWidget(self.decimal_spin)
                layout.addLayout(hbox1)
                # 科学计数法
                hbox2 = QHBoxLayout()
                self.sci_checkbox = QCheckBox(self.tr("使用科学计数法"))
                hbox2.addWidget(self.sci_checkbox)
                layout.addLayout(hbox2)
                # 精度提示
                self.warn_label = QLabel(self.tr("注意：格式化可能导致数值精度丢失"))
                self.warn_label.setStyleSheet("color: red;")
                layout.addWidget(self.warn_label)
                # 按钮
                btn_box = QHBoxLayout()
                self.ok_btn = QPushButton(self.tr("确定"))
                self.cancel_btn = QPushButton(self.tr("取消"))
                btn_box.addWidget(self.ok_btn)
                btn_box.addWidget(self.cancel_btn)
                layout.addLayout(btn_box)
                self.ok_btn.clicked.connect(self.accept)
                self.cancel_btn.clicked.connect(self.reject)

        dlg = FormatDialog(self)
        if dlg.exec() != QDialog.Accepted:
            return
        decimals = dlg.decimal_spin.value()
        use_sci = dlg.sci_checkbox.isChecked()
        selected = self.selectedRanges()
        top_row = selected[0].topRow()
        bottom_row = selected[0].bottomRow()
        left_column = selected[0].leftColumn()
        right_column = selected[0].rightColumn()
        for row in range(top_row, bottom_row + 1):
            for column in range(left_column, right_column + 1):
                item = self.item(row, column)
                if item:
                    try:
                        num = float(item.text())
                        if use_sci:
                            fmt = f"{{:.{decimals}e}}"
                        else:
                            fmt = f"{{:.{decimals}f}}"
                        item.setText(fmt.format(num))
                    except Exception:
                        continue

    def get_selected_columns_list(self):
        selected_items = self.selectedItems()
        selected_list = []
        for i in selected_items:
            if i.column() < 0 or i.column() >= self.columnCount():
                return
            selected_list.append(i.column())
        # remove duplicate elements
        selected_list = list(set(selected_list))
        return selected_list

    def sort_clo_ascending(self):
        if self.editable is False:
            return
        selected_list = self.get_selected_columns_list()
        if not selected_list:
            return
        for selected_column in selected_list:
            items = []
            for row in range(self.rowCount()):
                item = self.item(row, selected_column)
                if item:
                    items.append(item)

            def get_numeric_value(item):
                try:
                    return float(item.text())
                except ValueError:
                    return float("inf")

            items.sort(key=get_numeric_value)
            for row in range(self.rowCount()):
                self.takeItem(row, selected_column)
            for new_row, item in enumerate(items):
                self.setItem(new_row, selected_column, item)

    def sort_clo_descending(self):
        if self.editable is False:
            return
        self.sort_clo_ascending()
        self.reverse_clo()

    def reverse_clo(self):
        if self.editable is False:
            return
        selected_list = self.get_selected_columns_list()
        if not selected_list:
            return
        for selected_column in selected_list:
            items = []
            for row in range(self.rowCount()):
                item = self.item(row, selected_column)
                if item:
                    items.append(item)
            items = items[::-1]
            for row in range(self.rowCount()):
                self.takeItem(row, selected_column)
            for new_row, item in enumerate(items):
                self.setItem(new_row, selected_column, item)

    def filter_string_to_float_list(self, input_str: str) -> list:
        pattern = r"[-+]?\d+\.?\d*(?:[eE][-+]?\d+)?"
        matches = re.findall(pattern, input_str)
        output_list = []
        for num_str in matches:
            try:
                output_list.append(float(num_str))
            except ValueError:
                continue
        return output_list

    def paste_clo(self):
        """
        粘贴字符串中的数字到所选列，以任意非数字字符分隔
        """
        selected_list = self.get_selected_columns_list()
        if len(selected_list) != 1:
            QMessageBox.warning(
                self, self.tr("警告"), self.tr("只能选择一列进行粘贴替换操作")
            )
            return
        str_data = QApplication.clipboard().text()
        float_list = self.filter_string_to_float_list(str_data)
        if not float_list:
            QMessageBox.warning(
                self, self.tr("警告"), self.tr("粘贴数据中不包含有效数字字符")
            )
            return
        if len(float_list) > self.rowCount():
            self.setRowCount(len(float_list))
        clo = selected_list[0]
        for row in range(self.rowCount()):
            if row < len(float_list):
                item = QTableWidgetItem(str(float_list[row]))
                # item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                self.setItem(row, clo, item)
            else:
                self.setItem(row, clo, QTableWidgetItem(""))

    def float_clo(self):
        if self.editable is False:
            return
        selected_list = self.get_selected_columns_list()
        if not selected_list:
            return
        for clo in selected_list:
            number_list = []
            for row in range(self.rowCount()):
                item = self.item(row, clo)
                text = item.text() if item is not None else ""
                try:
                    float(text)
                except ValueError or AttributeError:
                    continue
                number_list.append(text)
            for row in range(self.rowCount()):
                if row < len(number_list):
                    item = QTableWidgetItem(str(number_list[row]))
                    self.setItem(row, clo, item)
                else:
                    self.setItem(row, clo, QTableWidgetItem(""))

    def clear_empty_row(self):
        """
        清除空行
        """
        if self.editable is False:
            return
        for row in range(self.rowCount() - 1, -1, -1):
            n = 0
            for clo in range(self.columnCount()):
                item = self.item(row, clo)
                text = item.text() if item is not None else ""
                if text in ["", " "]:
                    n += 1
                if n == self.columnCount():
                    self.removeRow(row)

    def clear_empty_col(self):
        """
        清除空列
        """
        if self.editable is False:
            return
        for clo in range(self.columnCount() - 1, -1, -1):
            n = 0
            for row in range(self.rowCount()):
                item = self.item(row, clo)
                text = item.text() if item is not None else ""
                if text in ["", " "]:
                    n += 1
                if n == self.rowCount():
                    self.removeColumn(clo)

    def clear_empty_space(self):
        """
        清除空行和空列
        """
        self.clear_empty_col()
        self.clear_empty_row()

    def transpose_table(self):
        """
        列表转置
        """
        self.clear_empty_space()
        if self.rowCount() == 0 or self.columnCount() == 0:
            QMessageBox.warning(
                self, self.tr("警告"), self.tr("表格为空，无法进行转置操作")
            )
            return

        def trans():
            for row in range(self.rowCount()):
                # 交换单元格
                for col in range(row + 1, self.columnCount()):
                    if row != col:
                        item_rc = self.takeItem(row, col)
                        item_cr = self.takeItem(col, row)
                        self.setItem(row, col, item_cr)
                        self.setItem(col, row, item_rc)
                # 交换表头
                head_col = self.takeHorizontalHeaderItem(row)
                head_row = self.takeVerticalHeaderItem(row)
                self.setHorizontalHeaderItem(row, head_row)
                self.setVerticalHeaderItem(row, head_col)

        if self.rowCount() == self.columnCount():
            trans()
        elif self.rowCount() > self.columnCount():
            self.setColumnCount(self.rowCount())
            trans()
        else:
            self.setRowCount(self.columnCount())
            trans()
        if not self.editable:
            self.enable_editing()
            self.clear_empty_space()
            self.disable_editing()
        else:
            self.clear_empty_space()

    def renumber_header_clo(self):
        """
        重编号列标题
        """
        if self.editable is False:
            return
        for clo in range(self.columnCount()):
            header = self.horizontalHeaderItem(clo)
            if header is None:
                header = QTableWidgetItem()
                self.setHorizontalHeaderItem(clo, header)
            header.setText(str(clo + 1))

    def renumber_header_row(self):
        """
        重编号行标题
        """
        if self.editable is False:
            return
        for row in range(self.rowCount()):
            header = self.verticalHeaderItem(row)
            if header is None:
                header = QTableWidgetItem()
                self.setVerticalHeaderItem(row, header)
            header.setText(str(row + 1))

    def renumber_header(self):
        """
        重编号列和行标题
        """
        self.renumber_header_clo()
        self.renumber_header_row()

    def get_first_empty_row_id(self):
        first_empty_row_id = 0
        for row in range(self.rowCount()):
            exist_item = False
            for column in range(self.columnCount()):
                if self.item(row, column) is not None and self.item(
                    row, column
                ).text() not in ["", " "]:
                    exist_item = True
                    break
            if not exist_item:
                return first_empty_row_id
            first_empty_row_id += 1
        return first_empty_row_id

    def read_table_context(self):
        context = [
            [
                self.item(row, col).text() if self.item(row, col) is not None else ""
                for col in range(self.columnCount())
            ]
            for row in range(self.rowCount())
        ]
        return context

    def _insert_add_row_helper(self, selected_top, selected_bottom):
        finaly_unempty_row_id = self.rowCount()
        end = False
        for row in sorted(range(self.rowCount()), reverse=True):
            finaly_unempty_row_id -= 1
            for column in range(selected_top, selected_bottom + 1):
                if self.item(row, column) is not None and self.item(
                    row, column
                ).text() not in ["", " "]:
                    end = True
                    break
            if end:
                break
        return finaly_unempty_row_id

    def _insert_add_col_helper(self, selected_left, selected_right):
        finaly_unempty_col_id = self.columnCount()
        end = False
        for column in sorted(range(self.columnCount()), reverse=True):
            finaly_unempty_col_id -= 1
            for row in range(selected_left, selected_right + 1):
                if self.item(row, column) is not None and self.item(
                    row, column
                ).text() not in ["", " "]:
                    end = True
                    break
            if end:
                break
        return finaly_unempty_col_id

    def _judge_rectangular_selected(self):
        selection = self.selectedRanges()
        if len(selection) != 1:
            return False
        return True

    def copy_selection(self):
        if not self._judge_rectangular_selected():
            return
        selected = self.selectedRanges()[0]
        text = "\n".join(
            [
                "\t".join(
                    [
                        (
                            self.item(row, col).text()
                            if self.item(row, col) is not None
                            else ""
                        )
                        for col in range(
                            selected.leftColumn(), selected.rightColumn() + 1
                        )
                    ]
                )
                for row in range(selected.topRow(), selected.bottomRow() + 1)
            ]
        )
        QApplication.clipboard().setText(text)

    def paste_selection(self):
        if self.editable is False:
            return
        if not self._judge_rectangular_selected():
            return
        selected = self.selectedRanges()[0]
        text = QApplication.clipboard().text()
        rows = text.split("\n")
        if "" in rows:
            rows.remove("")

        for r, row in enumerate(rows):
            if selected.topRow() + r >= self.rowCount():
                self.insertRow(selected.topRow() + r)
            cols = row.split("\t")
            for c, text in enumerate(cols):
                if selected.leftColumn() + c >= self.columnCount():
                    self.insertColumn(selected.leftColumn() + c)
                self.setItem(
                    selected.topRow() + r,
                    selected.leftColumn() + c,
                    QTableWidgetItem(text),
                )

    def clear_selection(self):
        if self.editable is False:
            return
        for item in self.selectedItems():
            self.setItem(item.row(), item.column(), QTableWidgetItem(""))

    def delete_selection(self):
        if self.editable is False:
            return
        if not self._judge_rectangular_selected():
            return
        delete_dialog = DeleteInsertDialog(dialog_type="delete")
        delete_dialog.DelSignal.connect(self._delete_operations)
        delete_dialog.setWindowModality(Qt.WindowModality.ApplicationModal)
        delete_dialog.exec()

    @Slot(str)
    def _delete_operations(self, message):
        selected = self.selectedRanges()[0]
        if message == "Move Left":
            selected_cols_num = selected.rightColumn() - selected.leftColumn() + 1
            start_col_index = selected.leftColumn() + selected_cols_num
            for col in range(start_col_index, self.columnCount() + selected_cols_num):
                ori_col = col - selected_cols_num
                for row in range(selected.topRow(), selected.bottomRow() + 1):
                    if col < self.columnCount():
                        text = (
                            self.item(row, col).text()
                            if self.item(row, col) is not None
                            else ""
                        )
                        self.setItem(row, ori_col, QTableWidgetItem(text))
                    else:
                        self.setItem(row, ori_col, QTableWidgetItem(""))
        elif message == "Move Up":
            selected_rows_num = selected.bottomRow() - selected.topRow() + 1
            start_row_index = selected.topRow() + selected_rows_num
            for row in range(start_row_index, self.rowCount() + selected_rows_num):
                ori_row = row - selected_rows_num
                for col in range(selected.leftColumn(), selected.rightColumn() + 1):
                    if row < self.rowCount():
                        text = (
                            self.item(row, col).text()
                            if self.item(row, col) is not None
                            else ""
                        )
                        self.setItem(ori_row, col, QTableWidgetItem(text))
                    else:
                        self.setItem(ori_row, col, QTableWidgetItem(""))
        elif message == "Delete Selected Rows":
            # 从最后一列开始删除，避免删除后索引变化
            for row in sorted(
                range(selected.topRow(), selected.bottomRow() + 1), reverse=True
            ):
                self.removeRow(row)
        elif message == "Delete Selected Cols":
            # 从最后一列开始删除，避免删除后索引变化
            for column in sorted(
                range(selected.leftColumn(), selected.rightColumn() + 1), reverse=True
            ):
                self.removeColumn(column)
        else:
            qDebug("Empty Message")

    def insert_whole_base_on_selection(self, insert_type):
        def insert():
            selected = self.selectedRanges()[0]
            if insert_type == "R":
                row_id = selected.topRow()
                for i in range(selected.bottomRow() - selected.topRow() + 1):
                    self.insertRow(row_id)
            elif insert_type == "C":
                col_id = selected.leftColumn()
                for i in range(selected.rightColumn() - selected.leftColumn() + 1):
                    self.insertColumn(col_id)

        return insert

    def insert_base_on_selection(self):
        if not self._judge_rectangular_selected():
            return
        insert_dialog = DeleteInsertDialog(dialog_type="insert")
        insert_dialog.InsertSignal.connect(self._insert_operations)
        insert_dialog.setWindowModality(Qt.WindowModality.ApplicationModal)
        insert_dialog.exec()

    @Slot(str)
    def _insert_operations(self, message):
        selected = self.selectedRanges()[0]
        if message == "Move Right":
            selected_cols_num = selected.rightColumn() - selected.leftColumn() + 1
            final_col = (
                self._insert_add_col_helper(selected.topRow(), selected.bottomRow())
                + 1
                + selected_cols_num
            )
            while self.columnCount() < final_col:
                self.insertColumn(self.columnCount())
            for col in sorted(range(selected.leftColumn(), final_col), reverse=True):
                ori_col = col - selected_cols_num
                for row in range(selected.topRow(), selected.bottomRow() + 1):
                    if col >= selected.leftColumn() + selected_cols_num:
                        text = (
                            self.item(row, ori_col).text()
                            if self.item(row, ori_col) is not None
                            else ""
                        )
                        self.setItem(row, col, QTableWidgetItem(text))
                    else:
                        self.setItem(row, col, QTableWidgetItem(""))
            qDebug("OK")
        elif message == "Move Down":
            selected_rows_num = selected.bottomRow() - selected.topRow() + 1
            final_row = (
                self._insert_add_row_helper(
                    selected.leftColumn(), selected.rightColumn()
                )
                + 1
                + selected_rows_num
            )
            while self.rowCount() < final_row:
                self.insertRow(self.rowCount())
            for row in sorted(range(selected.topRow(), final_row), reverse=True):
                ori_row = row - selected_rows_num
                for col in range(selected.leftColumn(), selected.rightColumn() + 1):
                    if row >= selected.topRow() + selected_rows_num:
                        text = (
                            self.item(ori_row, col).text()
                            if self.item(ori_row, col) is not None
                            else ""
                        )
                        self.setItem(row, col, QTableWidgetItem(text))
                    else:
                        self.setItem(row, col, QTableWidgetItem(""))
        elif message == "Insert Rows Above":
            self.insert_whole_base_on_selection("R")()
        elif message == "Insert Cols Left":
            self.insert_whole_base_on_selection("C")()
        else:
            qDebug("Empty Message")

    def _set_null_item(self):
        if not self._judge_rectangular_selected():
            return
        s = self.selectedRanges()[0]
        for row in range(s.topRow(), s.bottomRow() + 1):
            for col in range(s.leftColumn(), s.rightColumn() + 1):
                item = self.item(row, col)
                if item is None:
                    self.setItem(row, col, QTableWidgetItem(""))

    def align_right(self):
        self._set_null_item()
        for item in self.selectedItems():
            item.setTextAlignment(
                Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter
            )

    def align_left(self):
        self._set_null_item()
        for item in self.selectedItems():
            item.setTextAlignment(
                Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter
            )

    def align_center(self):
        self._set_null_item()
        for item in self.selectedItems():
            item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)

    def highlight_background(self, choice):
        def highlight_operation():
            self._set_null_item()
            yellow_bg = QColor(255, 255, 0)
            transparent_bg = QColor(255, 255, 255, 0)
            for item in self.selectedItems():
                if choice == "Y":
                    item.setBackground(yellow_bg)
                elif choice == "T":
                    item.setBackground(transparent_bg)
                else:
                    qDebug("highlight background error input")

        return highlight_operation

    def bold_text(self, choice):
        def bold_operation():
            self._set_null_item()
            for item in self.selectedItems():
                item_font = item.font()
                if choice == "Y":
                    item_font.setBold(True)
                    item.setFont(item_font)
                elif choice == "N":
                    item_font.setBold(False)
                    item.setFont(item_font)
                else:
                    qDebug("bold operation error input")

        return bold_operation

    @staticmethod
    def write_dim2_list_to_table(dim2_list, tablewidget_object):
        for row, dim1_list in enumerate(dim2_list):
            for col, text in enumerate(dim1_list):
                item = QTableWidgetItem(str(text))
                item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                tablewidget_object.setItem(row, col, item)

    def filter_operation(self, col, filter_list):
        for row in range(self.rowCount()):
            item = self.item(row, col)
            if item is not None and item.text() in filter_list:
                continue
            else:
                self.setRowHidden(row, True)


class DeleteInsertDialog(QDialog):
    DelSignal = Signal(str)
    InsertSignal = Signal(str)

    def __init__(self, dialog_type):
        super().__init__()
        self.dialog_type = dialog_type
        self.setWindowFlags(Qt.WindowType.Drawer | Qt.WindowType.WindowCloseButtonHint)
        self.dialog_typ_ch = (
            self.tr("删除") if dialog_type.lower() == "delete" else self.tr("插入")
        )
        self.setWindowTitle(self.dialog_typ_ch)
        self.resize(250, 150)
        # 1. 创建GroupBox
        self.groupBox = QGroupBox(self.dialog_typ_ch)
        self.groupBox.setFlat(True)
        # 1.1 创建RadioButton
        self.radioButtonA = QRadioButton()
        self.radioButtonB = QRadioButton()
        self.radioButtonC = QRadioButton()
        self.radioButtonD = QRadioButton()
        # 1.2 将RadioButton添加到GroupBox中
        gb_vbox = QVBoxLayout()
        gb_vbox.addWidget(self.radioButtonA)
        gb_vbox.addWidget(self.radioButtonB)
        gb_vbox.addWidget(self.radioButtonC)
        gb_vbox.addWidget(self.radioButtonD)
        self.groupBox.setLayout(gb_vbox)
        # 2. 创建确定和取消按钮
        self.buttonOK = QPushButton(self.tr("确定"))
        self.buttonCancel = QPushButton(self.tr("取消"))
        # 2.1 将按钮添加到水平布局中
        hbox = QHBoxLayout()
        hbox.addWidget(self.buttonOK)
        hbox.addWidget(self.buttonCancel)
        # 3. 将GroupBox和按钮添加到垂直布局中
        vbox = QVBoxLayout()
        vbox.addWidget(self.groupBox)
        vbox.addLayout(hbox)
        # 4. 设置对话框的布局
        self.setLayout(vbox)
        self.buttonCancel.clicked.connect(self.close)
        self._preperation()

    def _preperation(self):
        if self.dialog_type.lower() == "delete":
            # 1. 设置文本
            self.radioButtonA.setText(self.tr("右侧单元格左移(L)"))
            self.radioButtonB.setText(self.tr("下方单元格上移(U)"))
            self.radioButtonC.setText(self.tr("整行(R)"))
            self.radioButtonD.setText(self.tr("整列(C)"))

            # 2 设置热键
            QShortcut(QKeySequence("L"), self).activated.connect(
                self.radioButtonA.toggle
            )
            QShortcut(QKeySequence("U"), self).activated.connect(
                self.radioButtonB.toggle
            )
            QShortcut(QKeySequence("R"), self).activated.connect(
                self.radioButtonC.toggle
            )
            QShortcut(QKeySequence("C"), self).activated.connect(
                self.radioButtonD.toggle
            )

            self.buttonOK.clicked.connect(self.delete_button_ok_clicked)
        else:
            # 1. 设置文本
            self.radioButtonA.setText(self.tr("活动单元格右移(R)"))
            self.radioButtonB.setText(self.tr("活动单元格下移(D)"))
            self.radioButtonC.setText(self.tr("整行(R)"))
            self.radioButtonD.setText(self.tr("整列(C)"))

            # 2 设置热键
            QShortcut(QKeySequence("R"), self).activated.connect(
                self.radioButtonA.toggle
            )
            QShortcut(QKeySequence("D"), self).activated.connect(
                self.radioButtonB.toggle
            )
            QShortcut(QKeySequence("R"), self).activated.connect(
                self.radioButtonC.toggle
            )
            QShortcut(QKeySequence("C"), self).activated.connect(
                self.radioButtonD.toggle
            )

            self.buttonOK.clicked.connect(self.insert_button_ok_clicked)

    def delete_button_ok_clicked(self):
        if self.radioButtonA.isChecked():
            self.DelSignal.emit("Move Left")
        elif self.radioButtonB.isChecked():
            self.DelSignal.emit("Move Up")
        elif self.radioButtonC.isChecked():
            self.DelSignal.emit("Delete Selected Rows")
        elif self.radioButtonD.isChecked():
            self.DelSignal.emit("Delete Selected Cols")
        else:
            self.DelSignal.emit("")
        self.close()

    def insert_button_ok_clicked(self):
        if self.radioButtonA.isChecked():
            self.InsertSignal.emit("Move Right")
        elif self.radioButtonB.isChecked():
            self.InsertSignal.emit("Move Down")
        elif self.radioButtonC.isChecked():
            self.InsertSignal.emit("Insert Rows Above")
        elif self.radioButtonD.isChecked():
            self.InsertSignal.emit("Insert Cols Left")
        else:
            self.InsertSignal.emit("")
        self.close()


if __name__ == "__main__":
    """
    test CleverTW
    """
    import sys

    class TestUsingCleverTW(QDialog):
        def __init__(self, parent=None):
            super().__init__(parent)
            self.setWindowTitle(self.tr("Test Using CleverTableWidget"))
            self.setWindowFlags(
                Qt.WindowType.WindowMinimizeButtonHint
                | Qt.WindowType.WindowMaximizeButtonHint
                | Qt.WindowType.WindowCloseButtonHint
            )
            self.tableWidget = CleverTableWidget()
            self.tableWidget.setRowCount(10)
            self.tableWidget.setColumnCount(5)
            layout = QVBoxLayout()
            layout.addWidget(self.tableWidget)
            self.setLayout(layout)
            self.add_table_content()
            self.resize(700, 400)
            self.show()

        def add_table_content(self):
            for i in range(10):
                for j in range(5):
                    item = QTableWidgetItem("{}{}".format(i + 1, j + 1))
                    self.tableWidget.setItem(i, j, item)

    app = QApplication(sys.argv)
    ui = TestUsingCleverTW()
    ui.show()
    # ui.tableWidget.setHorizontalHeaderLabels(["A", "B", "C", "D", "E"])
    # ui.tableWidget.transpose_table()
    sys.exit(app.exec())
