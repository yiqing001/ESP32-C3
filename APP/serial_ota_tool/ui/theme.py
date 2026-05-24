"""界面主题：白蓝（默认）、黑金、科技蓝。"""

from __future__ import annotations

from PyQt5.QtGui import QColor

# 白蓝：浅色底 + 蓝色强调（对齐 APP/test 与 ota_console 浅色风格）
STYLESHEET_WHITE_BLUE = """
    QMainWindow, QWidget {
        background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
            stop:0 #f5f7fa, stop:1 #ffffff);
        color: #222222;
        font-family: "Microsoft YaHei", "Segoe UI", sans-serif;
    }
    QTabWidget::pane {
        border: 1px solid #dde3ea;
        border-radius: 6px;
        background: #ffffff;
    }
    QTabBar::tab {
        background: #eef2f7;
        color: #555555;
        padding: 8px 20px;
        margin-right: 2px;
        border-top-left-radius: 6px;
        border-top-right-radius: 6px;
    }
    QTabBar::tab:selected {
        background: #ffffff;
        color: #0078D7;
        border: 1px solid #0078D7;
        font-weight: bold;
    }
    QGroupBox {
        background-color: #ffffff;
        border: 1px solid #dde3ea;
        border-radius: 8px;
        margin-top: 12px;
        padding-top: 10px;
        font-weight: bold;
        color: #0078D7;
    }
    QGroupBox::title {
        subcontrol-origin: margin;
        left: 15px;
        padding: 0 8px;
    }
    QLabel { color: #333333; background: transparent; }
    QComboBox, QLineEdit {
        background-color: #ffffff;
        border: 1px solid #c5d0de;
        border-radius: 4px;
        padding: 4px 8px;
        color: #222222;
        min-height: 20px;
    }
    QComboBox:focus, QLineEdit:focus {
        border: 1px solid #0078D7;
    }
    QComboBox QAbstractItemView {
        background-color: #ffffff;
        selection-background-color: #0078D7;
        selection-color: #ffffff;
        color: #222222;
        border: 1px solid #dde3ea;
    }
    QPushButton {
        border-radius: 4px;
        padding: 6px 12px;
        font-weight: bold;
        color: #ffffff;
        min-height: 24px;
        background-color: #0078D7;
        border: 1px solid #0066b8;
    }
    QPushButton:hover {
        background-color: #0091FF;
        border: 1px solid #0078D7;
    }
    QPushButton:disabled {
        background-color: #e8ecf0;
        border: 1px solid #dde3ea;
        color: #999999;
    }
    QPushButton#accentGreen {
        background-color: #00a86b;
        border: 1px solid #00c97a;
        color: #ffffff;
    }
    QPushButton#accentGreen:hover { background-color: #00c97a; }
    QTextEdit {
        background-color: #ffffff;
        border: 1px solid #c5d0de;
        border-radius: 4px;
        padding: 6px;
        color: #1a1a1a;
        font-family: Consolas, "Courier New", monospace;
    }
    QCheckBox { color: #333333; spacing: 8px; }
    QProgressBar {
        border: 1px solid #c5d0de;
        border-radius: 4px;
        text-align: center;
        color: #333333;
        background: #eef2f7;
    }
    QProgressBar::chunk {
        background-color: qlineargradient(x1:0, y1:0, x2:1, y2:0,
            stop:0 #0078D7, stop:1 #00a8ff);
    }
    QSplitter::handle { background-color: #dde3ea; }
    QStatusBar {
        background-color: #eef2f7;
        color: #0078D7;
        border-top: 1px solid #dde3ea;
    }
"""

