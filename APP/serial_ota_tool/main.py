#!/usr/bin/env python3
"""ESP32-C3 串口调试 & OTA 入口。"""

import sys

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QApplication

from app.mainwindow import APP_TITLE, MainWindow


def main() -> None:
    QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)
    QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps, True)
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
