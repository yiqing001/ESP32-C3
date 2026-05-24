import sys
import os
import serial
import serial.tools.list_ports
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QHBoxLayout, QVBoxLayout,
                             QLabel, QComboBox, QPushButton, QTextEdit, QLineEdit, QGroupBox,
                             QFileDialog, QCheckBox, QSplitter, QStatusBar, QGridLayout, QFrame)
from PyQt5.QtCore import Qt, QThread, pyqtSignal, QDateTime, QTimer
from PyQt5.QtGui import QFont, QPalette, QColor

# ===================== 核心：传感器数据解析类（与官方解析100%匹配）=====================
class NU300SensorParser:
    def __init__(self):
        self.SHORT_FRAME_HEAD = 0xA5    # 命令短帧帧头
        self.LONG_FRAME_HEAD = 0xFF     # 测量长帧帧头
        self.FRAME_TAIL = 0xFE          # 长帧帧尾
        self.SHORT_FRAME_LEN = 5        # 命令短帧字节数
        self.LONG_FRAME_LEN = 14        # 测量长帧字节数
        self.PRECISION = 0.1            # 精度系数
        # 手册命令码说明
        self.CMD_DESC = {
            0x01: "写传感器ID号",
            0x02: "写A1点值",
            0x03: "写A2点值",
            0x04: "写入外部温度值并使用外部温度补偿",
            0x05: "使用内部温度补偿",
            0x06: "读取测量数据"
        }

    # 16进制字符串转字节列表
    def hex_str_to_bytes(self, hex_str):
        try:
            clean_hex = hex_str.replace(" ", "").upper().strip()
            if len(clean_hex) % 2 != 0:
                return []
            return [int(clean_hex[i:i+2], 16) for i in range(0, len(clean_hex), 2)]
        except Exception:
            return []

    # 校验位计算（手册规则：前五字节求和取低位）
    def calc_check_sum(self, bytes_list):
        if len(bytes_list) < 5:
            return None
        return sum(bytes_list[:5]) & 0xFF

    # 解析5字节命令短帧
    def parse_short_frame(self, bytes_list):
        if len(bytes_list) != self.SHORT_FRAME_LEN or bytes_list[0] != self.SHORT_FRAME_HEAD:
            return {"解析状态": "失败", "错误信息": "短帧格式错误"}
        result = {
            "解析状态": "成功",
            "帧类型": "命令回传短帧",
            "传感器地址": hex(bytes_list[1]),
            "命令码": hex(bytes_list[2]),
            "命令说明": self.CMD_DESC.get(bytes_list[2], "未知命令"),
            "数据位低": hex(bytes_list[3]),
            "数据字段": hex(bytes_list[4])
        }
        return result

    # 解析14字节测量长帧（感应强度取低位，匹配官方）
    def parse_long_frame(self, bytes_list):
        if len(bytes_list) != self.LONG_FRAME_LEN:
            return {"解析状态": "失败", "错误信息": f"长帧长度错误，预期14字节，实际{len(bytes_list)}字节"}
        if bytes_list[0] != self.LONG_FRAME_HEAD or bytes_list[-1] != self.FRAME_TAIL:
            return {"解析状态": "失败", "错误信息": "帧头/帧尾不匹配"}

        # 字段拆分（14字节标准结构）
        dis_b1, dis_b2 = bytes_list[1], bytes_list[2]
        time_b1, time_b2 = bytes_list[3], bytes_list[4]
        temp_b1, temp_b2 = bytes_list[5], bytes_list[6]
        a1_b1, a1_b2 = bytes_list[7], bytes_list[8]
        a2_b1, a2_b2 = bytes_list[9], bytes_list[10]
        ind_low, ind_high = bytes_list[11], bytes_list[12]

        # 数值换算（严格遵循手册高位在前规则）
        distance = (dis_b2 << 8 | dis_b1) * self.PRECISION
        fly_time = time_b2 << 8 | time_b1
        temperature = (temp_b2 << 8 | temp_b1) * self.PRECISION
        a1_val = (a1_b2 << 8 | a1_b1) * self.PRECISION
        a2_val = (a2_b2 << 8 | a2_b1) * self.PRECISION
        induct_intensity = ind_low  # 核心：取低位忽略高位，匹配官方解析结果

        # 距离状态判断（手册量程）
        if 0 <= distance < 20:
            dis_status = "盲区（0~20mm）"
        elif 20 <= distance <= 300:
            dis_status = "有效测量范围（20~300mm）"
        else:
            dis_status = "超出测量范围（>300mm）"

        result = {
            "解析状态": "成功",
            "帧类型": "测量数据长帧",
            "测量距离(mm)": round(distance, 1),
            "超声飞行时间(μs)": fly_time,
            "传感器温度(℃)": round(temperature, 1),
            "A1点值(mm)": round(a1_val, 1),
            "A2点值(mm)": round(a2_val, 1),
            "感应强度值": induct_intensity,
            "距离状态": dis_status
        }
        return result

    # 自动解析入口
    def auto_parse(self, bytes_data):
        bytes_list = list(bytes_data)
        if len(bytes_list) == self.SHORT_FRAME_LEN:
            return self.parse_short_frame(bytes_list)
        elif len(bytes_list) == self.LONG_FRAME_LEN:
            return self.parse_long_frame(bytes_list)
        else:
            return {"解析状态": "失败", "错误信息": f"帧长度不匹配，实际{len(bytes_list)}字节"}

