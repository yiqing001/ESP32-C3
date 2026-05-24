"""HTTP OTA 客户端，协议与设备 /api/info、/api/ota 一致。"""

from __future__ import annotations

import json
import socket
from dataclasses import dataclass
from pathlib import Path
from typing import Callable, Optional
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

ProgressCb = Callable[[int, int], None]


@dataclass
class DeviceInfo:
    name: str
    hostname: str
    sn: str
    ip: str
    mac: str
    version: str
    ota_url: str

    @classmethod
    def from_json(cls, data: dict) -> DeviceInfo:
        return cls(
            name=data.get("name", ""),
            hostname=data.get("hostname", ""),
            sn=data.get("sn", ""),
            ip=data.get("ip", ""),
            mac=data.get("mac", ""),
            version=data.get("version", ""),
            ota_url=data.get("ota_url", ""),
        )


def _normalize_host(host: str) -> str:
    host = host.strip()
    if host.startswith("http://"):
        host = host[7:]
    elif host.startswith("https://"):
        host = host[8:]
    return host.rstrip("/").split("/")[0]


def build_host_candidates(
    ip: str = "",
    name: str = "",
    sn: str = "",
    prefix: str = "MaiQing-C3",
) -> list[str]:
    hosts: list[str] = []
    if ip.strip():
        hosts.append(_normalize_host(ip))
    name = name.strip()
    if name:
        base = name.replace(".local", "").replace(".LOCAL", "")
        hosts.append(base)
        if "." not in name:
            hosts.append(f"{base}.local")
    sn = sn.strip().upper()
    if sn:
        tail = sn[-6:] if len(sn) > 6 else sn
        hosts.append(f"{prefix}-{tail}".lower())
        hosts.append(f"{prefix}-{tail}")
    seen: set[str] = set()
    out: list[str] = []
    for h in hosts:
        if h and h not in seen:
            seen.add(h)
            out.append(h)
    return out


def fetch_device_info(host: str, timeout: float = 3.0) -> Optional[DeviceInfo]:
    host = _normalize_host(host)
    url = f"http://{host}/api/info"
    try:
        req = Request(url, method="GET")
        with urlopen(req, timeout=timeout) as resp:
            data = json.loads(resp.read().decode("utf-8"))
        info = DeviceInfo.from_json(data)
        if not info.ip:
            info.ip = host
        return info
    except (URLError, HTTPError, json.JSONDecodeError, TimeoutError, socket.timeout):
        return None


def scan_subnet(prefix: str, timeout: float = 0.8) -> list[DeviceInfo]:
    if not prefix or prefix.count(".") != 2:
        return []
    found: dict[str, DeviceInfo] = {}
    for i in range(1, 255):
        info = fetch_device_info(f"{prefix}.{i}", timeout=timeout)
        if info:
            found[info.sn or info.ip] = info
    return list(found.values())


class _ProgressReader:
    def __init__(self, path: Path, on_progress: ProgressCb) -> None:
        self._f = path.open("rb")
        self._size = path.stat().st_size
        self._sent = 0
        self._cb = on_progress

    def read(self, amt: int = -1) -> bytes:
        data = self._f.read(amt if amt >= 0 else -1)
        if data:
            self._sent += len(data)
            self._cb(self._sent, self._size)
        return data

    def __len__(self) -> int:
        return self._size

    def close(self) -> None:
        self._f.close()


def upload_firmware(
    ip: str,
    bin_path: Path,
    on_progress: ProgressCb,
    timeout: float = 600.0,
) -> str:
    host = _normalize_host(ip)
    url = f"http://{host}/api/ota"
    reader = _ProgressReader(bin_path, on_progress)
    try:
        req = Request(
            url,
            data=reader,
            method="POST",
            headers={
                "Content-Type": "application/octet-stream",
                "Content-Length": str(len(reader)),
            },
        )
        with urlopen(req, timeout=timeout) as resp:
            return resp.read().decode("utf-8", errors="replace")
    finally:
        reader.close()
