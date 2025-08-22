# -*- coding: utf-8 -*-

import re
import csv
import numpy as np

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

from .cff import LinearFit, NonLinearFit

# Important:
# You need to run the following command to generate the ui_form.py file
#     pyside6-uic form.ui -o form_ui.py, or
#     pyside2-uic form.ui -o form_ui.py
from pycff.form_ui import Ui_Widget


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
        self.ui.funcLabel.setVisible(self.ui.comboBox.currentIndex() != 5)
        self.ui.funcInput.setVisible(self.ui.comboBox.currentIndex() == 5)
        self.ui.outputTable.disable_editing()
        self.ui.rowSpin.valueChanged.connect(self.onRowSpinChanged)
        self.ui.colSpin.valueChanged.connect(self.onColSpinChanged)
        self.ui.xDataBox.activated.connect(self.onXDataBoxChanged)
        self.ui.yDataBox.activated.connect(self.onYDataBoxChanged)
        self.ui.refineSP.setEnabled(self.ui.refineCB.isChecked())
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
        # fit class
        self.fit_class: LinearFit | NonLinearFit = None
        self.fit_nonl_func: str = None
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
            self.tr("关于本程序"),
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
                self, self.tr("加载错误"), self.tr("加载文件失败\n\n%s" % e)
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
                self.tr("保存文件时出现错误\n\n%s" % e),
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
        self.ui.funcLabel.setVisible(self.ui.comboBox.currentIndex() != 5)
        self.ui.funcInput.setVisible(self.ui.comboBox.currentIndex() == 5)
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
                text = "y = a + b * e^(c * x)"
            elif self.ui.comboBox.currentIndex() == 2:
                qDebug("Function: exponential")
                text = "y = a * e^(b * x) (y > 0)"
                self.ui.interceptCheck.setEnabled(True)
                self.ui.interceptIn.setEnabled(True)
            elif self.ui.comboBox.currentIndex() == 3:
                qDebug("Function: logarithmic")
                text = "y = a + b * ln(x) (x > 0)"
            elif self.ui.comboBox.currentIndex() == 4:
                qDebug("Function: power")
                text = "y = a * x^b (x > 0)"
            elif self.ui.comboBox.currentIndex() == 5:
                qDebug("Function: custom")
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
            self.fitOnExponential2()
        elif self.ui.comboBox.currentIndex() == 3:
            self.fitOnLogarithmic()
        elif self.ui.comboBox.currentIndex() == 4:
            self.fitOnPower()
        elif self.ui.comboBox.currentIndex() == 5:
            self.fitOnCustom()

    def updateOutputTable(
        self, r_squared: float, args: list[str] = None, coef: list[float] = None
    ):
        # update output table
        self.ui.outputTable.enable_editing()
        scientific = self.ui.scientificOutCheck.isChecked()
        decimals = self.ui.decimalOutBox.value()
        self.ui.outputTable.clearContents()
        if coef is None:
            coef = self.fit_class.params[::-1]
            args = []
            for i in range(len(coef)):
                args.append(f"a{i}")
        else:
            if args is None:
                raise RuntimeError("args must be provided if coef is provided")
            elif len(args) != len(coef):
                raise RuntimeError("length of args should match with coef")

        self.ui.outputTable.setRowCount(len(coef) + 1)
        for i in range(len(coef) + 1):
            if i == 0:
                self.ui.outputTable.setVerticalHeaderItem(i, QTableWidgetItem("r2"))
            else:
                self.ui.outputTable.setVerticalHeaderItem(
                    i, QTableWidgetItem(args[i - 1])
                )
        self.ui.outputTable.setItem(
            0, 0, self.createFormattedItem(r_squared, scientific, decimals)
        )
        for i in range(len(coef)):
            self.ui.outputTable.setItem(
                i + 1,
                0,
                self.createFormattedItem(coef[i], scientific, decimals),
            )
        self.ui.outputTable.renumber_header_clo()
        self.ui.outputTable.clear_empty_space()
        self.ui.outputTable.disable_editing()

    def fitOnCustom(self):
        expr = self.ui.funcInput.text().strip()
        if expr in ("", " ", None):
            QMessageBox.warning(
                self, self.tr("输入错误"), self.tr("请先输入自定义函数")
            )
            return
        try:
            self.fit_nonl_func = expr
            try:
                self.fit_class = NonLinearFit.from_expr(
                    self.xList,
                    self.yList,
                    self.fit_nonl_func,
                )
            except Exception as e:
                QMessageBox.warning(
                    self,
                    self.tr("初始化错误"),
                    self.tr("初始化失败，请检查输入数据\n\n%s" % e),
                )
                return
            coef = self.fit_class.fit()
        except Exception as e:
            QMessageBox.warning(
                self, self.tr("拟合错误"), self.tr("拟合失败，请检查输入数据\n\n%s" % e)
            )
            qDebug("Error in fitOnCustom: %s" % e)
            return
        r_squared = self.fit_class.r_squared()
        args = self.fit_class.args()
        qDebug("Fitted coefficients: %s" % coef)
        qDebug("R-squared: %s" % r_squared)
        self.updateOutputTable(r_squared, args=args[1:], coef=coef)
        # update text output
        of1_f = "y = %s" % self.fit_nonl_func
        ccoef: list[str] = []
        for i in coef:
            if self.ui.scientificOutCheck.isChecked():
                ss = f"{i:.{self.ui.decimalOutBox.value()}e}"
            else:
                ss = f"{i:.{self.ui.decimalOutBox.value()}f}"
            ccoef.append(ss)
        if self.ui.scientificOutCheck.isChecked():
            r2 = f"{r_squared:.{self.ui.decimalOutBox.value()}e}"
        else:
            r2 = f"{r_squared:.{self.ui.decimalOutBox.value()}f}"
        for i in range(len(ccoef)):
            of1_f = of1_f.replace(args[i + 1], ccoef[i])
        of1_f = of1_f.replace("+-", "-").replace("+ -", "-")
        of2 = f"r2 = {r2}"
        qDebug("Output formula: %s" % of1_f)
        qDebug("Output r2: %s" % of2)
        self.ui.outputEdit.clear()
        self.ui.outputEdit.setText("[R²]\n" + of2 + "\n[Formula]\n" + of1_f + "\n")

    def fitOnPower(self):
        if min(self.xList) <= 0:
            QMessageBox.warning(
                self,
                self.tr("输入错误"),
                self.tr("自变量必须大于0"),
            )
            return
        xlist = self.xList
        ylist = self.yList
        qDebug("xList: %s" % xlist)
        qDebug("yList: %s" % ylist)
        self.fit_nonl_func = "a * x**b"
        try:
            self.fit_class = NonLinearFit(
                xlist,
                ylist,
                lambda x, a, b: eval(self.fit_nonl_func),
            )
        except Exception as e:
            QMessageBox.warning(
                self,
                self.tr("初始化错误"),
                self.tr("初始化失败，请检查输入数据\n\n%s" % e),
            )
            return
        try:
            coef = self.fit_class.fit()
        except Exception as e:
            QMessageBox.warning(
                self, self.tr("拟合错误"), self.tr("拟合失败，请检查输入数据\n\n%s" % e)
            )
            qDebug("Error in fitOnPower: %s" % e)
            return
        r_squared = self.fit_class.r_squared()
        args = self.fit_class.args()
        qDebug("Fitted coefficients: %s" % coef)
        qDebug("R-squared: %s" % r_squared)
        self.updateOutputTable(r_squared, args=args[1:], coef=coef)
        # update text output
        of1_py = "y = %s" % self.fit_nonl_func
        of1_c = of1_py.replace("x**b", "pow(x, b)")
        a, b = coef
        if self.ui.scientificOutCheck.isChecked():
            a = f"{a:.{self.ui.decimalOutBox.value()}e}"
            b = f"{b:.{self.ui.decimalOutBox.value()}e}"
            r2 = f"{r_squared:.{self.ui.decimalOutBox.value()}e}"
        else:
            a = f"{a:.{self.ui.decimalOutBox.value()}f}"
            b = f"{b:.{self.ui.decimalOutBox.value()}f}"
            r2 = f"{r_squared:.{self.ui.decimalOutBox.value()}f}"
        of1_py = of1_py.replace("a", a).replace("b", b)
        of1_c = of1_c.replace("a", a).replace("b", b)
        of1_f = of1_py.replace("**", "^")
        of1_ps = of1_c.replace("pow", "[math]::pow")
        of1_ps = of1_ps.replace("x", "$x")
        of1_ps = of1_ps.replace("y", "$y")
        of2 = f"r2 = {r2}"
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
        if min(self.xList) <= 0:
            QMessageBox.warning(
                self,
                self.tr("输入错误"),
                self.tr("自变量必须大于0"),
            )
            return
        xlist = self.xList
        ylist = self.yList
        qDebug("xList: %s" % xlist)
        qDebug("yList: %s" % ylist)
        self.fit_nonl_func = "a + b * np.log(x)"
        try:
            self.fit_class = NonLinearFit(
                xlist,
                ylist,
                lambda x, a, b: eval(self.fit_nonl_func),
            )
        except Exception as e:
            QMessageBox.warning(
                self,
                self.tr("初始化错误"),
                self.tr("初始化失败，请检查输入数据\n\n%s" % e),
            )
            return
        try:
            coef = self.fit_class.fit()
        except Exception as e:
            QMessageBox.warning(
                self, self.tr("拟合错误"), self.tr("拟合失败，请检查输入数据\n\n%s" % e)
            )
            qDebug("Error in fitOnLogarithmic: %s" % e)
            return
        r_squared = self.fit_class.r_squared()
        args = self.fit_class.args()
        qDebug("Fitted coefficients: %s" % coef)
        qDebug("R-squared: %s" % r_squared)
        self.updateOutputTable(r_squared, args=args[1:], coef=coef)
        # update text output
        of1_c = "y = %s" % self.fit_nonl_func
        of1_c = of1_c.replace("np.log", "log")
        a, b = coef
        if self.ui.scientificOutCheck.isChecked():
            a = f"{a:.{self.ui.decimalOutBox.value()}e}"
            b = f"{b:.{self.ui.decimalOutBox.value()}e}"
            r2 = f"{r_squared:.{self.ui.decimalOutBox.value()}e}"
        else:
            a = f"{a:.{self.ui.decimalOutBox.value()}f}"
            b = f"{b:.{self.ui.decimalOutBox.value()}f}"
            r2 = f"{r_squared:.{self.ui.decimalOutBox.value()}f}"
        if abs(float(a)) < 1e-12:
            of1_c = of1_c.replace("a + b", "b").replace("b", b)
        else:
            of1_c = of1_c.replace("a", a).replace("b", b)
        of1_c = of1_c.replace("+-", "-").replace("+ -", "-")
        of1_py = of1_c.replace("log", "math.log")
        of1_f = of1_c.replace("log", "ln")
        of1_ps = of1_py.replace("math.log", "[math]::log")
        of1_ps = of1_ps.replace("x", "$x")
        of1_ps = of1_ps.replace("y", "$y")
        of2 = f"r2 = {r2}"
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

    def fitOnExponential2(self):
        if min(self.yList) <= 0:
            QMessageBox.warning(
                self,
                self.tr("输入错误"),
                self.tr("因变量必须大于0"),
            )
            return
        xlist = self.xList
        ylist = self.yList
        qDebug("xList: %s" % xlist)
        qDebug("yList: %s" % ylist)
        if self.ui.interceptCheck.isChecked():
            try:
                y = float(self.ui.interceptIn.text())
            except ValueError:
                QMessageBox.warning(
                    self, self.tr("输入错误"), self.tr("截距必须输入数字")
                )
                return
            if y <= 0:
                QMessageBox.warning(self, self.tr("输入错误"), self.tr("截距必须大于0"))
                return
            self.fit_nonl_func = "a * np.exp(b * x)".replace("a", str(y))
            try:
                self.fit_class = NonLinearFit(
                    xlist,
                    ylist,
                    lambda x, b: eval(self.fit_nonl_func),
                )
            except Exception as e:
                QMessageBox.warning(
                    self,
                    self.tr("初始化错误"),
                    self.tr("初始化失败，请检查输入数据\n\n%s" % e),
                )
                return
        else:
            self.fit_nonl_func = "a * np.exp(b * x)"
            try:
                self.fit_class = NonLinearFit(
                    xlist,
                    ylist,
                    lambda x, a, b: eval(self.fit_nonl_func),
                )
            except Exception as e:
                QMessageBox.warning(
                    self,
                    self.tr("初始化错误"),
                    self.tr("初始化失败，请检查输入数据\n\n%s" % e),
                )
                return
        try:
            coef = self.fit_class.fit().copy()
        except Exception as e:
            QMessageBox.warning(
                self, self.tr("拟合错误"), self.tr("拟合失败，请检查输入数据\n\n%s" % e)
            )
            qDebug("Error in fitOnExponential: %s" % e)
            return
        r_squared = self.fit_class.r_squared()
        args = self.fit_class.args().copy()
        qDebug("Fitted coefficients: %s" % coef)
        qDebug("R-squared: %s" % r_squared)
        if self.ui.interceptCheck.isChecked():
            args.insert(1, "a")
            coef.insert(0, float(self.ui.interceptIn.text()))
        self.updateOutputTable(r_squared, args=args[1:], coef=coef)
        # update text output
        of1_c = "y = a * exp(b * x)"
        a, b = coef
        if self.ui.scientificOutCheck.isChecked():
            a = f"{a:.{self.ui.decimalOutBox.value()}e}"
            b = f"{b:.{self.ui.decimalOutBox.value()}e}"
            r2 = f"{r_squared:.{self.ui.decimalOutBox.value()}e}"
        else:
            a = f"{a:.{self.ui.decimalOutBox.value()}f}"
            b = f"{b:.{self.ui.decimalOutBox.value()}f}"
            r2 = f"{r_squared:.{self.ui.decimalOutBox.value()}f}"
        of1_c = of1_c.replace("a", a).replace("b", b)
        of1_c = of1_c.replace("+-", "-").replace("+ -", "-")
        of1_py = of1_c.replace("exp", "math.exp")
        of1_f = of1_c.replace("exp", "e^")
        of1_ps = of1_py.replace("math.exp", "[math]::exp")
        of1_ps = of1_ps.replace("x", "$x")
        of1_ps = of1_ps.replace("y", "$y")
        of2 = f"r2 = {r2}"
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
        xlist = self.xList
        ylist = self.yList
        qDebug("xList: %s" % xlist)
        qDebug("yList: %s" % ylist)
        self.fit_nonl_func = "a + b * np.exp(c * x)"
        try:
            self.fit_class = NonLinearFit(
                xlist,
                ylist,
                lambda x, a, b, c: eval(self.fit_nonl_func),
            )
        except Exception as e:
            QMessageBox.warning(
                self,
                self.tr("初始化错误"),
                self.tr("初始化失败，请检查输入数据\n\n%s" % e),
            )
            return
        try:
            coef = self.fit_class.fit()
        except Exception as e:
            QMessageBox.warning(
                self, self.tr("拟合错误"), self.tr("拟合失败，请检查输入数据\n\n%s" % e)
            )
            qDebug("Error in fitOnExponential: %s" % e)
            return
        r_squared = self.fit_class.r_squared()
        args = self.fit_class.args()
        qDebug("Fitted coefficients: %s" % coef)
        qDebug("R-squared: %s" % r_squared)
        self.updateOutputTable(r_squared, args=args[1:], coef=coef)
        # update text output
        of1_c = "y = %s" % self.fit_nonl_func
        of1_c = of1_c.replace("np.exp", "exp")
        a, b, c = coef
        if self.ui.scientificOutCheck.isChecked():
            a = f"{a:.{self.ui.decimalOutBox.value()}e}"
            b = f"{b:.{self.ui.decimalOutBox.value()}e}"
            c = f"{c:.{self.ui.decimalOutBox.value()}e}"
            r2 = f"{r_squared:.{self.ui.decimalOutBox.value()}e}"
        else:
            a = f"{a:.{self.ui.decimalOutBox.value()}f}"
            b = f"{b:.{self.ui.decimalOutBox.value()}f}"
            c = f"{c:.{self.ui.decimalOutBox.value()}f}"
            r2 = f"{r_squared:.{self.ui.decimalOutBox.value()}f}"
        if abs(float(a)) < 1e-12:
            of1_c = of1_c.replace("a + b", "b").replace("b", b).replace("c", c)
        else:
            of1_c = of1_c.replace("a", a).replace("b", b).replace("c", c)
        of1_c = of1_c.replace("+-", "-").replace("+ -", "-")
        of1_py = of1_c.replace("exp", "math.exp")
        of1_f = of1_c.replace("exp", "e^")
        of1_ps = of1_py.replace("math.exp", "[math]::exp")
        of1_ps = of1_ps.replace("x", "$x")
        of1_ps = of1_ps.replace("y", "$y")
        of2 = f"r2 = {r2}"
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

    def fitOnPolynomial(self):
        xlist = self.xList
        ylist = self.yList
        qDebug("xList: %s" % xlist)
        qDebug("yList: %s" % ylist)
        deg = self.ui.numberSpin.value()
        if self.ui.interceptCheck.isChecked():
            try:
                y = float(self.ui.interceptIn.text())
            except ValueError:
                QMessageBox.warning(
                    self, self.tr("输入错误"), self.tr("截距必须输入数字")
                )
                return
            try:
                self.fit_class = LinearFit(
                    xlist,
                    ylist,
                    degree=deg,
                    y_intercept=y,
                )
            except Exception as e:
                QMessageBox.warning(
                    self,
                    self.tr("初始化错误"),
                    self.tr("初始化失败，请检查输入数据\n\n%s" % e),
                )
                return
        else:
            try:
                self.fit_class = LinearFit(
                    xlist,
                    ylist,
                    degree=deg,
                )
            except Exception as e:
                QMessageBox.warning(
                    self,
                    self.tr("初始化错误"),
                    self.tr("初始化失败，请检查输入数据\n\n%s" % e),
                )
                return
        try:
            coef = self.fit_class.fit()
        except Exception as e:
            QMessageBox.warning(
                self, self.tr("拟合错误"), self.tr("拟合失败，请检查输入数据\n\n%s" % e)
            )
            qDebug("Error in fitOnPolynomial: %s" % e)
            return
        r_squared = self.fit_class.r_squared()
        qDebug("Fitted coefficients: %s" % coef[::-1])
        qDebug("R-squared: %s" % r_squared)
        self.updateOutputTable(r_squared)
        # update text output
        coef_str: list[str] = []
        if self.ui.scientificOutCheck.isChecked():
            r2 = f"{r_squared:.{self.ui.decimalOutBox.value()}e}"
            for c in coef[::-1]:
                coef_str.append(f"{c:.{self.ui.decimalOutBox.value()}e}")
        else:
            r2 = f"{r_squared:.{self.ui.decimalOutBox.value()}f}"
            for c in coef[::-1]:
                coef_str.append(f"{c:.{self.ui.decimalOutBox.value()}f}")
        of1_c = "y = "
        of1_py = of1_c
        for i, s in enumerate(coef_str):
            if i == 0:
                if abs(float(s)) < 1e-12:
                    continue
                of1_c += s + " + "
                of1_py += s + " + "
            elif i == 1:
                if abs(float(s)) < 1e-12:
                    continue
                of1_c += s + " * x + "
                of1_py += s + " * x + "
            else:
                if abs(float(s)) < 1e-12:
                    continue
                of1_c += s + " * pow(x, %s) + " % i
                of1_py += s + " * x**%s + " % i
        of1_c = of1_c[:-3]
        of1_py = of1_py[:-3]
        of1_c = of1_c.replace("+-", "-").replace("+ -", "-")
        of1_py = of1_py.replace("+-", "-").replace("+ -", "-")
        of1_f = of1_py.replace("**", "^")
        of1_ps = of1_c.replace("pow", "[math]::pow")
        of1_ps = of1_ps.replace("x", "$x")
        of1_ps = of1_ps.replace("y", "$y")
        of2 = f"r2 = {r2}"
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
        if len(self.fit_class.params) <= 0:
            QMessageBox.warning(self, self.tr("输入错误"), self.tr("请先进行拟合"))
            return
        x_list = self.xList.copy()
        qDebug("length of x_list: %s" % len(x_list))
        if self.ui.refineCB.isChecked() and 10 ** self.ui.refineSP.value() > len(
            x_list
        ):
            if self.ui.refineSP.value() > 5:
                btn = QMessageBox.warning(
                    self,
                    self.tr("警告"),
                    self.tr("细化等级太小可能导致进程假死！"),
                    QMessageBox.Ok | QMessageBox.Cancel,
                )
                if btn != QMessageBox.Ok:
                    return
            refine_level = self.ui.refineSP.value()
            x_list = np.linspace(
                x_list[0], x_list[-1], num=10**refine_level, endpoint=True, dtype=float
            ).tolist()
            qDebug("extended length of x_list: %s" % len(x_list))
        yFitList = self.fit_class.ylist(x_list)
        # qDebug("x_list: %s" % x_list)
        # qDebug("yFitList: %s" % yFitList)
        self.ui.tabWidget.setCurrentIndex(1)
        self.onPlotBtnClicked()
        series = QSplineSeries()
        series.setName(self.curveName)
        series.setPen(QPen(self.curveColor, self.curveSize, self.curvePenSytle))
        for i in range(len(x_list)):
            series.append(x_list[i], yFitList[i])
        self.chart.addSeries(series)
        series.attachAxis(self.xAxis)
        series.attachAxis(self.yAxis)
        self.yAxis.setRange(min(yFitList + self.yList), max(yFitList + self.yList))
        self.chartView.show()

    def onCalcYOutClicked(self):
        if len(self.fit_class.params) <= 0:
            QMessageBox.warning(self, self.tr("输入错误"), self.tr("请先进行拟合"))
            return
        try:
            x_value = float(self.ui.xIn.text())
        except ValueError:
            QMessageBox.warning(self, self.tr("输入错误"), self.tr("请输入有效的数字"))
            return
        y_value = self.fit_class.yval(x_value)
        decimals = self.ui.decimalOutBox.value()
        if self.ui.scientificOutCheck.isChecked():
            result = f"{y_value:.{decimals}e}"
        else:
            result = f"{y_value:.{decimals}f}"
        self.ui.yOut.setText(result)
        qDebug("X: %s, Y: %s" % (x_value, y_value))

    def onCalcXOutClicked(self):
        if len(self.fit_class.params) <= 0:
            QMessageBox.warning(self, self.tr("输入错误"), self.tr("请先进行拟合"))
            return
        try:
            target_y = float(self.ui.yIn.text())
        except ValueError:
            QMessageBox.warning(self, self.tr("输入错误"), self.tr("请输入有效的数字"))
            return
        try:
            x_value = self.fit_class.solveval(target_y, limit=False)
            if isinstance(x_value, dict):
                x_value = x_value["x"]  # dict -> list[float]
            qDebug("X: %s, Y: %s" % (x_value, target_y))
            decimals = self.ui.decimalOutBox.value()
            if self.ui.scientificOutCheck.isChecked():
                if isinstance(x_value, float):
                    x_value = f"{x_value:.{decimals}e}"
                else:
                    for i in range(len(x_value)):
                        x_value[i] = f"{x_value[i]:.{decimals}e}"
            else:
                if isinstance(x_value, float):
                    x_value = f"{x_value:.{decimals}f}"
                else:
                    for i in range(len(x_value)):
                        x_value[i] = f"{x_value[i]:.{decimals}f}"
            if isinstance(x_value, str):
                self.ui.xOut.setText(x_value)
            else:
                self.ui.xOut.setText(", ".join(x_value))
        except ValueError:
            QMessageBox.warning(self, self.tr("输入错误"), self.tr("解不存在"))


if __name__ == "__main__":
    """
    test widget
    """
    import sys
    from PySide6.QtWidgets import QApplication

    app = QApplication(sys.argv)
    widget = Widget()
    widget.show()
    sys.exit(app.exec())
