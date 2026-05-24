"""串口枚举与参数配置。"""

from __future__ import annotations

import serial
from serial.tools import list_ports

BAUD_RATES = ("9600", "19200", "38400", "57600", "115200", "230400", "460800", "921600")


def list_serial_ports() -> list[tuple[str, str]]:
    """返回 (device, description) 列表。"""
    return [(p.device, p.description or "") for p in list_ports.comports()]


def parity_from_text(text: str) -> str:
    if text == "奇校验":
        return serial.PARITY_ODD
    if text == "偶校验":
        return serial.PARITY_EVEN
    return serial.PARITY_NONE


def stopbits_from_text(text: str) -> float:
    if text == "1.5":
        return serial.STOPBITS_ONE_POINT_FIVE
    if text == "2":
        return serial.STOPBITS_TWO
    return serial.STOPBITS_ONE


def open_serial_port(
    port: str,
    baud: int,
    data_bits: int = 8,
    stop_bits: float = serial.STOPBITS_ONE,
    parity: str = serial.PARITY_NONE,
) -> serial.Serial:
    return serial.Serial(
        port=port,
        baudrate=baud,
        bytesize=data_bits,
        stopbits=stop_bits,
        parity=parity,
        timeout=0.1,
    )
