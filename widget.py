# -*- coding: utf-8 -*-

import re
import csv
import numpy as np
import scipy.optimize as opt

from PySide6.QtWidgets import (
    QWidget,
    QMessageBox,
    QTableWidgetItem,
    QFileDialog,
    QDialog,
    QFormLayout,
    QLabel,
    QSpinBox,
    QPushButton,
    QSizePolicy,
    QLineEdit,
    QColorDialog,
    QComboBox,
    QHBoxLayout,
)
from PySide6.QtCharts import (
    QChart,
    QChartView,
    QLineSeries,
    QSplineSeries,
    QValueAxis,
)
from PySide6.QtGui import (
    QPainter,
    QPen,
    QColor,
)
from PySide6.QtCore import (
    Qt,
    QSize,
    QRect,
    qDebug,
)
from PySide6.QtSvg import QSvgGenerator

# Important:
# You need to run the following command to generate the ui_form.py file
#     pyside6-uic form.ui -o form_ui.py, or
#     pyside2-uic form.ui -o form_ui.py
from form_ui import Ui_Widget


class Widget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.ui = Ui_Widget()
        self.ui.setupUi(self)
        self.setWindowTitle(self.tr("拟合函数曲线"))
        # Connect signals to slots
        self.ui.aboutBtn.clicked.connect(self.onAboutBtnClicked)
        self.ui.qtBtn.clicked.connect(self.onQtBtnClicked)
        self.ui.plotBtn.clicked.connect(self.onPlotBtnClicked)
        self.ui.setPlotSizeBtn.clicked.connect(self.onSetPlotSizeBtn)
        self.ui.adjustPlotBtn.clicked.connect(self.onAdjustPlotBtnClicked)
        self.ui.savePlotBtn.clicked.connect(self.onSavePlotBtnClicked)
        self.ui.setPlotBtn.clicked.connect(self.onSetPlotBtnClicked)
        self.ui.loadBtn.clicked.connect(self.onLoadBtnClicked)
        self.ui.saveBtn.clicked.connect(self.onSaveBtnClicked)
        self.ui.refreshBtn.clicked.connect(self.onRefreshBtnClicked)
        self.ui.transBtn.clicked.connect(self.onTransBtnClicked)
        self.ui.fitBtn.clicked.connect(self.onFitBtnClicked)
        self.ui.curveBtn.clicked.connect(self.onCurveBtnClicked)
        self.ui.calcYOut.clicked.connect(self.onCalcYOutClicked)
        self.ui.calcXOut.clicked.connect(self.onCalcXOutClicked)
        self.ui.comboBox.currentIndexChanged.connect(self.onComboBoxChanged)
        self.ui.outputTable.disable_editing()
        self.ui.rowSpin.valueChanged.connect(self.onRowSpinChanged)
        self.ui.colSpin.valueChanged.connect(self.onColSpinChanged)
        self.ui.xDataBox.activated.connect(self.onXDataBoxChanged)
        self.ui.yDataBox.activated.connect(self.onYDataBoxChanged)
        # Add QCharts
        self.chart = QChart()
        self.chartView = QChartView(self.chart)
        self.chartView.setRenderHint(QPainter.Antialiasing)
        self.ui.sbox.addWidget(self.chartView)
        self.xAxis = QValueAxis()
        self.yAxis = QValueAxis()
        self.chartView.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        self.chartView.setFixedSize(720, 385)
        # data vars
        self.xList: list = []
        self.yList: list = []
        self.aCoeff: list = []
        # plot vars
        self.dataName = self.tr("Data Series")
        self.curveName = self.tr("Fitted Curve")
        self.dataColor = QColor(Qt.red)
        self.curveColor = QColor(Qt.black)
        self.dataColorTemp = QColor(Qt.red)
        self.curveColorTemp = QColor(Qt.black)
        self.dataSize = 2
        self.curveSize = 2
        self.dataPenStyle = Qt.PenStyle.SolidLine
        self.curvePenSytle = Qt.PenStyle.DashLine
        # initialize default data
        self.onRefreshBtnClicked()
        self.onXDataBoxChanged()
        self.onYDataBoxChanged()
        self.onPlotBtnClicked()
        self.onFitBtnClicked()
        self.onCurveBtnClicked()
        self.ui.comboBox.setCurrentIndex(0)
        self.onComboBoxChanged()
        # set min size
        self.ui.inputTable.setMinimumHeight(200)
        self.ui.outputTable.setMinimumHeight(200)

    def onAboutBtnClicked(self):
        QMessageBox.about(
            self,
            self.tr("版本: 1.1.0"),
            self.tr("...声明...\n"),
        )

    def onQtBtnClicked(self):
        QMessageBox.aboutQt(self, self.tr("Qt版本"))

    def onSetPlotSizeBtn(self):
        dialog = QDialog(self)
        dialog.setWindowTitle(self.tr("设置绘图大小"))
        # dialog.setGeometry(100, 100, 300, 100)
        dialog.setMinimumSize(150, 100)
        layout = QFormLayout(dialog)
        widthLabel = QLabel(self.tr("宽度:"))
        widthSpinBox = QSpinBox(dialog)
        widthSpinBox.setRange(10, 5000)
        widthSpinBox.setValue(self.chartView.width())
        heightLabel = QLabel(self.tr("高度:"))
        heightSpinBox = QSpinBox(dialog)
        heightSpinBox.setRange(10, 5000)
        heightSpinBox.setValue(self.chartView.height())
        layout.addRow(widthLabel, widthSpinBox)
        layout.addRow(heightLabel, heightSpinBox)
        okButton = QPushButton(self.tr("确定"), dialog)
        okButton.clicked.connect(dialog.accept)
        layout.addWidget(okButton)
        if dialog.exec() == QDialog.Accepted:
            self.chartView.setFixedSize(widthSpinBox.value(), heightSpinBox.value())
            self.chartView.resize(widthSpinBox.value(), heightSpinBox.value())
            qDebug(
                "ChartView size: [%s x %s]"
                % (self.chartView.width(), self.chartView.height())
            )

    def onDataColorBtnClicked(self):
        dialog = QColorDialog(self)
        dialog.setWindowTitle(self.tr("选择绘图数据颜色"))
        dialog.setCurrentColor(self.dataColor)
        if dialog.exec() == QDialog.Accepted:
            self.dataColorTemp = dialog.currentColor()
            self.dataColorPreview.setStyleSheet(
                f"background-color: {self.dataColorTemp.name()};"
            )

    def onCurveColorBtnClicked(self):
        dialog = QColorDialog(self)
        dialog.setWindowTitle(self.tr("选择拟合曲线颜色"))
        dialog.setCurrentColor(self.curveColor)
        if dialog.exec() == QDialog.Accepted:
            self.curveColorTemp = dialog.currentColor()
            self.curveColorPreview.setStyleSheet(
                f"background-color: {self.curveColorTemp.name()};"
            )

    def onSetPlotBtnClicked(self):
        dialog = QDialog(self)
        dialog.setWindowTitle(self.tr("设置绘图参数"))
        dialog.setMinimumSize(150, 100)
        layout = QFormLayout(dialog)
        # data vars
        dataNameLineEdit = QLineEdit(dialog)
        dataNameLineEdit.setText(self.dataName)
        layout.addRow(QLabel(self.tr("数据曲线标签:")), dataNameLineEdit)
        dataColorBtn = QPushButton(self.tr("选择颜色"), dialog)
        self.dataColorPreview = QLabel(dialog)
        self.dataColorPreview.setMinimumSize(40, 20)
        self.dataColorPreview.setStyleSheet(
            f"background-color: {self.dataColor.name()};"
        )
        dataColorBtn.clicked.connect(self.onDataColorBtnClicked)
        hb0 = QHBoxLayout()
        hb0.addWidget(dataColorBtn)
        hb0.addWidget(self.dataColorPreview)
        layout.addRow(QLabel(self.tr("数据曲线颜色:")), hb0)
        dataSizeSpinBox = QSpinBox(dialog)
        dataSizeSpinBox.setRange(1, 10)
        dataSizeSpinBox.setValue(self.dataSize)
        layout.addRow(QLabel(self.tr("数据曲线尺寸:")), dataSizeSpinBox)
        style_map = {
            Qt.PenStyle.SolidLine: 0,
            Qt.PenStyle.DashLine: 1,
            Qt.PenStyle.DotLine: 2,
            Qt.PenStyle.DashDotLine: 3,
            Qt.PenStyle.DashDotDotLine: 4,
        }
        dataLineStyleComboBox = QComboBox(dialog)
        dataLineStyleComboBox.addItems(
            [
                self.tr("实线"),
                self.tr("虚线"),
                self.tr("点线"),
                self.tr("点划线"),
                self.tr("双点划线"),
            ]
        )
        dataLineStyleComboBox.setCurrentIndex(style_map.get(self.dataPenStyle, 0))
        layout.addRow(QLabel(self.tr("数据曲线线型:")), dataLineStyleComboBox)
        # curve vars
        curveNameLineEdit = QLineEdit(dialog)
        curveNameLineEdit.setText(self.curveName)
        layout.addRow(QLabel(self.tr("拟合曲线标签:")), curveNameLineEdit)
        curveColorBtn = QPushButton(self.tr("选择颜色"), dialog)
        self.curveColorPreview = QLabel(dialog)
        self.curveColorPreview.setMinimumSize(40, 20)
        self.curveColorPreview.setStyleSheet(
            f"background-color: {self.curveColor.name()};"
        )
        curveColorBtn.clicked.connect(self.onCurveColorBtnClicked)
        hb1 = QHBoxLayout()
        hb1.addWidget(curveColorBtn)
        hb1.addWidget(self.curveColorPreview)
        layout.addRow(QLabel(self.tr("拟合曲线颜色:")), hb1)
        curveSizeSpinBox = QSpinBox(dialog)
        curveSizeSpinBox.setRange(1, 10)
        curveSizeSpinBox.setValue(self.curveSize)
        layout.addRow(QLabel(self.tr("拟合曲线尺寸:")), curveSizeSpinBox)
        curveLineStyleComboBox = QComboBox(dialog)
        curveLineStyleComboBox.addItems(
            [
                self.tr("实线"),
                self.tr("虚线"),
                self.tr("点线"),
                self.tr("点划线"),
                self.tr("双点划线"),
            ]
        )
        curveLineStyleComboBox.setCurrentIndex(style_map.get(self.curvePenSytle, 0))
        layout.addRow(QLabel(self.tr("拟合曲线线型:")), curveLineStyleComboBox)
        okButton = QPushButton(self.tr("确定"), dialog)
        okButton.clicked.connect(dialog.accept)
        layout.addWidget(okButton)
        if dialog.exec() == QDialog.Accepted:
            # data vars
            self.dataName = dataNameLineEdit.text()
            self.dataSize = dataSizeSpinBox.value()
            self.dataColor = self.dataColorTemp
            pen_styles = [
                Qt.PenStyle.SolidLine,
                Qt.PenStyle.DashLine,
                Qt.PenStyle.DotLine,
                Qt.PenStyle.DashDotLine,
                Qt.PenStyle.DashDotDotLine,
            ]
            self.dataPenStyle = pen_styles[dataLineStyleComboBox.currentIndex()]
            # curve vars
            self.curveName = curveNameLineEdit.text()
            self.curveSize = curveSizeSpinBox.value()
            self.curveColor = self.curveColorTemp
            self.curvePenSytle = pen_styles[curveLineStyleComboBox.currentIndex()]

    def onAdjustPlotBtnClicked(self):
        self.chartView.setFixedSize(self.ui.sarea.width(), self.ui.sarea.height())
        qDebug(
            "ChartView size: [%s x %s]"
            % (self.chartView.width(), self.chartView.height())
        )

    def onSavePlotBtnClicked(self):
        fileName, _ = QFileDialog.getSaveFileName(
            self,
            self.tr("保存绘图"),
            self.plotTitle,
            self.tr("SVG Files (*.svg);;PNG Files (*.png);;All Files (*)"),
        )
        cv = self.chartView
        if fileName:
            if fileName.endswith(".png"):
                cv.grab().save(fileName)
                qDebug("Save PNG file: %s" % fileName)
            elif fileName.endswith(".svg"):
                generator = QSvgGenerator()
                generator.setFileName(fileName)
                generator.setSize(
                    QSize(self.chartView.width(), self.chartView.height())
                )
                generator.setViewBox(
                    QRect(0, 0, self.chartView.width(), self.chartView.height())
                )
                generator.setTitle(self.ui.titleIn.text())
                generator.setDescription("This SVG file is generated by Qt.")
                painter = QPainter()
                painter.begin(generator)
                cv.render(painter)
                painter.end()
                qDebug("Save SVG file: %s" % fileName)
            else:
                QMessageBox.warning(
                    self, self.tr("保存失败"), self.tr("不支持的文件格式")
                )
                return
            QMessageBox.information(
                self, self.tr("保存成功"), self.tr(f"图表已保存为 {fileName}")
            )

    def createFormattedItem(self, value, scientific, decimals):
        if scientific:
            return QTableWidgetItem(f"{value:.{decimals}e}")
        else:
            return QTableWidgetItem(f"{value:.{decimals}f}")

    def filterStringToList(self, input_str: str) -> list:
        pattern = r"[-+]?\d+\.?\d*(?:[eE][-+]?\d+)?"
        matches = re.findall(pattern, input_str)
        output_list = []
        for num_str in matches:
            try:
                output_list.append(float(num_str))
            except ValueError:
                continue
        return output_list

    def clearEmptyRowsOfTableEnd(self, loop: int = 1):
        if loop <= 0:
            loop = 1
        for i in range(loop):
            num_rows = self.ui.inputTable.rowCount()
            for i in range(num_rows):
                try:
                    str1 = self.ui.inputTable.item(i, 0).text()
                except AttributeError:
                    str1 = ""
                try:
                    str2 = self.ui.inputTable.item(i, 1).text()
                except AttributeError:
                    str2 = ""
                if not str1 and not str2:
                    self.ui.inputTable.removeRow(i)

    def onPlotBtnClicked(self):
        if not self.xList or not self.yList:
            QMessageBox.warning(
                self, self.tr("输入错误"), self.tr("请先输入X轴和Y轴数据")
            )
            return
        if len(self.xList) != len(self.yList):
            QMessageBox.warning(
                self, self.tr("输入错误"), self.tr("X轴和Y轴数据长度不一致")
            )
            return
        if not self.ui.titleIn.text():
            QMessageBox.warning(self, self.tr("输入错误"), self.tr("图表标题不能为空"))
            return
        self.plotTitle = self.ui.titleIn.text()
        self.chart.removeAllSeries()
        # Clear existing axes
        if self.xAxis in self.chart.axes():
            self.chart.removeAxis(self.xAxis)
        if self.yAxis in self.chart.axes():
            self.chart.removeAxis(self.yAxis)
        # Create new axes
        axis_x = self.xAxis
        if self.ui.xLabelCheck.isChecked():
            axis_x.setTitleText(self.ui.xLabelIn.text())
        else:
            axis_x.setTitleText("")
        axis_x.setRange(min(self.xList), max(self.xList))
        if self.ui.xLabelCheck.isChecked():
            if self.ui.scientificXCheck.isChecked():
                axis_x.setLabelFormat("%.{}e".format(self.ui.decimalXBox.value()))
            else:
                axis_x.setLabelFormat("%.{}f".format(self.ui.decimalXBox.value()))
        else:
            axis_x.setLabelFormat("")
        axis_y = self.yAxis
        if self.ui.yLabelCheck.isChecked():
            axis_y.setTitleText(self.ui.yLabelIn.text())
        else:
            axis_y.setTitleText("")
        axis_y.setRange(min(self.yList), max(self.yList))
        if self.ui.yLabelCheck.isChecked():
            if self.ui.scientificYCheck.isChecked():
                axis_y.setLabelFormat("%.{}e".format(self.ui.decimalYBox.value()))
            else:
                axis_y.setLabelFormat("%.{}f".format(self.ui.decimalYBox.value()))
        else:
            axis_y.setLabelFormat("")
        series = QLineSeries()
        series.setName(self.dataName)
        series.setPen(QPen(self.dataColor, self.dataSize, self.dataPenStyle))
        for i in range(len(self.xList)):
            series.append(self.xList[i], self.yList[i])
        self.chart.addSeries(series)
        self.chart.addAxis(axis_x, Qt.AlignmentFlag.AlignBottom)
        self.chart.addAxis(axis_y, Qt.AlignmentFlag.AlignLeft)
        series.attachAxis(axis_x)
        series.attachAxis(axis_y)
        if self.ui.titleDisplayCheck.isChecked():
            self.chart.setTitle(self.plotTitle)
        else:
            self.chart.setTitle("")
        self.chart.legend().setAlignment(Qt.AlignmentFlag.AlignBottom)
        if self.ui.legendShowCheck.isChecked():
            self.chart.legend().setVisible(True)
        else:
            self.chart.legend().setVisible(False)
        self.chartView.setRenderHint(QPainter.Antialiasing)
        self.chartView.show()

    def onLoadBtnClicked(self):
        try:
            path, _ = QFileDialog.getOpenFileName(
                self,
                self.tr("打开文件"),
                "",
                self.tr("CSV Files (*.csv);;All Files (*)"),
            )
            if not path:
                return
            with open(path, "r", newline="", encoding="utf-8") as f:
                reader = csv.reader(f)
                rows = [row for row in reader if row]
                if len(rows) < 1:
                    QMessageBox.critical(
                        self, self.tr("格式错误"), self.tr("CSV文件没有内容")
                    )
                    return
                data_rows = rows[1:]
                if len(data_rows) < 1:
                    QMessageBox.critical(
                        self, self.tr("格式错误"), self.tr("CSV文件没有数据")
                    )
                    return
                clo_num = len(rows[0])
                row_num = len(data_rows)
                for row in range(row_num):
                    if len(data_rows[row]) != clo_num:
                        QMessageBox.critical(
                            self,
                            self.tr("格式错误"),
                            self.tr("第%s行数据不完整") % (row + 1),
                        )
                        return
                if self.ui.inputTable.columnCount() < clo_num:
                    self.ui.inputTable.setColumnCount(clo_num)
                for clo in range(clo_num):
                    header = rows[0][clo]
                    if not header or header in ("", " "):
                        header = f"{clo+1}"
                    header_item = self.ui.inputTable.horizontalHeaderItem(clo)
                    if header_item:
                        header_item.setText(header)
                    else:
                        self.ui.inputTable.setHorizontalHeaderItem(
                            clo, QTableWidgetItem(header)
                        )
                if self.ui.inputTable.rowCount() < row_num:
                    self.ui.inputTable.setRowCount(row_num)
                self.ui.inputTable.clearContents()
                for row in range(row_num):
                    for clo in range(clo_num):
                        item = self.ui.inputTable.item(row, clo)
                        if item:
                            item.setText(data_rows[row][clo])
                        else:
                            self.ui.inputTable.setItem(
                                row, clo, QTableWidgetItem(data_rows[row][clo])
                            )
            self.inputTableChanged()
            qDebug("Loaded file: %s" % path)
        except Exception as e:
            QMessageBox.critical(
                self, self.tr("加载错误"), self.tr(f"加载文件失败：{str(e)}")
            )
            qDebug("Error loading file: %s" % e)

    def onSaveBtnClicked(self):
        # self.onRefreshBtnClicked()
        try:
            path, _ = QFileDialog.getSaveFileName(
                self,
                self.tr("保存文件"),
                self.plotTitle,
                self.tr("CSV Files (*.csv);;All Files (*)"),
            )
            if not path:
                return
            with open(path, "w", newline="", encoding="utf-8") as f:
                writer = csv.writer(f)
                # deal row header
                headers = []
                for col in range(self.ui.inputTable.columnCount()):
                    item = self.ui.inputTable.horizontalHeaderItem(col)
                    text = item.text() if item else ""
                    if text in ("", " ", None):
                        text = " "
                    headers.append(text)
                writer.writerow(headers)
                # deal row data
                for row in range(self.ui.inputTable.rowCount()):
                    row_data = []
                    for col in range(self.ui.inputTable.columnCount()):
                        item = self.ui.inputTable.item(row, col)
                        text = item.text() if item else ""
                        if text in ("", " ", None):
                            text = " "
                        row_data.append(text)
                    writer.writerow(row_data)
            QMessageBox.information(
                self, self.tr("保存成功"), self.tr(f"文件已保存至：{path}")
            )
            qDebug("Saved file: %s" % path)
        except Exception as e:
            QMessageBox.critical(
                self,
                self.tr("保存错误"),
                self.tr(f"保存文件时出现错误：{str(e)}"),
            )
            qDebug("Error saving file: %s" % e)

    def getSelectedRowsList(self):
        selected_items = self.ui.inputTable.selectedItems()
        selected_list = []
        for i in selected_items:
            if i.row() < 0 or i.row() >= self.ui.inputTable.rowCount():
                QMessageBox.warning(self, self.tr("操作错误"), self.tr("选择的行无效"))
                return
            selected_list.append(i.row())
        # remove duplicate elements
        selected_list = list(set(selected_list))
        return selected_list

    def getSelectedColumnsList(self):
        selected_items = self.ui.inputTable.selectedItems()
        selected_list = []
        for i in selected_items:
            if i.column() < 0 or i.column() >= self.ui.inputTable.columnCount():
                QMessageBox.warning(self, self.tr("操作错误"), self.tr("选择的列无效"))
                return
            selected_list.append(i.column())
        # remove duplicate elements
        selected_list = list(set(selected_list))
        return selected_list

    def renumberTableRows(self):
        for i in range(self.ui.inputTable.rowCount()):
            self.ui.inputTable.setVerticalHeaderItem(i, QTableWidgetItem(f"{i + 1}"))

    def onRefreshBtnClicked(self):
        # self.ui.inputTable.renumber_header()
        self.ui.inputTable.selectAll()
        self.ui.inputTable.float_clo()
        self.ui.inputTable.clearSelection()
        self.ui.inputTable.clear_empty_space()
        self.inputTableChanged()
        self.ui.rowSpin.setValue(self.ui.inputTable.rowCount())
        self.ui.colSpin.setValue(self.ui.inputTable.columnCount())
        self.onXDataBoxChanged()
        self.onYDataBoxChanged()

    def onTransBtnClicked(self):
        self.ui.inputTable.transpose_table()
        self.ui.rowSpin.setValue(self.ui.inputTable.rowCount())
        self.ui.colSpin.setValue(self.ui.inputTable.columnCount())

    def onComboBoxChanged(self):
        text: str = None
        if self.ui.comboBox.currentIndex() == 0:
            self.ui.numberSpin.setEnabled(True)
            self.ui.interceptCheck.setEnabled(True)
            self.ui.interceptIn.setEnabled(self.ui.interceptCheck.isChecked())
            qDebug("Function: polynomial")
            text = "y = a<sub>0</sub> + a<sub>1</sub>x + a<sub>2</sub>x<sup>2</sup> + ... + a<sub>n</sub>x<sup>n</sup>"
        else:
            self.ui.numberSpin.setEnabled(False)
            self.ui.interceptCheck.setEnabled(False)
            self.ui.interceptIn.setEnabled(False)
            if self.ui.comboBox.currentIndex() == 1:
                qDebug("Function: exponential")
                text = (
                    "y = a<sub>0</sub> + a<sub>1</sub>e<span>^(a<sub>2</sub>x)</span>"
                )
            elif self.ui.comboBox.currentIndex() == 2:
                qDebug("Function: logarithmic")
                text = "y = a<sub>0</sub> + a<sub>1</sub>ln(x)"
            elif self.ui.comboBox.currentIndex() == 3:
                qDebug("Function: power")
                text = "y = a<sub>0</sub>x<span>^(a<sub>1</sub>)</span>"
        if text:
            self.ui.funcLabel.setText(text)

    def inputTableChanged(self):
        column_num = self.ui.inputTable.columnCount()
        column_list = []
        x = self.ui.xDataBox.currentIndex()
        y = self.ui.yDataBox.currentIndex()
        self.ui.xDataBox.clear()
        self.ui.yDataBox.clear()
        for col in range(column_num):
            header = self.ui.inputTable.horizontalHeaderItem(col)
            if header is None:
                text = ""
            else:
                text = header.text()
            column_list.append(self.tr("第{}列 : {}").format(col + 1, text))
            self.ui.xDataBox.addItem(column_list[col])
            self.ui.yDataBox.addItem(column_list[col])
        if x < column_num:
            self.ui.xDataBox.setCurrentIndex(x)
        else:
            self.ui.xDataBox.setCurrentIndex(0)
        if y < column_num:
            self.ui.yDataBox.setCurrentIndex(y)
        else:
            self.ui.yDataBox.setCurrentIndex(column_num - 1)

    def onRowSpinChanged(self, n):
        self.ui.inputTable.setRowCount(n)

    def onColSpinChanged(self, n):
        self.ui.inputTable.setColumnCount(n)
        self.inputTableChanged()

    def onXDataBoxChanged(self):
        col = self.ui.xDataBox.currentIndex()
        self.xList = []
        for row in range(self.ui.inputTable.rowCount()):
            item = self.ui.inputTable.item(row, col)
            if item is None:
                continue
            text = item.text()
            if text in ("", " ", None):
                continue
            try:
                num = float(text)
            except Exception:
                continue
            self.xList.append(num)
        qDebug("X data: %s" % self.xList)

    def onYDataBoxChanged(self):
        col = self.ui.yDataBox.currentIndex()
        self.yList = []
        for row in range(self.ui.inputTable.rowCount()):
            item = self.ui.inputTable.item(row, col)
            if item is None:
                continue
            text = item.text()
            if text in ("", " ", None):
                continue
            try:
                num = float(text)
            except Exception:
                continue
            self.yList.append(num)
        qDebug("Y data: %s" % self.yList)

    def onFitBtnClicked(self):
        if not self.xList or not self.yList:
            QMessageBox.warning(
                self, self.tr("输入错误"), self.tr("请先输入X轴和Y轴数据")
            )
            return
        if len(self.xList) != len(self.yList):
            QMessageBox.warning(
                self, self.tr("输入错误"), self.tr("X轴和Y轴数据长度不一致")
            )
            return
        if self.ui.comboBox.currentIndex() == 0:
            self.fitOnPolynomial()
        elif self.ui.comboBox.currentIndex() == 1:
            self.fitOnExponential()
        elif self.ui.comboBox.currentIndex() == 2:
            self.fitOnLogarithmic()
        elif self.ui.comboBox.currentIndex() == 3:
            self.fitOnPower()

    def updateOutputTable(self, r_squared: float):
        # update output table
        scientific = self.ui.scientificOutCheck.isChecked()
        decimals = self.ui.decimalOutBox.value()
        self.ui.outputTable.clearContents()
        self.ui.outputTable.setRowCount(len(self.aCoeff) + 1)
        for i in range(len(self.aCoeff) + 1):
            if i == 0:
                self.ui.outputTable.setVerticalHeaderItem(i, QTableWidgetItem("r2"))
            else:
                self.ui.outputTable.setVerticalHeaderItem(
                    i, QTableWidgetItem(f"a{i - 1}")
                )
        self.ui.outputTable.setItem(
            0, 0, self.createFormattedItem(r_squared, scientific, decimals)
        )
        for i in range(len(self.aCoeff)):
            self.ui.outputTable.setItem(
                i + 1,
                0,
                self.createFormattedItem(self.aCoeff[i], scientific, decimals),
            )

    def fitOnPower(self):
        for x in self.xList:
            if x <= 0:
                QMessageBox.warning(
                    self,
                    self.tr("输入错误"),
                    self.tr("乘幂函数的自变量必须大于0"),
                )
                return
        xlist = self.xList.copy()
        ylist = self.yList.copy()
        qDebug("xList: %s" % xlist)
        qDebug("yList: %s" % ylist)

        def pow_func(x, a0, a1):
            return a0 * x**a1

        if (ylist[-1] - ylist[0]) / (xlist[-1] - xlist[0]) == 0:
            a0 = a1 = 0.01
        else:
            a0 = a1 = (ylist[-1] - ylist[0]) / (xlist[-1] - xlist[0])
        try:
            popt, pcov = opt.curve_fit(pow_func, xlist, ylist, p0=[a0, a1])
        except:
            QMessageBox.warning(
                self, self.tr("拟合错误"), self.tr("拟合失败，请检查输入数据")
            )
            return
        a0, a1 = popt
        self.aCoeff = [float(a0), float(a1)]

        y_pred = pow_func(np.array(xlist), a0, a1)
        # calculate r^2
        r_squared = self.calcFitRSquared(y_pred.tolist(), ylist)
        # print the fitted curve
        qDebug("Fitted coefficients: %s" % self.aCoeff)
        qDebug("R-squared: %s" % r_squared)
        self.updateOutputTable(r_squared)
        # update text output
        of1_c = f"y={str(self.ui.outputTable.item(1, 0).text())}*pow(x,{str(self.ui.outputTable.item(2, 0).text())})"
        of1_py = f"y={str(self.ui.outputTable.item(1, 0).text())}*x**{str(self.ui.outputTable.item(2, 0).text())}"
        of1_f = of1_py.replace("**", "^")
        of2 = f"r2={self.ui.outputTable.item(0, 0).text()}"
        of1_ps = of1_c.replace("pow", "[math]::pow")
        of1_ps = of1_ps.replace("x", "$x")
        of1_ps = of1_ps.replace("y", "$y")
        qDebug("Output formula: %s" % of1_f)
        qDebug("Output r2: %s" % of2)
        self.ui.outputEdit.clear()
        self.ui.outputEdit.setText(
            "[R²]\n"
            + of2
            + "\n[Formula]\n"
            + of1_f
            + "\n[Python/Fortran]\n"
            + of1_py
            + "\n[C/C++]\n"
            + of1_c
            + "\n[PowerShell]\n"
            + of1_ps
            + "\n"
        )

    def fitOnLogarithmic(self):
        for x in self.xList:
            if x <= 0:
                QMessageBox.warning(
                    self,
                    self.tr("输入错误"),
                    self.tr("对数函数的自变量必须大于0"),
                )
                return
        xlist = self.xList.copy()
        ylist = self.yList.copy()
        qDebug("xList: %s" % xlist)
        qDebug("yList: %s" % ylist)

        def log_func(x, a0, a1):
            return a0 + a1 * np.log(x)

        if (ylist[-1] - ylist[0]) / (xlist[-1] - xlist[0]) == 0:
            a0 = a1 = 0.01
        else:
            a0 = a1 = (ylist[-1] - ylist[0]) / (xlist[-1] - xlist[0])
        try:
            popt, pcov = opt.curve_fit(log_func, xlist, ylist, p0=[a0, a1])
        except:
            QMessageBox.warning(
                self, self.tr("拟合错误"), self.tr("拟合失败，请检查输入数据")
            )
            return
        a0, a1 = popt
        self.aCoeff = [float(a0), float(a1)]

        y_pred = log_func(np.array(xlist), a0, a1)
        # calculate r^2
        r_squared = self.calcFitRSquared(y_pred.tolist(), ylist)
        # print the fitted curve
        qDebug("Fitted coefficients: %s" % self.aCoeff)
        qDebug("R-squared: %s" % r_squared)
        self.updateOutputTable(r_squared)
        # update text output
        of1_c = f"y={str(self.ui.outputTable.item(1, 0).text())}+{str(self.ui.outputTable.item(2, 0).text())}*log(x)"
        of1_c = of1_c.replace("+-", "-")
        of1_py = of1_c.replace("log", "math.log")
        of1_f = of1_c.replace("log", "ln")
        of1_f = of1_f.replace("+-", "-")
        of2 = f"r2={self.ui.outputTable.item(0, 0).text()}"
        of1_ps = of1_py.replace("math.log", "[math]::log")
        of1_ps = of1_ps.replace("x", "$x")
        of1_ps = of1_ps.replace("y", "$y")
        qDebug("Output formula: %s" % of1_f)
        qDebug("Output r2: %s" % of2)
        self.ui.outputEdit.clear()
        self.ui.outputEdit.setText(
            "[R²]\n"
            + of2
            + "\n[Formula]\n"
            + of1_f
            + "\n[Python]\n"
            + of1_py
            + "\n[C/C++/Fortran]\n"
            + of1_c
            + "\n[PowerShell]\n"
            + of1_ps
            + "\n"
        )

    def fitOnExponential(self):
        xlist = self.xList.copy()
        ylist = self.yList.copy()
        qDebug("xList: %s" % xlist)
        qDebug("yList: %s" % ylist)

        def exp_func(x, a0, a1, a2):
            return a0 + a1 * np.exp(a2 * x)

        if (ylist[-1] - ylist[0]) / (xlist[-1] - xlist[0]) == 0:
            a0 = a1 = a2 = 0.01
        else:
            a0 = a1 = a2 = (ylist[-1] - ylist[0]) / (xlist[-1] - xlist[0])
        try:
            popt, pcov = opt.curve_fit(exp_func, xlist, ylist, p0=[a0, a1, a2])
        except:
            QMessageBox.warning(
                self, self.tr("拟合错误"), self.tr("拟合失败，请检查输入数据")
            )
            return
        a0, a1, a2 = popt
        self.aCoeff = [float(a0), float(a1), float(a2)]

        y_pred = exp_func(np.array(xlist), a0, a1, a2)
        # calculate r^2
        r_squared = self.calcFitRSquared(y_pred.tolist(), ylist)
        # print the fitted curve
        qDebug("Fitted coefficients: %s" % self.aCoeff)
        qDebug("R-squared: %s" % r_squared)
        self.updateOutputTable(r_squared)
        # update text output
        of1_c = f"y={str(self.ui.outputTable.item(1, 0).text())}+{str(self.ui.outputTable.item(2, 0).text())}*exp({str(self.ui.outputTable.item(3, 0).text())}*x)"
        of1_c = of1_c.replace("+-", "-")
        of1_py = of1_c.replace("exp", "math.exp")
        of1_f = of1_c.replace("exp", "e^")
        of2 = f"r2={self.ui.outputTable.item(0, 0).text()}"
        of1_ps = of1_py.replace("math.exp", "[math]::exp")
        of1_ps = of1_ps.replace("x", "$x")
        of1_ps = of1_ps.replace("y", "$y")
        qDebug("Output formula: %s" % of1_f)
        qDebug("Output r2: %s" % of2)
        self.ui.outputEdit.clear()
        self.ui.outputEdit.setText(
            "[R²]\n"
            + of2
            + "\n[Formula]\n"
            + of1_f
            + "\n[Python]\n"
            + of1_py
            + "\n[C/C++/Fortran]\n"
            + of1_c
            + "\n[PowerShell]\n"
            + of1_ps
            + "\n"
        )

    def calcPolyCoeff(self, xlist: list, ylist: list, deg: int):
        try:
            if len(xlist) <= deg:
                raise ValueError(self.tr("数据点数不足以拟合该次数多项式"))
            coefficients = np.polyfit(xlist, ylist, deg)
            np.polyfit(xlist, ylist, deg, full=True)
            return coefficients
        except ValueError as e:
            QMessageBox.warning(self, self.tr("拟合错误"), str(e))
            return None

    def calcFitRSquared(self, y_pred: list, y_true: list):
        try:
            if len(y_pred) != len(y_true):
                raise ValueError(self.tr("预测值和拟合值数据长度不一致"))
            # calculate r_squared
            y_mean = np.mean(np.array(y_true))
            SS_tot = np.sum((np.array(y_true) - y_mean) ** 2)
            SS_res = np.sum((np.array(y_true) - np.array(y_pred)) ** 2)
            r_squared = 1 - (SS_res / SS_tot)
            return r_squared
        except ValueError as e:
            QMessageBox.warning(self, self.tr("计算R2错误"), str(e))
            return None

    def fitOnPolynomial(self):
        xlist = self.xList.copy()
        ylist = self.yList.copy()
        if self.ui.interceptCheck.isChecked():
            try:
                y = float(self.ui.interceptIn.text())
            except ValueError:
                QMessageBox.warning(
                    self, self.tr("输入错误"), self.tr("截距必须输入数字")
                )
                return
            for i in range(len(xlist)):
                if xlist[i] < 0:
                    continue
                elif xlist[i] == 0:
                    QMessageBox.warning(
                        self,
                        self.tr("输入错误"),
                        self.tr("X轴数据不能包含0，除非取消勾选截距选项"),
                    )
                    return
                else:
                    xlist.insert(i, 0)
                    ylist.insert(i, y)
                    break
        qDebug("xList: %s" % xlist)
        qDebug("yList: %s" % ylist)
        deg = self.ui.numberSpin.value()
        coefficients = self.calcPolyCoeff(xlist, ylist, deg)
        if coefficients is None:
            return
        self.aCoeff = coefficients[::-1]
        if self.ui.interceptCheck.isChecked():
            self.aCoeff[0] = y
        p = np.poly1d(self.aCoeff[::-1])
        y_pred = p(xlist)
        # calculate r^2
        r_squared = self.calcFitRSquared(y_pred.tolist(), ylist)
        # print the fitted curve
        qDebug("Fitted coefficients: %s" % self.aCoeff)
        qDebug("R-squared: %s" % r_squared)
        self.updateOutputTable(r_squared)
        # update text output
        of1_c = f"y={str(self.ui.outputTable.item(1, 0).text())}+{str(self.ui.outputTable.item(2, 0).text())}*x"
        of1_py = of1_c
        for i in range(3, deg + 2):
            of1_c += f"+{self.ui.outputTable.item(i, 0).text()}*pow(x,{i-1})"
            of1_py += f"+{self.ui.outputTable.item(i, 0).text()}*x**{i-1}"
        of1_c = of1_c.replace("+-", "-")
        of1_py = of1_py.replace("+-", "-")
        of1_f = of1_py.replace("**", "^")
        of1_ps = of1_c.replace("pow", "[math]::pow")
        of1_ps = of1_ps.replace("x", "$x")
        of1_ps = of1_ps.replace("y", "$y")
        of2 = f"r2={self.ui.outputTable.item(0, 0).text()}"
        qDebug("Output formula: %s" % of1_f)
        qDebug("Output r2: %s" % of2)
        self.ui.outputEdit.clear()
        self.ui.outputEdit.setText(
            "[R²]\n"
            + of2
            + "\n[Formula]\n"
            + of1_f
            + "\n[Python/Fortran]\n"
            + of1_py
            + "\n[C/C++]\n"
            + of1_c
            + "\n[PowerShell]\n"
            + of1_ps
            + "\n"
        )

    def onCurveBtnClicked(self):
        if len(self.aCoeff) <= 0:
            QMessageBox.warning(self, self.tr("输入错误"), self.tr("请先进行拟合"))
            return
        yFitList = []
        if self.ui.comboBox.currentIndex() == 0:
            for x in self.xList:
                y_value = self.aCoeff[0]
                for i in range(1, len(self.aCoeff)):
                    y_value += self.aCoeff[i] * (x**i)
                yFitList.append(y_value)
        elif self.ui.comboBox.currentIndex() == 1:
            for x in self.xList:
                y_value = self.aCoeff[0] + self.aCoeff[1] * np.exp(self.aCoeff[2] * x)
                yFitList.append(y_value)
        elif self.ui.comboBox.currentIndex() == 2:
            for x in self.xList:
                if x <= 0:
                    QMessageBox.warning(
                        self,
                        self.tr("输入错误"),
                        self.tr("对数函数的自变量必须大于0"),
                    )
                    return
                y_value = self.aCoeff[0] + self.aCoeff[1] * np.log(x)
                yFitList.append(y_value)
        elif self.ui.comboBox.currentIndex() == 3:
            for x in self.xList:
                if x <= 0:
                    QMessageBox.warning(
                        self,
                        self.tr("输入错误"),
                        self.tr("乘幂函数的自变量必须大于0"),
                    )
                    return
                y_value = self.aCoeff[0] * x ** self.aCoeff[1]
                yFitList.append(y_value)
        self.ui.tabWidget.setCurrentIndex(1)
        self.onPlotBtnClicked()
        series = QSplineSeries()
        series.setName(self.curveName)
        series.setPen(QPen(self.curveColor, self.curveSize, self.curvePenSytle))
        for i in range(len(self.xList)):
            series.append(self.xList[i], yFitList[i])
        self.chart.addSeries(series)
        series.attachAxis(self.xAxis)
        series.attachAxis(self.yAxis)
        self.yAxis.setRange(min(yFitList + self.yList), max(yFitList + self.yList))
        self.chartView.show()

    def onCalcYOutClicked(self):
        if len(self.aCoeff) <= 0:
            QMessageBox.warning(self, self.tr("输入错误"), self.tr("请先进行拟合"))
            return
        try:
            x_value = float(self.ui.xIn.text())
        except ValueError:
            QMessageBox.warning(self, self.tr("输入错误"), self.tr("请输入有效的数字"))
            return
        if self.ui.comboBox.currentIndex() == 0:
            for i in range(len(self.aCoeff)):
                if i == 0:
                    y_value = self.aCoeff[i]
                else:
                    y_value += self.aCoeff[i] * (x_value**i)
        elif self.ui.comboBox.currentIndex() == 1:
            y_value = self.aCoeff[0] + self.aCoeff[1] * np.exp(self.aCoeff[2] * x_value)
        elif self.ui.comboBox.currentIndex() == 2:
            if x_value <= 0:
                QMessageBox.warning(
                    self,
                    self.tr("输入错误"),
                    self.tr("对数函数的自变量必须大于0"),
                )
                return
            y_value = self.aCoeff[0] + self.aCoeff[1] * np.log(x_value)
        elif self.ui.comboBox.currentIndex() == 3:
            if x_value <= 0:
                QMessageBox.warning(
                    self,
                    self.tr("输入错误"),
                    self.tr("乘幂函数的自变量必须大于0"),
                )
                return
            y_value = self.aCoeff[0] * x_value ** self.aCoeff[1]
        decimals = self.ui.decimalOutBox.value()
        if self.ui.scientificOutCheck.isChecked():
            result = f"{y_value:.{decimals}e}"
        else:
            result = f"{y_value:.{decimals}f}"
        self.ui.yOut.setText(result)
        qDebug("X: %s, Y: %s" % (x_value, y_value))

    def onCalcXOutClicked(self):
        if len(self.aCoeff) <= 0:
            QMessageBox.warning(self, self.tr("输入错误"), self.tr("请先进行拟合"))
            return
        try:
            target_y = float(self.ui.yIn.text())
        except ValueError:
            QMessageBox.warning(self, self.tr("输入错误"), self.tr("请输入有效的数字"))
            return
        # Newton's iterative method
        max_iterations = 100000
        tolerance = 1e-8
        x_init = self.xList[len(self.xList) // 2]
        n = 0
        if self.ui.comboBox.currentIndex() == 0:

            def f(x):
                return (
                    sum(coeff * (x**i) for i, coeff in enumerate(self.aCoeff))
                    - target_y
                )

            def df(x):
                return sum(
                    i * coeff * (x ** (i - 1))
                    for i, coeff in enumerate(self.aCoeff)
                    if i > 0
                )

            for t in range(max_iterations):
                fx = f(x_init)
                if abs(fx) < tolerance:
                    break
                dfx = df(x_init)
                if abs(dfx) < 1e-12:
                    x_init = x_init + 0.1
                    continue
                x_init -= fx / dfx
                n = t + 1
        elif self.ui.comboBox.currentIndex() == 1:
            for t in range(max_iterations):
                exp_term = self.aCoeff[1] * np.exp(self.aCoeff[2] * x_init)
                y_init = self.aCoeff[0] + exp_term
                f_prime = self.aCoeff[2] * exp_term
                if abs(y_init - target_y) < tolerance:
                    break
                if abs(f_prime) < 1e-12:
                    x_init += 0.1
                    continue
                x_init -= (y_init - target_y) / f_prime
                n = t + 1
        elif self.ui.comboBox.currentIndex() == 2:
            for t in range(max_iterations):
                if x_init <= 0:
                    x_init = 1e-6
                    continue
                y_init = self.aCoeff[0] + self.aCoeff[1] * np.log(x_init)
                f_prime = self.aCoeff[1] / x_init
                if abs(y_init - target_y) < tolerance:
                    break
                if abs(f_prime) < 1e-12:
                    x_init += 0.1
                    continue
                x_init -= (y_init - target_y) / f_prime
                n = t + 1
        elif self.ui.comboBox.currentIndex() == 3:
            for t in range(max_iterations):
                if x_init <= 0:
                    x_init = 1e-6
                    continue
                y_init = self.aCoeff[0] * x_init ** self.aCoeff[1]
                f_prime = self.aCoeff[1] * x_init ** (self.aCoeff[1] - 1)
                if abs(y_init - target_y) < tolerance:
                    break
                if abs(f_prime) < 1e-12:
                    x_init += 0.1
                    continue
                x_init -= (y_init - target_y) / f_prime
                n = t + 1
        if n >= max_iterations:
            if abs(y_init - target_y) > tolerance:
                QMessageBox.warning(
                    self,
                    self.tr("迭代失败"),
                    self.tr("未在最大迭代次数内找到解"),
                )
                return
        qDebug("X: %s, Y: %s, LoopNum: %s" % (x_init, target_y, n))
        decimals = self.ui.decimalOutBox.value()
        if self.ui.scientificOutCheck.isChecked():
            x_value = f"{x_init:.{decimals}e}"
        else:
            x_value = f"{x_init:.{decimals}f}"
        self.ui.xOut.setText(x_value)


if __name__ == "__main__":
    """
    app = QApplication(sys.argv)
    widget = Widget()
    widget.show()
    widget.onAdjustPlotBtnClicked()
    sys.exit(app.exec())
    """
