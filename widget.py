# This Python file uses the following encoding: utf-8
import re
import csv
import numpy as np
import scipy.optimize as opt

from PySide6.QtWidgets import (
    QApplication,
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
    QPixmap,
    #    QIcon,
)
from PySide6.QtCore import (
    Qt,
    QSize,
    QRect,
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
        self.ui.xDataBtn.clicked.connect(self.onXDataBtnClicked)
        self.ui.xLabelBtn.clicked.connect(self.onXLabelBtnClicked)
        self.ui.yDataBtn.clicked.connect(self.onYDataBtnClicked)
        self.ui.yLabelBtn.clicked.connect(self.onYLabelBtnClicked)
        self.ui.plotBtn.clicked.connect(self.onPlotBtnClicked)
        self.ui.setPlotSizeBtn.clicked.connect(self.onSetPlotSizeBtn)
        self.ui.adjustPlotBtn.clicked.connect(self.onAdjustPlotBtnClicked)
        self.ui.savePlotBtn.clicked.connect(self.onSavePlotBtnClicked)
        self.ui.setPlotBtn.clicked.connect(self.onSetPlotBtnClicked)
        self.ui.loadBtn.clicked.connect(self.onLoadBtnClicked)
        self.ui.saveBtn.clicked.connect(self.onSaveBtnClicked)
        self.ui.moveUpBtn.clicked.connect(self.onMoveUpBtnClicked)
        self.ui.moveDownBtn.clicked.connect(self.onMoveDownBtnClicked)
        self.ui.insertPreBtn.clicked.connect(self.onInsertPreBtnClicked)
        self.ui.insertNextBtn.clicked.connect(self.onInsertNextBtnClicked)
        self.ui.addRowBtn.clicked.connect(self.onAddRowBtnClicked)
        self.ui.removeRowBtn.clicked.connect(self.onRemoveRowBtnClicked)
        self.ui.exchangeBtn.clicked.connect(self.onExchangeBtnClicked)
        self.ui.refreshBtn.clicked.connect(self.onRefreshBtnClicked)
        self.ui.sortBtn.clicked.connect(self.onSortBtnClicked)
        self.ui.reverseBtn.clicked.connect(self.onReverseBtnClicked)
        self.ui.transCheck.toggled.connect(self.onTransCheckToggled)
        self.ui.fitBtn.clicked.connect(self.onFitBtnClicked)
        self.ui.curveBtn.clicked.connect(self.onCurveBtnClicked)
        self.ui.calcYOut.clicked.connect(self.onCalcYOutClicked)
        self.ui.calcXOut.clicked.connect(self.onCalcXOutClicked)
        self.ui.xDataPasteBtn.clicked.connect(self.onXDataPasteBtnClicked)
        self.ui.yDataPasteBtn.clicked.connect(self.onYDataPasteBtnClicked)
        self.ui.xLabelPasteBtn.clicked.connect(self.onXLabelPasteBtnClicked)
        self.ui.yLabelPasteBtn.clicked.connect(self.onYLabelPasteBtnClicked)
        self.ui.comboBox.currentIndexChanged.connect(self.onComboBoxChanged)
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
        self.plotTitle: str = self.ui.titleIn.text()
        self.xLabel: str = self.ui.xLabelIn.text()
        self.yLabel: str = self.ui.yLabelIn.text()
        self.xList: list = []
        self.yList: list = []
        self.aCoeff: list = []
        # plot vars
        self.dataName = "Data Series"
        self.curveName = "Fitted Curve"
        self.dataColor = QColor(Qt.red)
        self.curveColor = QColor(Qt.black)
        self.dataColorTemp = QColor(Qt.red)
        self.curveColorTemp = QColor(Qt.black)
        self.dataSize = 2
        self.curveSize = 2
        self.dataPenStyle = Qt.PenStyle.SolidLine
        self.curvePenSytle = Qt.PenStyle.DashLine
        # initialize default data
        self.onXDataBtnClicked()
        self.onYDataBtnClicked()
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
            self.tr("关于..."),
            self.tr("...声明...\n"
            ),
        )

    def onQtBtnClicked(self):
        QMessageBox.aboutQt(self, self.tr("Qt版本"))

    def copyTextToQLineEdit(self, widget: QLineEdit):
        clipboard = QApplication.clipboard()
        str = clipboard.text()
        widget.setText(str)

    def onXDataPasteBtnClicked(self):
        self.copyTextToQLineEdit(self.ui.xDataIn)

    def onYDataPasteBtnClicked(self):
        self.copyTextToQLineEdit(self.ui.yDataIn)

    def onXLabelPasteBtnClicked(self):
        self.copyTextToQLineEdit(self.ui.xLabelIn)

    def onYLabelPasteBtnClicked(self):
        self.copyTextToQLineEdit(self.ui.yLabelIn)

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
            print("ChartView size:", self.chartView.size())

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
        print("ChartView size:", self.chartView.size())

    def onSavePlotBtnClicked(self):
        options = QFileDialog.Options()
        options |= QFileDialog.ReadOnly
        fileName, _ = QFileDialog.getSaveFileName(
            self,
            self.tr("保存绘图"),
            self.plotTitle,
            self.tr("SVG Files (*.svg);;PNG Files (*.png);;All Files (*)"),
            options=options,
        )
        cv = self.chartView
        if fileName:
            if fileName.endswith(".png"):
                cv.grab().save(fileName)
                print("Save PNG file:", fileName)
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
                print("Save SVG file:", fileName)
            else:
                QMessageBox.warning(
                    self, self.tr("保存失败"), self.tr("不支持的文件格式")
                )
            QMessageBox.information(
                self, self.tr("保存成功"), self.tr(f"图表已保存为 {fileName}")
            )

    def onExchangeBtnClicked(self):
        self.xList, self.yList = self.yList, self.xList
        self.appendListToTable(self.xList, 0)
        self.appendListToTable(self.yList, 1)
        self.xLabel, self.yLabel = self.yLabel, self.xLabel
        self.ui.xLabelIn.setText(self.xLabel)
        self.ui.yLabelIn.setText(self.yLabel)
        self.onXLabelBtnClicked()
        self.onYLabelBtnClicked()
        self.onRefreshBtnClicked()

    def disableTransCheck(self):
        if self.ui.transCheck.isChecked():
            self.ui.transCheck.setChecked(False)

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

    def appendListToTable(
        self,
        input_list: list,
        pos: int,
        decimal_places: int = 2,
        scientific: bool = False,
    ):
        num_rows = self.ui.inputTable.rowCount()
        if num_rows < len(input_list):
            self.ui.inputTable.setRowCount(len(input_list))
        for i in range(self.ui.inputTable.rowCount()):
            if i >= len(input_list):
                self.ui.inputTable.setItem(i, pos, QTableWidgetItem(""))
            else:
                if scientific:
                    self.ui.inputTable.setItem(
                        i, pos, QTableWidgetItem(f"{input_list[i]:.{decimal_places}e}")
                    )
                else:
                    self.ui.inputTable.setItem(
                        i, pos, QTableWidgetItem(f"{input_list[i]:.{decimal_places}f}")
                    )
        self.clearEmptyRowsOfTableEnd(self.ui.inputTable.rowCount())

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

    def onXDataBtnClicked(self):
        self.xList = self.filterStringToList(self.ui.xDataIn.text())
        if not self.xList:
            QMessageBox.warning(
                self,
                self.tr("输入错误"),
                self.tr("未找到有效数字，请检查X轴数据格式"),
            )
            return
        self.disableTransCheck()
        print("xData: ", self.xList)
        self.appendListToTable(
            self.xList,
            0,
            self.ui.decimalXBox.value(),
            self.ui.scientificXCheck.isChecked(),
        )

    def onYDataBtnClicked(self):
        self.yList = self.filterStringToList(self.ui.yDataIn.text())
        if not self.yList:
            QMessageBox.warning(
                self,
                self.tr("输入错误"),
                self.tr("未找到有效数字，请检查Y轴数据格式"),
            )
            return
        self.disableTransCheck()
        print("yData: ", self.yList)
        self.appendListToTable(
            self.yList,
            1,
            self.ui.decimalYBox.value(),
            self.ui.scientificYCheck.isChecked(),
        )

    def onXLabelBtnClicked(self):
        if not self.ui.xLabelIn.text():
            QMessageBox.warning(self, self.tr("输入错误"), self.tr("X轴标签不能为空"))
            return
        self.disableTransCheck()
        self.xLabel = self.ui.xLabelIn.text()
        print("xLabel: ", self.xLabel)
        self.ui.inputTable.setHorizontalHeaderLabels([self.xLabel, self.yLabel])

    def onYLabelBtnClicked(self):
        if not self.ui.yLabelIn.text():
            QMessageBox.warning(self, self.tr("输入错误"), self.tr("Y轴标签不能为空"))
            return
        self.disableTransCheck()
        self.yLabel = self.ui.yLabelIn.text()
        print("yLabel: ", self.yLabel)
        self.ui.inputTable.setHorizontalHeaderLabels([self.xLabel, self.yLabel])

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
        self.disableTransCheck()
        self.chart.removeAllSeries()
        # Clear existing axes
        if self.xAxis in self.chart.axes():
            self.chart.removeAxis(self.xAxis)
        if self.yAxis in self.chart.axes():
            self.chart.removeAxis(self.yAxis)
        # Create new axes
        axis_x = self.xAxis
        axis_x.setTitleText(self.xLabel)
        axis_x.setRange(min(self.xList), max(self.xList))
        if self.ui.scientificXCheck.isChecked():
            axis_x.setLabelFormat("%.{}e".format(self.ui.decimalXBox.value()))
        else:
            axis_x.setLabelFormat("%.{}f".format(self.ui.decimalXBox.value()))
        axis_y = self.yAxis
        axis_y.setTitleText(self.yLabel)
        axis_y.setRange(min(self.yList), max(self.yList))
        if self.ui.scientificYCheck.isChecked():
            axis_y.setLabelFormat("%.{}e".format(self.ui.decimalYBox.value()))
        else:
            axis_y.setLabelFormat("%.{}f".format(self.ui.decimalYBox.value()))
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
                if len(rows[0]) != 2:
                    QMessageBox.critical(
                        self,
                        self.tr("格式错误"),
                        self.tr("CSV必须也只能包含2列数据"),
                    )
                    return
                x_label, y_label = rows[0]
                data_rows = rows[1:]
                x_data = []
                y_data = []
                for i, row in enumerate(data_rows, start=1):
                    if len(row) != 2:
                        QMessageBox.critical(
                            self,
                            self.tr("数据错误"),
                            self.tr(f"第{i}行数据不完整"),
                        )
                        return
                    try:
                        x_val = float(row[0])
                        y_val = float(row[1])
                    except ValueError:
                        QMessageBox.critical(
                            self,
                            self.tr("转换错误"),
                            self.tr(f"第{i}行包含非数字数据"),
                        )
                        return
                    x_data.append(x_val)
                    y_data.append(y_val)
                self.ui.xLabelIn.setText(x_label)
                self.ui.yLabelIn.setText(y_label)
                self.onXLabelBtnClicked()
                self.onYLabelBtnClicked()
                self.xList = x_data
                self.yList = y_data
                self.appendListToTable(
                    x_data,
                    0,
                    self.ui.decimalXBox.value(),
                    self.ui.scientificXCheck.isChecked(),
                )
                self.appendListToTable(
                    y_data,
                    1,
                    self.ui.decimalYBox.value(),
                    self.ui.scientificYCheck.isChecked(),
                )
                self.onRefreshBtnClicked()
        except Exception as e:
            QMessageBox.critical(
                self, self.tr("加载错误"), self.tr(f"加载文件失败：{str(e)}")
            )

    def onSaveBtnClicked(self):
        if (
            not self.onRefreshBtnClicked()
        ):  # Ensure the table is up-to-date before saving
            return
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
                if self.ui.transCheck.isChecked():
                    self.ui.transCheck.setChecked(False)
                headers = [
                    self.ui.inputTable.horizontalHeaderItem(i).text()
                    for i in range(self.ui.inputTable.columnCount())
                ]
                writer.writerow(headers)
                # deal row data
                for row in range(self.ui.inputTable.rowCount()):
                    row_data = []
                    for col in range(self.ui.inputTable.columnCount()):
                        item = self.ui.inputTable.item(row, col)
                        row_data.append(item.text() if item else "")
                    writer.writerow(row_data)

            QMessageBox.information(
                self, self.tr("保存成功"), self.tr(f"文件已保存至：{path}")
            )
        except Exception as e:
            QMessageBox.critical(
                self,
                self.tr("保存错误"),
                self.tr(f"保存文件时出现错误：{str(e)}"),
            )

    def onMoveUpBtnClicked(self):
        selected_list = self.getSelectedRowsList()
        if not selected_list:
            QMessageBox.warning(
                self, self.tr("移动错误"), self.tr("请先选择要移动的行")
            )
            return
        if min(selected_list) == 0:
            QMessageBox.warning(
                self, self.tr("移动错误"), self.tr("不能将第一行向上移动")
            )
            return
        if len(selected_list) > 1:
            QMessageBox.warning(self, self.tr("移动错误"), self.tr("不能同时移动多行"))
            return
        for i in selected_list:
            i = i + 1
            self.ui.inputTable.insertRow(i - 2)
            for j in range(self.ui.inputTable.columnCount()):
                item = self.ui.inputTable.takeItem(i, j)
                self.ui.inputTable.setItem(i - 2, j, item)
            self.ui.inputTable.removeRow(i)
            print("Move row: ", i, "to", i - 1)
            self.ui.inputTable.selectRow(i - 2)

    def onMoveDownBtnClicked(self):
        selected_list = self.getSelectedRowsList()
        if not selected_list:
            QMessageBox.warning(
                self, self.tr("移动错误"), self.tr("请先选择要移动的行")
            )
            return
        if max(selected_list) == self.ui.inputTable.rowCount() - 1:
            QMessageBox.warning(
                self, self.tr("移动错误"), self.tr("不能将最后一行向下移动")
            )
            return
        if len(selected_list) > 1:
            QMessageBox.warning(self, self.tr("移动错误"), self.tr("不能同时移动多行"))
            return
        for i in selected_list:
            self.ui.inputTable.insertRow(i + 2)
            for j in range(self.ui.inputTable.columnCount()):
                item = self.ui.inputTable.takeItem(i, j)
                self.ui.inputTable.setItem(i + 2, j, item)
            self.ui.inputTable.removeRow(i)
            print("Move row: ", i + 1, "to", i + 2)
            self.ui.inputTable.selectRow(i + 1)

    def onInsertPreBtnClicked(self):
        selected_list = self.getSelectedRowsList()
        if not selected_list:
            QMessageBox.warning(
                self, self.tr("插入错误"), self.tr("请先选择要插入的位置")
            )
            return
        row_num = min(selected_list)
        self.ui.inputTable.insertRow(row_num)
        print("Insert row: ", row_num + 1)
        self.renumberTableRows()

    def onInsertNextBtnClicked(self):
        selected_list = self.getSelectedRowsList()
        if not selected_list:
            QMessageBox.warning(
                self, self.tr("插入错误"), self.tr("请先选择要插入的位置")
            )
            return
        row_num = max(selected_list)
        self.ui.inputTable.insertRow(row_num + 1)
        print("Insert row: ", row_num + 2)
        self.renumberTableRows()

    def onAddRowBtnClicked(self):
        num_rows = self.ui.inputTable.rowCount()
        self.ui.inputTable.setRowCount(num_rows + 1)
        self.ui.inputTable.setItem(num_rows, 0, QTableWidgetItem(""))
        self.ui.inputTable.setItem(num_rows, 1, QTableWidgetItem(""))
        self.renumberTableRows()
        print(f"Row {num_rows + 1} added.")

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

    def onRemoveRowBtnClicked(self):
        remove_list = self.getSelectedRowsList()
        if not remove_list:
            QMessageBox.warning(
                self, self.tr("删除错误"), self.tr("请先选择要删除的行")
            )
            return
        remove_list.sort(reverse=True)
        for i in remove_list:
            self.ui.inputTable.removeRow(i)
            print(f"Row {i} removed.")
        self.renumberTableRows()

    def textToFloat(self, text: str):
        b: bool = True
        f: float = 0.0
        try:
            f = float(text)
        except ValueError:
            f = float("NaN")
            b = False
        return f, b

    def renumberTableRows(self):
        for i in range(self.ui.inputTable.rowCount()):
            self.ui.inputTable.setVerticalHeaderItem(i, QTableWidgetItem(f"{i + 1}"))

    def onRefreshBtnClicked(self) -> bool:
        xlabel = self.ui.inputTable.horizontalHeaderItem(0).text()
        ylabel = self.ui.inputTable.horizontalHeaderItem(1).text()
        if not xlabel or not ylabel:
            QMessageBox.warning(
                self, self.tr("输入错误"), self.tr("X轴和Y轴标签不能为空")
            )
            return False
        xList = []
        yList = []
        for row in range(self.ui.inputTable.rowCount()):
            try:
                x_value, x_valid = self.textToFloat(
                    self.ui.inputTable.item(row, 0).text()
                )
                y_value, y_valid = self.textToFloat(
                    self.ui.inputTable.item(row, 1).text()
                )
            except AttributeError:
                continue
            if x_valid:
                xList.append(x_value)
            if y_valid:
                yList.append(y_value)
        if len(xList) == 0 or len(yList) == 0:
            QMessageBox.warning(
                self, self.tr("输入错误"), self.tr("X轴和Y轴数据不能为空")
            )
            return False
        if len(xList) != len(yList):
            QMessageBox.warning(
                self, self.tr("输入错误"), self.tr("X轴和Y轴数据长度不一致")
            )
            return False
        self.xLabel = xlabel
        self.yLabel = ylabel
        self.xList = xList
        self.yList = yList
        self.ui.xLabelIn.setText(self.xLabel)
        self.ui.yLabelIn.setText(self.yLabel)
        self.ui.xDataIn.setText(", ".join(map(str, self.xList)))
        self.ui.yDataIn.setText(", ".join(map(str, self.yList)))
        self.clearEmptyRowsOfTableEnd(self.ui.inputTable.rowCount())
        self.renumberTableRows()
        return True

    def onSortBtnClicked(self):
        if not self.ui.inputTable.selectedItems():
            QMessageBox.warning(self, self.tr("操作错误"), self.tr("请选择要排序的列"))
            return
        selected_list = self.getSelectedColumnsList()
        if not selected_list:
            return
        for selected_column in selected_list:
            items = []
            for row in range(self.ui.inputTable.rowCount()):
                item = self.ui.inputTable.item(row, selected_column)
                if item:
                    items.append(item)

            def get_numeric_value(item):
                try:
                    return float(item.text())
                except ValueError:
                    return float("inf")

            items.sort(key=get_numeric_value)
            for row in range(self.ui.inputTable.rowCount()):
                self.ui.inputTable.takeItem(row, selected_column)
            for new_row, item in enumerate(items):
                self.ui.inputTable.setItem(new_row, selected_column, item)

    def onReverseBtnClicked(self):
        if not self.ui.inputTable.selectedItems():
            QMessageBox.warning(self, self.tr("操作错误"), self.tr("请选择反序的列"))
            return
        selected_list = self.getSelectedColumnsList()
        if not selected_list:
            return
        for selected_column in selected_list:
            items = []
            for row in range(self.ui.inputTable.rowCount()):
                item = self.ui.inputTable.item(row, selected_column)
                if item:
                    items.append(item)
            items = items[::-1]
            for row in range(self.ui.inputTable.rowCount()):
                self.ui.inputTable.takeItem(row, selected_column)
            for new_row, item in enumerate(items):
                self.ui.inputTable.setItem(new_row, selected_column, item)

    def onTransCheckToggled(self, checked):
        if checked:
            self.ui.inputTable.clearContents()
            self.ui.inputTable.setRowCount(2)
            self.ui.inputTable.setVerticalHeaderLabels([self.xLabel, self.yLabel])
            num_clos = max(len(self.xList), len(self.yList))
            self.ui.inputTable.setColumnCount(num_clos)
            hhead: list = []
            for i in range(num_clos):
                hhead.append(f"{i + 1}")
                if i < len(self.xList):
                    if self.ui.scientificXCheck.isChecked():
                        self.ui.inputTable.setItem(
                            0,
                            i,
                            QTableWidgetItem(
                                f"{self.xList[i]:.{self.ui.decimalXBox.value()}e}"
                            ),
                        )
                    else:
                        self.ui.inputTable.setItem(
                            0,
                            i,
                            QTableWidgetItem(
                                f"{self.xList[i]:.{self.ui.decimalXBox.value()}f}"
                            ),
                        )
                else:
                    self.ui.inputTable.setItem(0, i, QTableWidgetItem(""))
                if i < len(self.yList):
                    if self.ui.scientificYCheck.isChecked():
                        self.ui.inputTable.setItem(
                            1,
                            i,
                            QTableWidgetItem(
                                f"{self.yList[i]:.{self.ui.decimalYBox.value()}e}"
                            ),
                        )
                    else:
                        self.ui.inputTable.setItem(
                            1,
                            i,
                            QTableWidgetItem(
                                f"{self.yList[i]:.{self.ui.decimalYBox.value()}f}"
                            ),
                        )
                else:
                    self.ui.inputTable.setItem(i, 1, QTableWidgetItem(""))
            self.ui.inputTable.setHorizontalHeaderLabels(hhead)
        else:
            self.ui.inputTable.clearContents()
            self.ui.inputTable.setColumnCount(2)
            self.ui.inputTable.setHorizontalHeaderLabels([self.xLabel, self.yLabel])
            num_rows = max(len(self.xList), len(self.yList))
            self.ui.inputTable.setRowCount(num_rows)
            vhead: list = []
            for i in range(num_rows):
                vhead.append(f"{i + 1}")
                if i < len(self.xList):
                    if self.ui.scientificXCheck.isChecked():
                        self.ui.inputTable.setItem(
                            i,
                            0,
                            QTableWidgetItem(
                                f"{self.xList[i]:.{self.ui.decimalXBox.value()}e}"
                            ),
                        )
                    else:
                        self.ui.inputTable.setItem(
                            i,
                            0,
                            QTableWidgetItem(
                                f"{self.xList[i]:.{self.ui.decimalXBox.value()}f}"
                            ),
                        )
                else:
                    self.ui.inputTable.setItem(i, 0, QTableWidgetItem(""))
                if i < len(self.yList):
                    if self.ui.scientificYCheck.isChecked():
                        self.ui.inputTable.setItem(
                            i,
                            1,
                            QTableWidgetItem(
                                f"{self.yList[i]:.{self.ui.decimalYBox.value()}e}"
                            ),
                        )
                    else:
                        self.ui.inputTable.setItem(
                            i,
                            1,
                            QTableWidgetItem(
                                f"{self.yList[i]:.{self.ui.decimalYBox.value()}f}"
                            ),
                        )
                else:
                    self.ui.inputTable.setItem(i, 1, QTableWidgetItem(""))
            self.ui.inputTable.setVerticalHeaderLabels(vhead)

    def onComboBoxChanged(self):
        text: str = None
        if self.ui.comboBox.currentIndex() == 0:
            self.ui.numberSpin.setEnabled(True)
            self.ui.interceptCheck.setEnabled(True)
            self.ui.interceptIn.setEnabled(self.ui.interceptCheck.isChecked())
            print("Function: polynomial")
            text = "y = a<sub>0</sub> + a<sub>1</sub>x + a<sub>2</sub>x<sup>2</sup> + ... + a<sub>n</sub>x<sup>n</sup>"
        else:
            self.ui.numberSpin.setEnabled(False)
            self.ui.interceptCheck.setEnabled(False)
            self.ui.interceptIn.setEnabled(False)
            if self.ui.comboBox.currentIndex() == 1:
                print("Function: exponential")
                text = (
                    "y = a<sub>0</sub> + a<sub>1</sub>e<span>^(a<sub>2</sub>x)</span>"
                )
            elif self.ui.comboBox.currentIndex() == 2:
                print("Function: logarithmic")
                text = "y = a<sub>0</sub> + a<sub>1</sub>ln(x)"
            elif self.ui.comboBox.currentIndex() == 3:
                print("Function: power")
                text = "y = a<sub>0</sub>x<span>^(a<sub>1</sub>)</span>"
        if text:
            self.ui.funcLabel.setText(text)

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
        print("xList: ", xlist)
        print("yList: ", ylist)

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
        print("Fitted coefficients: ", self.aCoeff)
        print("R-squared: ", r_squared)
        self.updateOutputTable(r_squared)
        # update text output
        of1_c = f"y={str(self.ui.outputTable.item(1, 0).text())}*pow(x,{str(self.ui.outputTable.item(2, 0).text())})"
        of1_py = f"y={str(self.ui.outputTable.item(1, 0).text())}*x**{str(self.ui.outputTable.item(2, 0).text())}"
        of1_f = of1_py.replace("**", "^")
        of2 = f"r2={self.ui.outputTable.item(0, 0).text()}"
        of1_ps = of1_c.replace("pow", "[math]::pow")
        of1_ps = of1_ps.replace("x", "$x")
        of1_ps = of1_ps.replace("y", "$y")
        print("Output formula: ", of1_f)
        print("Output r2: ", of2)
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
        print("xList: ", xlist)
        print("yList: ", ylist)

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
        print("Fitted coefficients: ", self.aCoeff)
        print("R-squared: ", r_squared)
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
        print("Output formula: ", of1_f)
        print("Output r2: ", of2)
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
        print("xList: ", xlist)
        print("yList: ", ylist)

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
        print("Fitted coefficients: ", self.aCoeff)
        print("R-squared: ", r_squared)
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
        print("Output formula: ", of1_f)
        print("Output r2: ", of2)
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
        print("xList: ", xlist)
        print("yList: ", ylist)
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
        print("Fitted coefficients: ", self.aCoeff)
        print("R-squared: ", r_squared)
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
        print("Output formula: ", of1_f)
        print("Output r2: ", of2)
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
        print("X:", x_value, "Y:", y_value)

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
        print("X:", x_init, "Y:", target_y, "LoopNum:", n)
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