# 黑金：深黑底 + 金色描边/高亮
STYLESHEET_BLACK_GOLD = """
    QMainWindow, QWidget {
        background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
            stop:0 #0A0A0A, stop:0.5 #12100C, stop:1 #1A1608);
        color: #E8E0D0;
        font-family: "Microsoft YaHei", "Segoe UI", sans-serif;
    }
    QTabWidget::pane {
        border: 1px solid rgba(201, 162, 39, 0.45);
        border-radius: 6px;
        background: rgba(12, 11, 8, 0.92);
    }
    QTabBar::tab {
        background: rgba(28, 24, 16, 0.9);
        color: #A89878;
        padding: 8px 20px;
        margin-right: 2px;
        border-top-left-radius: 6px;
        border-top-right-radius: 6px;
    }
    QTabBar::tab:selected {
        background: rgba(40, 32, 12, 0.95);
        color: #E8C547;
        border: 1px solid #D4AF37;
    }
    QGroupBox {
        background-color: rgba(20, 18, 12, 0.85);
        border: 1px solid rgba(201, 162, 39, 0.5);
        border-radius: 8px;
        margin-top: 12px;
        padding-top: 10px;
        font-weight: bold;
        color: #D4AF37;
    }
    QGroupBox::title {
        subcontrol-origin: margin;
        left: 15px;
        padding: 0 8px;
    }
    QLabel { color: #E8E0D0; background: transparent; }
    QComboBox, QLineEdit {
        background-color: rgba(24, 22, 16, 0.9);
        border: 1px solid rgba(201, 162, 39, 0.45);
        border-radius: 4px;
        padding: 4px 8px;
        color: #F0E6D2;
        min-height: 20px;
    }
    QComboBox QAbstractItemView {
        background-color: rgba(24, 22, 16, 0.98);
        selection-background-color: rgba(80, 60, 20, 0.85);
        color: #F0E6D2;
    }
    QPushButton {
        border-radius: 4px;
        padding: 6px 12px;
        font-weight: bold;
        color: #1A1408;
        min-height: 24px;
        background-color: qlineargradient(x1:0, y1:0, x2:0, y2:1,
            stop:0 #E8C547, stop:1 #B8860B);
        border: 1px solid #D4AF37;
    }
    QPushButton:hover {
        background-color: qlineargradient(x1:0, y1:0, x2:0, y2:1,
            stop:0 #FFD700, stop:1 #D4AF37);
        border: 1px solid #FFE566;
        color: #0A0804;
    }
    QPushButton:disabled {
        background-color: rgba(40, 36, 28, 0.8);
        border: 1px solid rgba(100, 90, 60, 0.4);
        color: #666050;
    }
    QPushButton#accentGreen {
        background-color: #2E7D32;
        border: 1px solid #4CAF50;
        color: #FFFFFF;
    }
    QPushButton#accentGreen:hover { background-color: #43A047; }
    QTextEdit {
        background-color: rgba(16, 14, 10, 0.95);
        border: 1px solid rgba(201, 162, 39, 0.4);
        border-radius: 4px;
        padding: 6px;
        color: #F0E6D2;
        font-family: Consolas, "Courier New", monospace;
    }
    QCheckBox { color: #E8E0D0; spacing: 8px; }
    QProgressBar {
        border: 1px solid rgba(201, 162, 39, 0.45);
        border-radius: 4px;
        text-align: center;
        color: #F0E6D2;
        background: rgba(16, 14, 10, 0.9);
    }
    QProgressBar::chunk {
        background-color: qlineargradient(x1:0, y1:0, x2:1, y2:0,
            stop:0 #B8860B, stop:1 #FFD700);
    }
    QSplitter::handle { background-color: rgba(201, 162, 39, 0.35); }
    QStatusBar {
        background-color: rgba(16, 14, 10, 0.95);
        color: #D4AF37;
        border-top: 1px solid rgba(201, 162, 39, 0.45);
    }
"""

