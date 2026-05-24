"""主窗口：串口调试 + OTA（架构借鉴 APP/test，OTA 为 ESP32-C3 专用）。"""

from __future__ import annotations

import os
import sys
from pathlib import Path

import serial
from PyQt5.QtCore import QDateTime, Qt, QThread, pyqtSignal
from PyQt5.QtGui import QFont, QPalette, QColor
from PyQt5.QtWidgets import (
    QApplication,
    QCheckBox,
    QComboBox,
    QFileDialog,
    QGridLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMainWindow,
    QMessageBox,
    QProgressBar,
    QPushButton,
    QSplitter,
    QStatusBar,
    QTabWidget,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from core.hex_util import bytes_to_hex, hex_str_to_bytes
from core.ota_client import (
    DeviceInfo,
    build_host_candidates,
    fetch_device_info,
    scan_subnet,
    upload_firmware,
)
from core.serial_io import (
    BAUD_RATES,
    list_serial_ports,
    open_serial_port,
    parity_from_text,
    stopbits_from_text,
)
from core.serial_thread import SerialReadThread
from ui.theme import DEFAULT_THEME, get_stylesheet, get_window_color, theme_names

APP_TITLE = "ESP32-C3 串口调试 & OTA"
EOL_MAP = {"无": b"", "\\n": b"\n", "\\r": b"\r", "\\r\\n": b"\r\n"}


class OtaWorkerThread(QThread):
    """后台 OTA 任务，避免阻塞界面。"""

    log_line = pyqtSignal(str)
    find_done = pyqtSignal(object)
    scan_done = pyqtSignal(list)
    upload_progress = pyqtSignal(int)
    upload_done = pyqtSignal(bool, str)

    def __init__(self, task: str, **kwargs) -> None:
        super().__init__()
        self._task = task
        self._kwargs = kwargs

    def run(self) -> None:
        if self._task == "find":
            hosts = self._kwargs["hosts"]
            for h in hosts:
                self.log_line.emit(f"尝试: {h}")
                info = fetch_device_info(h)
                if info:
                    self.find_done.emit(info)
                    return
            self.find_done.emit(None)
        elif self._task == "scan":
            prefix = self._kwargs["prefix"]
            self.log_line.emit(f"扫描 {prefix}.1-254 ...")
            devices = scan_subnet(prefix)
            self.scan_done.emit(devices)
        elif self._task == "upload":
            ip = self._kwargs["ip"]
            path = self._kwargs["path"]

            def on_prog(sent: int, total: int) -> None:
                pct = int(sent * 100 / total) if total else 0
                self.upload_progress.emit(pct)

            try:
                self.log_line.emit(f"上传 {path.name} ({path.stat().st_size} B)")
                msg = upload_firmware(ip, path, on_prog)
                self.upload_done.emit(True, msg)
            except Exception as exc:
                self.upload_done.emit(False, str(exc))


class MainWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self._serial = serial.Serial()
        self._read_thread: SerialReadThread | None = None
        self._rx_count = 0
        self._tx_count = 0
        self._device: DeviceInfo | None = None
        self._bin_path: Path | None = None
        self._ota_worker: OtaWorkerThread | None = None

        self._init_ui()
        self._apply_theme(DEFAULT_THEME)
        self._refresh_ports()

    def _init_ui(self) -> None:
        self.setWindowTitle(APP_TITLE)
        self.setMinimumSize(1100, 720)
        QApplication.setFont(QFont("Microsoft YaHei", 9))

        root = QWidget()
        root_layout = QVBoxLayout(root)
        root_layout.setContentsMargins(6, 6, 6, 0)
        root_layout.setSpacing(6)

        self._tabs = QTabWidget()
        self._tabs.addTab(self._build_serial_tab(), "串口调试")
        self._tabs.addTab(self._build_ota_tab(), "OTA 升级")
        self._tabs.addTab(self._build_settings_tab(), "设置")
        root_layout.addWidget(self._tabs)
        self.setCentralWidget(root)

        self._status = QStatusBar()
        self.setStatusBar(self._status)
        self._status_serial = QLabel("串口：未打开")
        self._status_count = QLabel("接收：0 B | 发送：0 B")
        self._status.addWidget(self._status_serial)
        self._status.addPermanentWidget(self._status_count)

    def _apply_theme(self, name: str) -> None:
        if name not in theme_names():
            return
        self.setStyleSheet(get_stylesheet(name))
        palette = self.palette()
        palette.setColor(QPalette.Window, get_window_color(name))
        self.setPalette(palette)

    def _build_serial_tab(self) -> QWidget:
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setSpacing(10)
        layout.setContentsMargins(10, 10, 10, 10)

        cfg = QGroupBox("串口配置")
        cfg.setMaximumHeight(88)
        grid = QGridLayout(cfg)
        grid.addWidget(QLabel("端口"), 0, 0)
        self._port_combo = QComboBox()
        self._port_combo.setMinimumWidth(200)
        grid.addWidget(self._port_combo, 0, 1)
        self._refresh_btn = QPushButton("刷新")
        self._refresh_btn.setMaximumWidth(80)
        self._refresh_btn.clicked.connect(self._refresh_ports)
        grid.addWidget(self._refresh_btn, 0, 2)

        grid.addWidget(QLabel("波特率"), 0, 3)
        self._baud_combo = QComboBox()
        self._baud_combo.addItems(list(BAUD_RATES))
        self._baud_combo.setCurrentText("115200")
        grid.addWidget(self._baud_combo, 0, 4)

        grid.addWidget(QLabel("数据位"), 0, 5)
        self._data_combo = QComboBox()
        self._data_combo.addItems(["8", "7", "6", "5"])
        grid.addWidget(self._data_combo, 0, 6)

        grid.addWidget(QLabel("停止位"), 0, 7)
        self._stop_combo = QComboBox()
        self._stop_combo.addItems(["1", "1.5", "2"])
        grid.addWidget(self._stop_combo, 0, 8)

        grid.addWidget(QLabel("校验"), 0, 9)
        self._parity_combo = QComboBox()
        self._parity_combo.addItems(["无", "奇校验", "偶校验"])
        grid.addWidget(self._parity_combo, 0, 10)

        self._open_btn = QPushButton("打开串口")
        self._open_btn.setMinimumWidth(100)
        self._open_btn.clicked.connect(self._toggle_serial)
        grid.addWidget(self._open_btn, 0, 11)
        layout.addWidget(cfg)

        splitter = QSplitter(Qt.Horizontal)
        left = QWidget()
        left_l = QVBoxLayout(left)

        send_g = QGroupBox("发送")
        send_l = QVBoxLayout(send_g)
        self._tx_edit = QTextEdit()
        self._tx_edit.setMaximumHeight(100)
        self._tx_edit.setPlaceholderText("文本发送内容")
        send_l.addWidget(self._tx_edit)

        self._hex_cmd = QLineEdit()
        self._hex_cmd.setPlaceholderText("十六进制，如 AA 55 01（优先发送此项若已填写）")
        send_l.addWidget(self._hex_cmd)

        row = QHBoxLayout()
        row.addWidget(QLabel("行尾"))
        self._eol_combo = QComboBox()
        self._eol_combo.addItems(list(EOL_MAP.keys()))
        self._eol_combo.setCurrentText("\\r\\n")
        row.addWidget(self._eol_combo)
        self._hex_rx_chk = QCheckBox("接收十六进制")
        self._hex_rx_chk.setChecked(True)
        row.addWidget(self._hex_rx_chk)
        self._auto_scroll = QCheckBox("自动滚屏")
        self._auto_scroll.setChecked(True)
        row.addWidget(self._auto_scroll)
        send_l.addLayout(row)

        btn_row = QHBoxLayout()
        send_btn = QPushButton("发送")
        send_btn.clicked.connect(self._send_data)
        btn_row.addWidget(send_btn)
        clr_tx = QPushButton("清空发送")
        clr_tx.clicked.connect(self._tx_edit.clear)
        btn_row.addWidget(clr_tx)
        send_l.addLayout(btn_row)
        left_l.addWidget(send_g)

        assist = QGroupBox("辅助")
        assist_l = QHBoxLayout(assist)
        clr_rx = QPushButton("清空接收")
        clr_rx.clicked.connect(self._clear_rx)
        assist_l.addWidget(clr_rx)
        save_btn = QPushButton("保存日志")
        save_btn.clicked.connect(self._save_log)
        assist_l.addWidget(save_btn)
        left_l.addWidget(assist)
        left_l.addStretch()
        splitter.addWidget(left)

        recv_g = QGroupBox("接收")
        recv_l = QVBoxLayout(recv_g)
        self._rx_edit = QTextEdit()
        self._rx_edit.setReadOnly(True)
        self._rx_edit.setFont(QFont("Consolas", 10))
        recv_l.addWidget(self._rx_edit)
        splitter.addWidget(recv_g)
        splitter.setStretchFactor(1, 3)
        layout.addWidget(splitter)
        return page

    def _build_ota_tab(self) -> QWidget:
        page = QWidget()
        layout = QVBoxLayout(page)

        find_g = QGroupBox("设备信息")
        find_l = QGridLayout(find_g)
        self._ota_ip = QLineEdit()
        self._ota_name = QLineEdit()
        self._ota_sn = QLineEdit()
        self._ota_prefix = QLineEdit("MaiQing-C3")
        find_l.addWidget(QLabel("IP"), 0, 0)
        find_l.addWidget(self._ota_ip, 0, 1)
        find_l.addWidget(QLabel("设备名"), 0, 2)
        find_l.addWidget(self._ota_name, 0, 3)
        find_l.addWidget(QLabel("SN"), 1, 0)
        find_l.addWidget(self._ota_sn, 1, 1)
        find_l.addWidget(QLabel("前缀"), 1, 2)
        find_l.addWidget(self._ota_prefix, 1, 3)

        btn_row = QHBoxLayout()
        find_btn = QPushButton("查询设备")
        find_btn.clicked.connect(self._ota_find)
        btn_row.addWidget(find_btn)
        btn_row.addWidget(QLabel("网段"))
        self._ota_subnet = QLineEdit("192.168.1")
        self._ota_subnet.setMaximumWidth(120)
        btn_row.addWidget(self._ota_subnet)
        scan_btn = QPushButton("扫描网段")
        scan_btn.clicked.connect(self._ota_scan)
        btn_row.addWidget(scan_btn)
        find_l.addLayout(btn_row, 2, 0, 1, 4)

        self._ota_dev_label = QLabel("未连接设备")
        self._ota_dev_label.setWordWrap(True)
        find_l.addWidget(self._ota_dev_label, 3, 0, 1, 4)
        layout.addWidget(find_g)

        flash_g = QGroupBox("固件烧录")
        flash_l = QVBoxLayout(flash_g)
        file_row = QHBoxLayout()
        self._bin_label = QLabel("未选择 .bin")
        file_row.addWidget(self._bin_label, 1)
        pick_btn = QPushButton("选择固件")
        pick_btn.clicked.connect(self._pick_bin)
        file_row.addWidget(pick_btn)
        flash_l.addLayout(file_row)

        self._ota_prog = QProgressBar()
        flash_l.addWidget(self._ota_prog)
        self._ota_flash_btn = QPushButton("开始 OTA")
        self._ota_flash_btn.setEnabled(False)
        self._ota_flash_btn.clicked.connect(self._ota_upload)
        flash_l.addWidget(self._ota_flash_btn)

        self._ota_log = QTextEdit()
        self._ota_log.setReadOnly(True)
        self._ota_log.setMaximumHeight(180)
        flash_l.addWidget(self._ota_log)
        layout.addWidget(flash_g)
        layout.addStretch()
        return page

    def _build_settings_tab(self) -> QWidget:
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setSpacing(10)
        layout.setContentsMargins(10, 10, 10, 10)

        theme_g = QGroupBox("界面主题")
        theme_l = QGridLayout(theme_g)
        theme_l.addWidget(QLabel("配色方案"), 0, 0)
        self._theme_combo = QComboBox()
        self._theme_combo.addItems(theme_names())
        self._theme_combo.setCurrentText(DEFAULT_THEME)
        self._theme_combo.setMinimumWidth(160)
        self._theme_combo.setToolTip("切换白蓝 / 黑金 / 科技蓝界面配色")
        self._theme_combo.currentTextChanged.connect(self._apply_theme)
        theme_l.addWidget(self._theme_combo, 0, 1)
        theme_hint = QLabel("白蓝（默认）、黑金、科技蓝；切换后立即生效。")
        theme_hint.setWordWrap(True)
        theme_l.addWidget(theme_hint, 1, 0, 1, 2)
        layout.addWidget(theme_g)
        layout.addStretch()
        return page

    def _ts(self) -> str:
        return QDateTime.currentDateTime().toString("HH:mm:ss.zzz")

    def _update_count(self) -> None:
        self._status_count.setText(f"接收：{self._rx_count} B | 发送：{self._tx_count} B")

    def _refresh_ports(self) -> None:
        self._port_combo.clear()
        ports = list_serial_ports()
        if not ports:
            self._port_combo.addItem("无可用串口")
            return
        for dev, desc in ports:
            self._port_combo.addItem(f"{dev} - {desc}", dev)

    def _port_device(self) -> str:
        data = self._port_combo.currentData()
        if data:
            return str(data)
        text = self._port_combo.currentText()
        return text.split(" - ")[0] if " - " in text else text

    def _toggle_serial(self) -> None:
        if self._serial.is_open:
            self._close_serial()
            return
        port = self._port_device()
        if port == "无可用串口":
            QMessageBox.warning(self, APP_TITLE, "无可用串口")
            return
        try:
            self._serial = open_serial_port(
                port=port,
                baud=int(self._baud_combo.currentText()),
                data_bits=int(self._data_combo.currentText()),
                stop_bits=stopbits_from_text(self._stop_combo.currentText()),
                parity=parity_from_text(self._parity_combo.currentText()),
            )
            self._open_btn.setText("关闭串口")
            self._status_serial.setText(f"串口：{port} @ {self._baud_combo.currentText()}")
            for w in (
                self._port_combo,
                self._baud_combo,
                self._data_combo,
                self._stop_combo,
                self._parity_combo,
                self._refresh_btn,
            ):
                w.setEnabled(False)
            self._read_thread = SerialReadThread(self._serial)
            self._read_thread.data_received.connect(self._on_rx)
            self._read_thread.error_signal.connect(self._on_serial_error)
            self._read_thread.start()
        except Exception as exc:
            QMessageBox.critical(self, APP_TITLE, f"打开串口失败：{exc}")

    def _close_serial(self) -> None:
        if self._read_thread and self._read_thread.isRunning():
            self._read_thread.stop()
            self._read_thread = None
        if self._serial.is_open:
            self._serial.close()
        self._open_btn.setText("打开串口")
        self._status_serial.setText("串口：未打开")
        for w in (
            self._port_combo,
            self._baud_combo,
            self._data_combo,
            self._stop_combo,
            self._parity_combo,
            self._refresh_btn,
        ):
            w.setEnabled(True)

    def _on_serial_error(self, msg: str) -> None:
        self._status.showMessage(msg, 5000)
        self._close_serial()

    def _append_rx(self, line: str) -> None:
        self._rx_edit.append(line)
        if self._auto_scroll.isChecked():
            self._rx_edit.moveCursor(self._rx_edit.textCursor().End)

    def _on_rx(self, data: bytes) -> None:
        self._rx_count += len(data)
        self._update_count()
        if self._hex_rx_chk.isChecked():
            text = bytes_to_hex(data)
        else:
            text = data.decode("utf-8", errors="replace")
        self._append_rx(f"[{self._ts()}] 收 {text}")

    def _send_data(self) -> None:
        if not self._serial.is_open:
            QMessageBox.warning(self, APP_TITLE, "请先打开串口")
            return
        hex_line = self._hex_cmd.text().strip()
        try:
            if hex_line:
                payload = hex_str_to_bytes(hex_line)
                if not payload:
                    raise ValueError("十六进制格式错误")
                label = bytes_to_hex(payload)
            else:
                payload = self._tx_edit.toPlainText().encode("utf-8")
                payload += EOL_MAP.get(self._eol_combo.currentText(), b"\r\n")
                label = payload.decode("utf-8", errors="replace")
            self._serial.write(payload)
            self._tx_count += len(payload)
            self._update_count()
            self._append_rx(f"[{self._ts()}] 发 {label}")
        except Exception as exc:
            QMessageBox.warning(self, APP_TITLE, f"发送失败：{exc}")

    def _clear_rx(self) -> None:
        self._rx_edit.clear()
        self._rx_count = 0
        self._tx_count = 0
        self._update_count()

    def _save_log(self) -> None:
        if not self._rx_edit.toPlainText():
            QMessageBox.information(self, APP_TITLE, "无日志可保存")
            return
        path, _ = QFileDialog.getSaveFileName(
            self,
            "保存日志",
            f"esp32c3_serial_{QDateTime.currentDateTime().toString('yyyyMMdd_hhmmss')}.txt",
            "文本 (*.txt)",
        )
        if path:
            Path(path).write_text(self._rx_edit.toPlainText(), encoding="utf-8")
            self._status.showMessage(f"已保存 {os.path.basename(path)}", 4000)

    def _set_device(self, info: DeviceInfo) -> None:
        self._device = info
        self._ota_ip.setText(info.ip)
        self._ota_dev_label.setText(
            f"{info.name} | SN:{info.sn} | IP:{info.ip} | {info.version}"
        )
        self._ota_flash_btn.setEnabled(self._bin_path is not None)

    def _ota_log_append(self, msg: str) -> None:
        self._ota_log.append(msg)

    def _ota_find(self) -> None:
        hosts = build_host_candidates(
            ip=self._ota_ip.text(),
            name=self._ota_name.text(),
            sn=self._ota_sn.text(),
            prefix=self._ota_prefix.text(),
        )
        if not hosts:
            QMessageBox.warning(self, APP_TITLE, "请填写 IP、设备名或 SN")
            return
        self._ota_log.clear()
        self._start_ota_worker("find", hosts=hosts)

    def _ota_scan(self) -> None:
        prefix = self._ota_subnet.text().strip()
        if prefix.count(".") != 2:
            QMessageBox.warning(self, APP_TITLE, "网段格式如 192.168.1")
            return
        self._ota_log.clear()
        self._start_ota_worker("scan", prefix=prefix)

    def _start_ota_worker(self, task: str, **kwargs) -> None:
        if self._ota_worker and self._ota_worker.isRunning():
            return
        self._ota_worker = OtaWorkerThread(task, **kwargs)
        self._ota_worker.log_line.connect(self._ota_log_append)
        if task == "find":
            self._ota_worker.find_done.connect(self._on_ota_find_done)
        elif task == "scan":
            self._ota_worker.scan_done.connect(self._on_ota_scan_done)
        self._ota_worker.start()

    def _on_ota_find_done(self, info: DeviceInfo | None) -> None:
        if info:
            self._set_device(info)
            self._ota_log_append(f"已连接: {info.name} @ {info.ip}")
        else:
            self._ota_log_append("未找到设备")

    def _on_ota_scan_done(self, devices: list[DeviceInfo]) -> None:
        if not devices:
            self._ota_log_append("未发现设备")
            return
        for d in devices:
            self._ota_log_append(f"  {d.name}  {d.ip}  SN={d.sn}")
        self._set_device(devices[0])
        if len(devices) > 1:
            self._ota_log_append(f"已选第一台，共 {len(devices)} 台")

    def _pick_bin(self) -> None:
        path, _ = QFileDialog.getOpenFileName(self, "选择固件", "", "固件 (*.bin)")
        if path:
            self._bin_path = Path(path)
            self._bin_label.setText(path)
            self._ota_flash_btn.setEnabled(self._device is not None)

    def _ota_upload(self) -> None:
        if not self._device or not self._bin_path:
            return
        if QMessageBox.question(
            self,
            APP_TITLE,
            f"向 {self._device.name} ({self._device.ip}) 烧录\n{self._bin_path.name}？",
        ) != QMessageBox.Yes:
            return
        self._ota_flash_btn.setEnabled(False)
        self._ota_prog.setValue(0)
        if self._ota_worker and self._ota_worker.isRunning():
            return
        self._ota_worker = OtaWorkerThread(
            "upload", ip=self._device.ip, path=self._bin_path
        )
        self._ota_worker.log_line.connect(self._ota_log_append)
        self._ota_worker.upload_progress.connect(self._ota_prog.setValue)
        self._ota_worker.upload_done.connect(self._on_ota_upload_done)
        self._ota_worker.start()

    def _on_ota_upload_done(self, ok: bool, msg: str) -> None:
        self._ota_flash_btn.setEnabled(self._device is not None and self._bin_path is not None)
        self._ota_log_append(msg)
        if ok:
            QMessageBox.information(self, APP_TITLE, msg)
        else:
            QMessageBox.critical(self, APP_TITLE, f"OTA 失败：{msg}")

    def closeEvent(self, event) -> None:
        self._close_serial()
        if self._ota_worker and self._ota_worker.isRunning():
            self._ota_worker.wait(2000)
        event.accept()
