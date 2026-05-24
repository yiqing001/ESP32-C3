"""串口读取线程（与 APP/test 相同模式：QThread + pyqtSignal）。"""

from __future__ import annotations

import serial
from PyQt5.QtCore import QThread, pyqtSignal


class SerialReadThread(QThread):
    data_received = pyqtSignal(bytes)
    error_signal = pyqtSignal(str)

    def __init__(self, serial_port: serial.Serial) -> None:
        super().__init__()
        self._port = serial_port
        self._running = True

    def run(self) -> None:
        while self._running and self._port.is_open:
            try:
                waiting = self._port.in_waiting
                if waiting > 0:
                    self.data_received.emit(self._port.read(waiting))
                self.msleep(10)
            except Exception as exc:
                self.error_signal.emit(f"串口读取错误：{exc}")
                self._running = False
                break

    def stop(self) -> None:
        self._running = False
        self.wait(1500)