# 科技蓝：原紫蓝青配色（备用主题）
STYLESHEET_TECH_BLUE = """
    QMainWindow, QWidget {
        background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #121212, stop:1 #1A1A2E);
        color: #E0E0E0;
        font-family: "Microsoft YaHei", "Segoe UI", sans-serif;
    }
    QTabWidget::pane {
        border: 1px solid rgba(40, 40, 80, 0.8);
        border-radius: 6px;
        background: rgba(18, 18, 30, 0.9);
    }
    QTabBar::tab {
        background: rgba(30, 30, 60, 0.8);
        color: #B0B0B0;
        padding: 8px 20px;
        margin-right: 2px;
        border-top-left-radius: 6px;
        border-top-right-radius: 6px;
    }
    QTabBar::tab:selected {
        background: rgba(10, 36, 99, 0.9);
        color: #00E5FF;
        border: 1px solid #00E5FF;
    }
    QGroupBox {
        background-color: rgba(26, 26, 46, 0.8);
        border: 1px solid rgba(40, 40, 80, 0.8);
        border-radius: 8px;
        margin-top: 12px;
        padding-top: 10px;
        font-weight: bold;
        color: #00E5FF;
    }
    QGroupBox::title {
        subcontrol-origin: margin;
        left: 15px;
        padding: 0 8px;
    }
    QLabel { color: #E0E0E0; background: transparent; }
    QComboBox, QLineEdit {
        background-color: rgba(30, 30, 60, 0.8);
        border: 1px solid rgba(60, 60, 120, 0.8);
        border-radius: 4px;
        padding: 4px 8px;
        color: #E0E0E0;
        min-height: 20px;
    }
    QComboBox QAbstractItemView {
        background-color: rgba(30, 30, 60, 0.95);
        selection-background-color: rgba(10, 36, 99, 0.8);
        color: #E0E0E0;
    }
    QPushButton {
        border-radius: 4px;
        padding: 6px 12px;
        font-weight: bold;
        color: #FFFFFF;
        min-height: 24px;
        background-color: rgba(10, 36, 99, 0.8);
        border: 1px solid #00E5FF;
    }
    QPushButton:hover { background-color: rgba(10, 36, 99, 1); border: 1px solid #00FFFF; }
    QPushButton:disabled {
        background-color: rgba(30, 30, 40, 0.8);
        border: 1px solid rgba(60, 60, 80, 0.8);
        color: #666666;
    }
    QPushButton#accentGreen {
        background-color: #00C853;
        border: 1px solid #00E676;
    }
    QPushButton#accentGreen:hover { background-color: #00E676; }
    QTextEdit {
        background-color: rgba(30, 30, 60, 0.8);
        border: 1px solid rgba(60, 60, 120, 0.8);
        border-radius: 4px;
        padding: 6px;
        color: #E0E0E0;
        font-family: Consolas, "Courier New", monospace;
    }
    QCheckBox { color: #E0E0E0; spacing: 8px; }
    QProgressBar {
        border: 1px solid rgba(60, 60, 120, 0.8);
        border-radius: 4px;
        text-align: center;
        color: #E0E0E0;
    }
    QProgressBar::chunk { background-color: #00E5FF; }
    QSplitter::handle { background-color: rgba(40, 40, 80, 0.5); }
    QStatusBar {
        background-color: rgba(26, 26, 46, 0.8);
        color: #00E5FF;
        border-top: 1px solid rgba(40, 40, 80, 0.8);
    }
"""

THEMES: dict[str, dict] = {
    "白蓝": {
        "stylesheet": STYLESHEET_WHITE_BLUE,
        "window": QColor(245, 247, 250),
    },
    "黑金": {
        "stylesheet": STYLESHEET_BLACK_GOLD,
        "window": QColor(10, 10, 8),
    },
    "科技蓝": {
        "stylesheet": STYLESHEET_TECH_BLUE,
        "window": QColor(18, 18, 30),
    },
}

DEFAULT_THEME = "白蓝"

# 兼容旧引用
APP_STYLESHEET = STYLESHEET_WHITE_BLUE


def theme_names() -> list[str]:
    return list(THEMES.keys())


def get_stylesheet(name: str) -> str:
    return THEMES.get(name, THEMES[DEFAULT_THEME])["stylesheet"]


def get_window_color(name: str) -> QColor:
    return THEMES.get(name, THEMES[DEFAULT_THEME])["window"]