# ===================== 串口读取子线程（避免GUI卡死）=====================
class SerialReadThread(QThread):
    data_received = pyqtSignal(bytes)
    error_signal = pyqtSignal(str)

    def __init__(self, serial_port):
        super().__init__()
        self.serial_port = serial_port
        self.is_running = True

    def run(self):
        while self.is_running and self.serial_port.is_open:
            try:
                if self.serial_port.in_waiting > 0:
                    data = self.serial_port.read(self.serial_port.in_waiting)
                    self.data_received.emit(data)
                self.msleep(10)
            except Exception as e:
                self.error_signal.emit(f"串口读取错误：{str(e)}")
                self.is_running = False
                break

    def stop(self):
        self.is_running = False
        self.wait()

# ===================== 主窗口：黑金科技风UI =====================
class SerialToolMainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.parser = NU300SensorParser()
        self.serial_port = serial.Serial()
        self.read_thread = None
        self.receive_count = 0
        self.send_count = 0
        self.is_continuous_mode = False  # 连续读取状态标记
        self.continuous_timer = QTimer()  # 连续读取定时器
        self.continuous_timer.setInterval(200)  # 200ms读取一次，可自行调整
        self.continuous_timer.timeout.connect(self.send_read_once)
        self.init_ui()
        self.set_global_style()

    # 全局科技风格设置
    def set_global_style(self):
        # 全局样式表
        self.setStyleSheet("""
            QMainWindow, QWidget {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #121212, stop:1 #1A1A2E);
                color: #E0E0E0;
                font-family: "Microsoft YaHei", "Segoe UI", sans-serif;
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
                padding: 0 8px 0 8px;
            }
            QLabel {
                color: #E0E0E0;
                background-color: transparent;
            }
            QComboBox {
                background-color: rgba(30, 30, 60, 0.8);
                border: 1px solid rgba(60, 60, 120, 0.8);
                border-radius: 4px;
                padding: 4px 8px;
                color: #E0E0E0;
                min-height: 20px;
            }
            QComboBox::drop-down {
                border: none;
            }
            QComboBox::down-arrow {
                image: none;
                border-left: 5px solid transparent;
                border-right: 5px solid transparent;
                border-top: 5px solid #00E5FF;
                width: 0;
                height: 0;
                margin-right: 8px;
            }
            QComboBox QAbstractItemView {
                background-color: rgba(30, 30, 60, 0.95);
                border: 1px solid rgba(60, 60, 120, 0.8);
                selection-background-color: rgba(10, 36, 99, 0.8);
                color: #E0E0E0;
            }
            QPushButton {
                border-radius: 4px;
                padding: 6px 12px;
                font-weight: bold;
                color: #FFFFFF;
                min-height: 24px;
            }
            QPushButton:enabled {
                background-color: rgba(10, 36, 99, 0.8);
                border: 1px solid #00E5FF;
            }
            QPushButton:disabled {
                background-color: rgba(30, 30, 40, 0.8);
                border: 1px solid rgba(60, 60, 80, 0.8);
                color: #666666;
            }
            QPushButton:enabled:hover {
                background-color: rgba(10, 36, 99, 1);
                border: 1px solid #00FFFF;
            }
            QPushButton:enabled:pressed {
                background-color: rgba(5, 20, 60, 0.8);
            }
            QTextEdit, QLineEdit {
                background-color: rgba(30, 30, 60, 0.8);
                border: 1px solid rgba(60, 60, 120, 0.8);
                border-radius: 4px;
                padding: 6px;
                color: #E0E0E0;
                font-family: "Consolas", "Courier New", monospace;
            }
            QCheckBox {
                color: #E0E0E0;
                spacing: 8px;
            }
            QCheckBox::indicator {
                width: 16px;
                height: 16px;
                border: 1px solid rgba(60, 60, 120, 0.8);
                border-radius: 3px;
                background-color: rgba(30, 30, 60, 0.8);
            }
            QCheckBox::indicator:checked {
                background-color: rgba(10, 36, 99, 0.8);
                border: 1px solid #00E5FF;
                image: url(:/qt-project.org/styles/commonstyle/images/check.png);
            }
            QSplitter::handle {
                background-color: rgba(40, 40, 80, 0.5);
            }
            QStatusBar {
                background-color: rgba(26, 26, 46, 0.8);
                color: #00E5FF;
                border-top: 1px solid rgba(40, 40, 80, 0.8);
            }
            QFrame {
                background-color: transparent;
            }
        """)
        # 窗口背景
        self.setAutoFillBackground(True)
        palette = self.palette()
        palette.setColor(QPalette.Window, QColor(18, 18, 18))
        self.setPalette(palette)

    # 初始化UI界面
    def init_ui(self):
        # 窗口基础设置
        self.setWindowTitle("金瓷超声波串口调试助手")
        self.setMinimumSize(1200, 750)
        # 全局字体
        font = QFont("Microsoft YaHei", 9)
        QApplication.setFont(font)

        # 中心部件
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        main_layout.setSpacing(12)
        main_layout.setContentsMargins(12, 12, 12, 12)

        # ===================== 1. 顶部：紧凑串口配置区（缩小尺寸）=====================
        config_group = QGroupBox("串口配置")
        config_group.setMaximumHeight(80)  # 限制最大高度，缩小区域
        config_layout = QGridLayout(config_group)
        config_layout.setSpacing(15)
        config_layout.setContentsMargins(15, 10, 15, 10)

        # 第一行：端口选择
        config_layout.addWidget(QLabel("串口端口："), 0, 0)
        self.port_combo = QComboBox()
        self.port_combo.setMinimumWidth(150)
        config_layout.addWidget(self.port_combo, 0, 1)

        # 刷新端口按钮
        self.refresh_btn = QPushButton("刷新端口")
        self.refresh_btn.setMaximumWidth(100)
        self.refresh_btn.clicked.connect(self.refresh_serial_ports)
        config_layout.addWidget(self.refresh_btn, 0, 2)

        # 波特率
        config_layout.addWidget(QLabel("波特率："), 0, 3)
        self.baud_combo = QComboBox()
        self.baud_combo.addItems(["115200", "9600", "19200", "38400", "57600"])
        self.baud_combo.setCurrentText("115200")  # 手册默认波特率
        self.baud_combo.setMinimumWidth(100)
        config_layout.addWidget(self.baud_combo, 0, 4)

        # 数据位
        config_layout.addWidget(QLabel("数据位："), 0, 5)
        self.data_combo = QComboBox()
        self.data_combo.addItems(["8", "7", "6", "5"])
        self.data_combo.setCurrentText("8")
        self.data_combo.setMaximumWidth(80)
        config_layout.addWidget(self.data_combo, 0, 6)

        # 停止位
        config_layout.addWidget(QLabel("停止位："), 0, 7)
        self.stop_combo = QComboBox()
        self.stop_combo.addItems(["1", "1.5", "2"])
        self.stop_combo.setCurrentText("1")
        self.stop_combo.setMaximumWidth(80)
        config_layout.addWidget(self.stop_combo, 0, 8)

        # 校验位
        config_layout.addWidget(QLabel("校验位："), 0, 9)
        self.parity_combo = QComboBox()
        self.parity_combo.addItems(["无", "奇校验", "偶校验"])
        self.parity_combo.setCurrentText("无")
        self.parity_combo.setMaximumWidth(80)
        config_layout.addWidget(self.parity_combo, 0, 10)

        # 打开/关闭串口按钮
        self.open_close_btn = QPushButton("打开串口")
        self.open_close_btn.setMinimumWidth(120)
        self.open_close_btn.setStyleSheet("""
            QPushButton:enabled {
                background-color: rgba(10, 36, 99, 0.8);
                border: 1px solid #00E5FF;
                font-size: 10pt;
                font-weight: bold;
            }
            QPushButton:enabled:hover {
                background-color: rgba(10, 36, 99, 1);
            }
        """)
        self.open_close_btn.clicked.connect(self.open_close_serial)
        config_layout.addWidget(self.open_close_btn, 0, 11)

        config_layout.setColumnStretch(12, 1)
        main_layout.addWidget(config_group)

        # ===================== 2. 中间：功能区分割 =====================
        main_splitter = QSplitter(Qt.Horizontal)
        main_splitter.setStretchFactor(0, 1)
        main_splitter.setStretchFactor(1, 4)
        main_splitter.setHandleWidth(2)

        # -------------------- 左侧：控制区 + 命令示例区 --------------------
        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)
        left_layout.setSpacing(12)
        left_layout.setContentsMargins(0, 0, 0, 0)

        # 1. 核心控制区（单次/连续按钮）
        control_group = QGroupBox("测量控制")
        control_layout = QHBoxLayout(control_group)
        control_layout.setSpacing(20)
        control_layout.setContentsMargins(20, 15, 20, 15)

        # 单次读取按钮
        self.once_btn = QPushButton("单次读取")
        self.once_btn.setMinimumHeight(50)
        self.once_btn.setStyleSheet("""
            QPushButton {
                font-size: 11pt;
                font-weight: bold;
                background-color: #0078D7;
                border: 1px solid #0091FF;
            }
            QPushButton:hover {
                background-color: #0091FF;
            }
            QPushButton:pressed {
                background-color: #005A9E;
            }
        """)
        self.once_btn.clicked.connect(self.send_read_once)
        control_layout.addWidget(self.once_btn)

        # 连续读取按钮
        self.continuous_btn = QPushButton("连续读取")
        self.continuous_btn.setMinimumHeight(50)
        self.continuous_btn.setStyleSheet("""
            QPushButton {
                font-size: 11pt;
                font-weight: bold;
                background-color: rgba(10, 36, 99, 0.8);
                border: 1px solid #00E5FF;
            }
            QPushButton:hover {
                background-color: rgba(10, 36, 99, 1);
            }
        """)
        self.continuous_btn.clicked.connect(self.toggle_continuous_mode)
        control_layout.addWidget(self.continuous_btn)
        left_layout.addWidget(control_group)

        # 2. 自定义命令发送区
        custom_cmd_group = QGroupBox("自定义命令发送")
        custom_cmd_layout = QVBoxLayout(custom_cmd_group)
        custom_cmd_layout.setSpacing(8)

        self.custom_cmd_input = QLineEdit()
        self.custom_cmd_input.setPlaceholderText("请输入16进制命令，如：A5 01 06 00 00 AC")
        self.custom_cmd_input.setMinimumHeight(28)
        custom_cmd_layout.addWidget(self.custom_cmd_input)

        self.send_custom_btn = QPushButton("发送自定义命令")
        self.send_custom_btn.setStyleSheet("""
            QPushButton {
                background-color: #00C853;
                border: 1px solid #00E676;
            }
            QPushButton:hover {
                background-color: #00E676;
            }
        """)
        self.send_custom_btn.clicked.connect(self.send_custom_cmd)
        custom_cmd_layout.addWidget(self.send_custom_btn)
        left_layout.addWidget(custom_cmd_group)

        # 3. 辅助功能区
        assist_group = QGroupBox("辅助功能")
        assist_layout = QHBoxLayout(assist_group)
        assist_layout.setSpacing(10)

        self.clear_receive_btn = QPushButton("清空接收区")
        self.clear_receive_btn.clicked.connect(self.clear_receive_area)
        assist_layout.addWidget(self.clear_receive_btn)

        self.save_log_btn = QPushButton("保存日志")
        self.save_log_btn.clicked.connect(self.save_log_file)
        assist_layout.addWidget(self.save_log_btn)
        left_layout.addWidget(assist_group)

        # 4. 选项区
        option_group = QGroupBox("显示选项")
        option_layout = QHBoxLayout(option_group)
        option_layout.setSpacing(20)

        self.auto_scroll_check = QCheckBox("自动滚屏")
        self.auto_scroll_check.setChecked(True)
        option_layout.addWidget(self.auto_scroll_check)

        self.hex_show_check = QCheckBox("16进制显示")
        self.hex_show_check.setChecked(True)
        option_layout.addWidget(self.hex_show_check)
        left_layout.addWidget(option_group)

        # 5. 命令示例参考区（取消按键，纯文本展示）
        cmd_example_group = QGroupBox("协议命令示例参考（手册标准）")
        cmd_example_layout = QVBoxLayout(cmd_example_group)
        cmd_example_layout.setSpacing(6)

        # 示例文本（严格匹配手册内容）
        example_text = QTextEdit()
        example_text.setReadOnly(True)
        example_text.setMinimumHeight(220)
        example_text.setStyleSheet("""
            QTextEdit {
                color: #B0B0B0;
                font-size: 9pt;
                line-height: 150%;
            }
        """)
        example_content = """
1. 读取测量数据
   写入：A5 01 06 00 00 AC
   回传：14字节测量长帧（FF开头，FE结尾）

2. 写传感器ID号
   写入：A5 01 01 00 02 A9
   回传：A5 02 01 00 00 A8

3. 写A1点值
   写入：A5 01 02 F4 01 9D
   回传：A5 01 02 F4 01 9D

4. 写A2点值
   写入：A5 01 03 B0 04 5D
   回传：A5 01 03 B0 04 5D

5. 写入外部温度值并使用外部温度补偿
   写入：A5 01 04 12 00 BC
   回传：A5 01 04 12 00 BC

6. 使用内部温度补偿
   写入：A5 01 05 00 00 AB
   回传：A5 01 04 00 00 AB
        """
        example_text.setText(example_content)
        cmd_example_layout.addWidget(example_text)
        left_layout.addWidget(cmd_example_group)

        left_layout.addStretch()
        main_splitter.addWidget(left_widget)

        # -------------------- 右侧：数据接收与解析区 --------------------
        receive_group = QGroupBox("数据接收与解析")
        receive_layout = QVBoxLayout(receive_group)
        receive_layout.setContentsMargins(10, 10, 10, 10)

        # 分割上下区域：原始数据 + 解析结果
        receive_splitter = QSplitter(Qt.Vertical)
        receive_splitter.setHandleWidth(2)

        # 原始数据接收区
        self.raw_receive_text = QTextEdit()
        self.raw_receive_text.setReadOnly(True)
        self.raw_receive_text.setFont(QFont("Consolas", 10))
        receive_splitter.addWidget(self.raw_receive_text)

        # 解析结果区：固定标签 + 实时参数显示
        parse_widget = QWidget()
        parse_layout = QGridLayout(parse_widget)
        parse_layout.setSpacing(10)
        parse_layout.setContentsMargins(15, 15, 15, 15)
        
        # 固定文本标签和值显示
        labels = [
            "测量距离(mm)",
            "超声飞行时间(μs)",
            "传感器温度(℃)",
            "A1点值(mm)",
            "A2点值(mm)",
            "感应强度值",
            "距离状态"
        ]
        
        self.param_labels = {}
        for i, label_text in enumerate(labels):
            # 固定标签
            label = QLabel(label_text + "：")
            label.setStyleSheet("color: #E0E0E0; font-weight: bold;")
            parse_layout.addWidget(label, i, 0)
            
            # 值显示标签
            value_label = QLabel("--")
            value_label.setStyleSheet("color: #00E5FF; font-family: 'Consolas';")
            value_label.setMinimumWidth(200)
            parse_layout.addWidget(value_label, i, 1)
            
            self.param_labels[label_text] = value_label
        
        receive_splitter.addWidget(parse_widget)

        receive_splitter.setStretchFactor(0, 1)
        receive_splitter.setStretchFactor(1, 1)
        receive_layout.addWidget(receive_splitter)
        main_splitter.addWidget(receive_group)

        main_layout.addWidget(main_splitter)

        # ===================== 3. 底部：状态栏 =====================
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_label = QLabel("串口状态：未打开")
        self.status_label.setStyleSheet("color: #00E5FF; font-weight: bold;")
        self.count_label = QLabel("接收：0 字节 | 发送：0 字节")
        self.count_label.setStyleSheet("color: #E0E0E0;")
        self.status_bar.addWidget(self.status_label)
        self.status_bar.addPermanentWidget(self.count_label)

        # 初始化：刷新串口列表
        self.refresh_serial_ports()
        # 初始禁用按钮
        self.set_control_btn_enable(False)

    # ===================== 核心控制功能 =====================
    # 单次读取测量数据
    def send_read_once(self):
        if not self.serial_port.is_open:
            self.status_bar.showMessage("请先打开串口！", 3000)
            return
        # 手册标准读取测量数据命令
        read_cmd = "A5 01 06 00 00 AC"
        self.send_preset_cmd(read_cmd)

    # 切换连续读取模式
    def toggle_continuous_mode(self):
        if not self.serial_port.is_open:
            self.status_bar.showMessage("请先打开串口！", 3000)
            return

        if not self.is_continuous_mode:
            # 启动连续模式
            self.is_continuous_mode = True
            self.continuous_timer.start()
            self.continuous_btn.setText("停止读取")
            self.continuous_btn.setStyleSheet("""
                QPushButton {
                    font-size: 11pt;
                    font-weight: bold;
                    background-color: rgba(10, 36, 99, 0.8);
                    border: 1px solid #00E5FF;
                }
                QPushButton:hover {
                    background-color: rgba(10, 36, 99, 1);
                }
            """)
            self.status_bar.showMessage("连续读取模式已启动", 2000)
        else:
            # 停止连续模式
            self.is_continuous_mode = False
            self.continuous_timer.stop()
            self.continuous_btn.setText("连续读取")
            self.continuous_btn.setStyleSheet("""
                QPushButton {
                    font-size: 11pt;
                    font-weight: bold;
                    background-color: rgba(10, 36, 99, 0.8);
                    border: 1px solid #00E5FF;
                }
                QPushButton:hover {
                    background-color: rgba(10, 36, 99, 1);
                }
            """)
            self.status_bar.showMessage("连续读取模式已停止", 2000)

    # 控制按钮启用/禁用
    def set_control_btn_enable(self, enable):
        self.once_btn.setEnabled(enable)
        self.continuous_btn.setEnabled(enable)
        self.send_custom_btn.setEnabled(enable)

    # ===================== 串口功能函数 =====================
    # 刷新串口列表
    def refresh_serial_ports(self):
        self.port_combo.clear()
        port_list = serial.tools.list_ports.comports()
        for port in port_list:
            self.port_combo.addItem(f"{port.device} - {port.description}")
        if self.port_combo.count() == 0:
            self.port_combo.addItem("无可用串口")

    # 打开/关闭串口
    def open_close_serial(self):
        if not self.serial_port.is_open:
            # 打开串口
            try:
                port_name = self.port_combo.currentText().split(" - ")[0]
                if port_name == "无可用串口":
                    self.status_bar.showMessage("无可用串口，请检查设备连接", 3000)
                    return
                baudrate = int(self.baud_combo.currentText())
                data_bits = int(self.data_combo.currentText())
                stop_bits = float(self.stop_combo.currentText())
                # 校验位设置
                parity_text = self.parity_combo.currentText()
                if parity_text == "无":
                    parity = serial.PARITY_NONE
                elif parity_text == "奇校验":
                    parity = serial.PARITY_ODD
                else:
                    parity = serial.PARITY_EVEN

                # 配置串口
                self.serial_port.port = port_name
                self.serial_port.baudrate = baudrate
                self.serial_port.bytesize = data_bits
                self.serial_port.stopbits = stop_bits
                self.serial_port.parity = parity
                self.serial_port.timeout = 0.1

                # 打开串口
                self.serial_port.open()
                if self.serial_port.is_open:
                    # 更新UI状态
                    self.open_close_btn.setText("关闭串口")
                    self.open_close_btn.setStyleSheet("""
                QPushButton:enabled {
                    background-color: rgba(10, 36, 99, 0.8);
                    border: 1px solid #00E5FF;
                    font-size: 10pt;
                    font-weight: bold;
                }
                QPushButton:enabled:hover {
                    background-color: rgba(10, 36, 99, 1);
                }
            """)
                    self.status_label.setText(f"串口状态：{port_name} 已打开 | 波特率 {baudrate}")
                    # 禁用配置项
                    self.port_combo.setEnabled(False)
                    self.baud_combo.setEnabled(False)
                    self.data_combo.setEnabled(False)
                    self.stop_combo.setEnabled(False)
                    self.parity_combo.setEnabled(False)
                    self.refresh_btn.setEnabled(False)
                    # 启用控制按钮
                    self.set_control_btn_enable(True)
                    # 启动读取线程
                    self.read_thread = SerialReadThread(self.serial_port)
                    self.read_thread.data_received.connect(self.handle_received_data)
                    self.read_thread.error_signal.connect(self.handle_serial_error)
                    self.read_thread.start()
            except Exception as e:
                self.status_bar.showMessage(f"串口打开失败：{str(e)}", 5000)
        else:
            # 关闭串口
            self.close_serial()

    # 关闭串口
    def close_serial(self):
        # 先停止连续读取
        if self.is_continuous_mode:
            self.toggle_continuous_mode()
        # 停止读取线程
        if self.read_thread and self.read_thread.isRunning():
            self.read_thread.stop()
            self.read_thread = None
        # 关闭串口
        if self.serial_port.is_open:
            self.serial_port.close()
        # 更新UI状态
        self.open_close_btn.setText("打开串口")
        self.open_close_btn.setStyleSheet("""
            QPushButton:enabled {
                background-color: rgba(10, 36, 99, 0.8);
                border: 1px solid #00E5FF;
                font-size: 10pt;
                font-weight: bold;
            }
            QPushButton:enabled:hover {
                background-color: rgba(10, 36, 99, 1);
            }
        """)
        self.status_label.setText("串口状态：未打开")
        # 启用配置项
        self.port_combo.setEnabled(True)
        self.baud_combo.setEnabled(True)
        self.data_combo.setEnabled(True)
        self.stop_combo.setEnabled(True)
        self.parity_combo.setEnabled(True)
        self.refresh_btn.setEnabled(True)
        # 禁用控制按钮
        self.set_control_btn_enable(False)

    # 处理串口错误
    def handle_serial_error(self, error_msg):
        self.status_bar.showMessage(error_msg, 5000)
        self.close_serial()

    # ===================== 数据发送函数 =====================
    # 发送预设命令
    def send_preset_cmd(self, hex_str):
        try:
            bytes_list = self.parser.hex_str_to_bytes(hex_str)
            if not bytes_list:
                self.status_bar.showMessage("命令格式错误！", 3000)
                return
            send_data = bytes(bytes_list)
            # 发送数据
            self.serial_port.write(send_data)
            self.send_count += len(send_data)
            self.update_count_label()
            # 显示发送的内容
            time_str = QDateTime.currentDateTime().toString("HH:mm:ss.zzz")
            self.raw_receive_text.append(f"[{time_str}] 发送：{hex_str.upper()}")
        except Exception as e:
            self.status_bar.showMessage(f"发送失败：{str(e)}", 3000)

    # 发送自定义命令
    def send_custom_cmd(self):
        hex_str = self.custom_cmd_input.text().strip()
        if not hex_str:
            self.status_bar.showMessage("请输入要发送的命令！", 3000)
            return
        self.send_preset_cmd(hex_str)

    # ===================== 数据接收与解析 =====================
    # 处理收到的串口数据
    def handle_received_data(self, data):
        # 更新接收计数
        self.receive_count += len(data)
        self.update_count_label()
        # 获取时间戳
        time_str = QDateTime.currentDateTime().toString("HH:mm:ss.zzz")
        # 转换为16进制字符串
        hex_str = data.hex(" ").upper()
        # 显示原始数据
        if self.hex_show_check.isChecked():
            self.raw_receive_text.append(f"[{time_str}] 接收：{hex_str}")
        else:
            try:
                ascii_str = data.decode("gbk", errors="ignore")
                self.raw_receive_text.append(f"[{time_str}] 接收：{ascii_str}")
            except:
                self.raw_receive_text.append(f"[{time_str}] 接收：{hex_str}")
        # 自动滚屏
        if self.auto_scroll_check.isChecked():
            self.raw_receive_text.moveCursor(self.raw_receive_text.textCursor().End)

        # 核心：自动解析数据
        parse_result = self.parser.auto_parse(data)
        # 实时更新参数值
        if parse_result.get("解析状态") == "成功":
            # 更新各个参数标签
            for param_name, label in self.param_labels.items():
                if param_name in parse_result:
                    label.setText(str(parse_result[param_name]))
                else:
                    # 对于短帧或其他类型的数据，保持原值
                    pass

    # ===================== 辅助功能函数 =====================
    # 更新收发计数
    def update_count_label(self):
        self.count_label.setText(f"接收：{self.receive_count} 字节 | 发送：{self.send_count} 字节")

    # 清空接收区
    def clear_receive_area(self):
        self.raw_receive_text.clear()
        # 重置参数标签
        for label in self.param_labels.values():
            label.setText("--")
        self.receive_count = 0
        self.send_count = 0
        self.update_count_label()

    # 保存日志文件
    def save_log_file(self):
        if self.raw_receive_text.toPlainText() == "":
            self.status_bar.showMessage("无日志可保存！", 3000)
            return
        file_path, _ = QFileDialog.getSaveFileName(
            self, "保存日志", f"金瓷超声波调试日志_{QDateTime.currentDateTime().toString('yyyyMMdd_hhmmss')}.txt",
            "文本文件 (*.txt);;所有文件 (*.*)"
        )
        if file_path:
            try:
                with open(file_path, "w", encoding="utf-8") as f:
                    f.write("===== 金瓷超声波串口调试助手 接收日志 =====\n")
                    f.write(f"日志生成时间：{QDateTime.currentDateTime().toString('yyyy-MM-dd HH:mm:ss')}\n")
                    f.write(f"串口配置：{self.status_label.text()}\n")
                    f.write("="*70 + "\n\n")
                    f.write("===== 原始接收数据 =====\n")
                    f.write(self.raw_receive_text.toPlainText() + "\n\n")
                    f.write("===== 当前参数值 =====\n")
                    for param_name, label in self.param_labels.items():
                        f.write(f"{param_name}：{label.text()}\n")
                self.status_bar.showMessage(f"日志保存成功：{os.path.basename(file_path)}", 5000)
            except Exception as e:
                self.status_bar.showMessage(f"日志保存失败：{str(e)}", 5000)

    # 窗口关闭事件：安全释放资源
    def closeEvent(self, event):
        self.close_serial()
        event.accept()

# ===================== 程序入口 =====================
if __name__ == "__main__":
    # 高分屏适配
    QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)
    QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps, True)
    # 启动APP
    app = QApplication(sys.argv)
    window = SerialToolMainWindow()
    window.show()
    sys.exit(app.exec_())