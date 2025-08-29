# -*- coding: utf-8 -*-

import sys
import pathlib
import argparse

from .widget import Widget
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import (
    QTranslator,
    QLocale,
    qDebug,
)


class MApp(QApplication):
    def __init__(self, argv, language=None):
        super().__init__(argv)
        self.translator = QTranslator()
        if language:
            locale = language
        else:
            locale = QLocale.system().name()
        folder = pathlib.Path(__file__).parent.resolve()
        if locale == "zh_CN":
            translation_file = f"{folder}/translations/PyCFF_zh_CN.qm"
            qDebug(f"locale: {locale}")
        elif locale == "en":
            translation_file = f"{folder}/translations/PyCFF_en.qm"
            qDebug(f"locale: {locale}")
        else:
            translation_file = f"{folder}/translations/PyCFF_en.qm"
            qDebug("no locale, use default")
        if self.translator.load(translation_file):
            qDebug(f"load translation file: {translation_file}")
            self.installTranslator(self.translator)
        else:
            qDebug(f"load translation file failed: {translation_file}")

def run_app():
    parser = argparse.ArgumentParser(description="PyCFF Application")
    parser.add_argument(
        "-l",
        "--locale",
        help="set locale (e.g. zh_CN for Simplified Chinese, en for English)",
        type=str,
    )
    args = parser.parse_args()
    app = MApp(sys.argv, language=args.locale)
    widget = Widget()
    widget.show()
    widget.onAdjustPlotBtnClicked()
    sys.exit(app.exec())

if __name__ == "__main__":
    run_app()
    
    