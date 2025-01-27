import sys
import json
import platform
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout,
                             QHBoxLayout, QPushButton, QLineEdit, QTableWidget,
                             QTableWidgetItem, QHeaderView, QLabel, QMessageBox,
                             QFrame, QStyle, QStyleFactory, QScrollArea)
from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import QIcon, QFont, QPalette, QColor
from pynput import keyboard
from pynput.keyboard import Key, KeyCode
import pyperclip
import subprocess
import os


class ModernButton(QPushButton):
    def __init__(self, text, parent=None, primary=False, delete=False):
        super().__init__(text, parent)
        self.primary = primary
        self.delete = delete
        if delete:
            self.setFixedHeight(28)
            self.setMinimumWidth(70)
            icon = QIcon("delicon.svg")
            self.setIcon(icon)
            self.setIconSize(QSize(14, 14))
            self.setText(" 删除")  # 添加空格使图标和文字有间距
            self.setLayoutDirection(Qt.LayoutDirection.LeftToRight)  # 确保图标在左边
        else:
            self.setMinimumHeight(36)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.update_style()

    def update_style(self):
        if self.primary:
            self.setStyleSheet("""
                QPushButton {
                    background-color: #6c5ce7;
                    border: none;
                    color: white;
                    padding: 8px 16px;
                    border-radius: 8px;
                    font-weight: 500;
                    font-size: 13px;
                }
                QPushButton:hover {
                    background-color: #5b4cc7;
                }
                QPushButton:pressed {
                    background-color: #4a3cb7;
                }
            """)
        elif self.delete:
            self.setStyleSheet("""
                QPushButton {
                    background-color: #ff4757;
                    border: none;
                    color: white;
                    padding: 4px 12px;
                    border-radius: 6px;
                    font-size: 12px;
                    font-weight: 500;
                }
                QPushButton:hover {
                    background-color: #ff6b81;
                }
                QPushButton:pressed {
                    background-color: #ff4757;
                }
                QPushButton:focus {
                    outline: none;
                }
            """)
        else:
            self.setStyleSheet("""
                QPushButton {
                    background-color: transparent;
                    border: 1px solid #ff7675;
                    color: #ff7675;
                    padding: 4px 12px;
                    border-radius: 6px;
                    font-size: 12px;
                }
                QPushButton:hover {
                    background-color: #fff5f5;
                }
                QPushButton:pressed {
                    background-color: #ffe5e5;
                }
            """)


class ModernLineEdit(QLineEdit):
    def __init__(self, parent=None, search=False):
        super().__init__(parent)
        self.setMinimumHeight(36)
        style = """
            QLineEdit {
                border: 1px solid #dfe6e9;
                border-radius: 8px;
                padding: 8px 12px;
                background-color: white;
                color: #2d3436;
                font-size: 13px;
            }
            QLineEdit:focus {
                border: 1px solid #6c5ce7;
                background-color: white;
            }
        """
        if search:
            style = """
                QLineEdit {
                    border: none;
                    border-radius: 8px;
                    padding: 8px 12px;
                    background-color: #f5f6fa;
                    color: #2d3436;
                    font-size: 13px;
                }
                QLineEdit:focus {
                    background-color: #eee;
                }
            """
        self.setStyleSheet(style)


class ModernTable(QTableWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet("""
            QTableWidget {
                background-color: white;
                border: none;
                border-radius: 12px;
                gridline-color: transparent;
            }
            QTableWidget::item {
                padding: 8px 16px;
                border-bottom: 1px solid #f0f0f0;
                color: #2d3436;
                font-size: 13px;
            }
            QTableWidget::item:selected {
                background-color: #f5f6fa;
                color: #2d3436;
            }
            QHeaderView::section {
                background-color: white;
                color: #636e72;
                padding: 16px;
                border: none;
                font-weight: 500;
                font-size: 13px;
                border-bottom: 1px solid #dfe6e9;
            }
            QHeaderView::section:first {
                padding-left: 16px;
            }
            QTableWidget::item:hover {
                background-color: #f5f6fa;
            }
        """)
        self.setShowGrid(False)
        self.setAlternatingRowColors(False)
        self.verticalHeader().setVisible(False)
        self.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.horizontalHeader().setHighlightSections(False)
        self.setFrameShape(QFrame.Shape.NoFrame)

        # 设置默认行高
        self.verticalHeader().setDefaultSectionSize(52)
        # 设置最小行高
        self.verticalHeader().setMinimumSectionSize(52)


class ClipboardManager(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Dota2本色风情")
        self.setGeometry(100, 100, 800, 600)
        self.setStyleSheet("""
            QMainWindow {
                background-color: white;
            }
            QLabel {
                color: #2d3436;
                font-size: 13px;
            }
        """)

        # 初始化键盘监听器
        self.keyboard_listener = None
        self.current_keys = set()
        self.hotkey_handlers = {}
        self.is_recording = False

        # 主窗口部件
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        main_layout = QVBoxLayout(main_widget)
        main_layout.setSpacing(16)
        main_layout.setContentsMargins(24, 24, 24, 24)

        # 顶部区域
        top_layout = QHBoxLayout()
        top_layout.setSpacing(16)

        # 标题区域
        title_layout = QVBoxLayout()
        title_layout.setSpacing(4)
        title_label = QLabel("用快捷键复制经典用语，而无需切换游戏窗口")
        title_label.setStyleSheet("""
            QLabel {
                color: #2d3436;
                font-size: 20px;
                font-weight: 600;
            }
        """)
        subtitle_label = QLabel("已添加 0 条短语")
        subtitle_label.setStyleSheet("""
            QLabel {
                color: #636e72;
                font-size: 13px;
            }
        """)
        title_layout.addWidget(title_label)
        title_layout.addWidget(subtitle_label)
        top_layout.addLayout(title_layout)
        top_layout.addStretch()

        main_layout.addLayout(top_layout)

        # 创建表格容器
        table_container = QFrame()
        table_container.setStyleSheet("""
            QFrame {
                background-color: white;
                border: 1px solid #dfe6e9;
                border-radius: 12px;
            }
        """)
        table_layout = QVBoxLayout(table_container)
        table_layout.setContentsMargins(0, 0, 0, 0)
        table_layout.setSpacing(0)

        self.table = ModernTable()
        self.table.setColumnCount(3)
        self.table.setHorizontalHeaderLabels(["短语内容", "快捷键", "操作"])
        header = self.table.horizontalHeader()

        # 添加表格点击事件
        self.table.cellClicked.connect(self.on_cell_clicked)

        # 添加当前编辑行的标记
        self.current_editing_row = -1

        # 调整列宽比例
        total_width = self.width()
        header.setSectionResizeMode(
            0, QHeaderView.ResizeMode.Stretch)  # 短语内容列自适应
        header.setSectionResizeMode(
            1, QHeaderView.ResizeMode.Fixed)    # 快捷键列固定宽度
        header.setSectionResizeMode(
            2, QHeaderView.ResizeMode.Fixed)    # 操作列固定宽度
        self.table.setColumnWidth(1, 120)  # 快捷键列宽度
        self.table.setColumnWidth(2, 100)  # 操作列宽度

        table_layout.addWidget(self.table)

        main_layout.addWidget(table_container, stretch=1)

        # 底部添加区域
        bottom_frame = QFrame()
        bottom_frame.setStyleSheet("""
            QFrame {
                background-color: #f5f6fa;
                border-radius: 12px;
            }
        """)
        bottom_layout = QHBoxLayout(bottom_frame)
        bottom_layout.setContentsMargins(16, 12, 16, 12)
        bottom_layout.setSpacing(12)

        # 文本输入
        self.text_input = ModernLineEdit()
        self.text_input.setPlaceholderText("输入新的短语...")

        # 快捷键输入
        self.hotkey_input = ModernLineEdit()
        self.hotkey_input.setPlaceholderText("点击设置快捷键")
        self.hotkey_input.setReadOnly(True)
        self.hotkey_input.mousePressEvent = self.start_hotkey_recording
        self.hotkey_input.setFixedWidth(150)

        # 添加按钮
        add_button = ModernButton("添加", primary=True)
        add_button.clicked.connect(self.add_entry)

        bottom_layout.addWidget(self.text_input)
        bottom_layout.addWidget(self.hotkey_input)
        bottom_layout.addWidget(add_button)

        main_layout.addWidget(bottom_frame)

        self.entries = []
        self.load_settings()

        # 如果没有预设文案，添加默认文案
        if not self.entries:
            default_entries = [
                {"text": "已使自身本场比赛的积分得失加倍!", "hotkey": "cmd+y"},
                {"text": "由于挂机行为已经被系统从游戏中踢出，他的战绩也会记录为逃跑，玩家现在离开该场比赛将不会被判定为放弃。",
                    "hotkey": "cmd+u"},
                {"text": "已经放弃了游戏，这场比赛不计入天梯积分，剩余玩家可以自由退出。", "hotkey": "cmd+i"},
                {"text": "由于长时间没有重连至游戏，系统判定他为逃跑。玩家现在离开该场比赛将不会被判定为放弃。", "hotkey": "cmd+o"},
                {"text": "已经连续258次预测他们队伍将取得胜利！", "hotkey": "cmd+p"},
                {"text": "经系统检测：玩家XXXXXX存在代练或共享账号嫌疑，遵守社区游戏规范，再次违反将进行封禁处理。",
                    "hotkey": "cmd+["}
            ]
            for entry in default_entries:
                self.add_preset_entry(entry["text"], entry["hotkey"])

        # 更新短语计数
        subtitle_label.setText(f"已添加 {len(self.entries)} 条短语")

        # 启动键盘监听
        self.start_keyboard_listener()

    def get_key_string(self, key):
        try:
            if hasattr(key, 'char'):
                return key.char.lower()
            elif key == Key.cmd or key == Key.cmd_r:
                return 'cmd'
            elif key == Key.ctrl or key == Key.ctrl_r:
                return 'ctrl'
            elif key == Key.alt or key == Key.alt_r:
                return 'alt'
            elif key == Key.shift or key == Key.shift_r:
                return 'shift'
            elif hasattr(key, 'name'):
                return key.name.lower()
        except AttributeError:
            pass
        return None

    def on_cell_clicked(self, row, column):
        # 只处理快捷键列的点击
        if column == 1:
            # 取消之前的编辑状态
            if self.current_editing_row != -1:
                self.reset_hotkey_cell_style(self.current_editing_row)

            # 设置新的编辑状态
            self.current_editing_row = row
            self.is_recording = True
            self.current_keys.clear()

            # 更新单元格样式
            item = self.table.item(row, column)
            item.setBackground(QColor("#fff3f3"))
            item.setText("请按下新的快捷键...")

            # 更新当前快捷键显示
            self.hotkey_input.clear()
            self.hotkey_input.setStyleSheet("""
                QLineEdit {
                    border: 1px solid #dfe6e9;
                    border-radius: 8px;
                    padding: 8px 12px;
                    background-color: white;
                    color: #2d3436;
                    font-size: 13px;
                }
            """)

    def reset_hotkey_cell_style(self, row):
        if row != -1:
            item = self.table.item(row, 1)
            if item:
                item.setBackground(QColor("white"))
                item.setText(self.entries[row]["hotkey"])

    def start_keyboard_listener(self):
        def on_press(key):
            key_str = self.get_key_string(key)
            if key_str:
                if self.is_recording:
                    if key_str not in ['cmd', 'ctrl', 'alt', 'shift']:
                        self.current_keys.add(key_str)
                        # 使用新的排序逻辑
                        modifiers = sorted([k for k in self.current_keys if k in ['cmd', 'ctrl', 'alt', 'shift']],
                                           key=lambda x: {'cmd': 0, 'ctrl': 1, 'alt': 2, 'shift': 3}[x])
                        others = [k for k in self.current_keys if k not in [
                            'cmd', 'ctrl', 'alt', 'shift']]
                        hotkey = '+'.join(modifiers + others)

                        # 更新当前编辑的单元格
                        if self.current_editing_row != -1:
                            self.entries[self.current_editing_row]["hotkey"] = hotkey
                            item = self.table.item(self.current_editing_row, 1)
                            item.setText(hotkey)
                            item.setBackground(QColor("white"))
                            self.current_editing_row = -1
                            self.save_settings()  # 静默保存
                        else:
                            self.hotkey_input.setText(hotkey)
                            self.hotkey_input.setStyleSheet("""
                                QLineEdit {
                                    border: 2px solid #e74c3c;
                                    border-radius: 4px;
                                    padding: 8px;
                                    background-color: #fff3f3;
                                }
                            """)
                        self.is_recording = False
                    else:
                        self.current_keys.add(key_str)
                else:
                    self.current_keys.add(key_str)
                    self.check_hotkeys()

        def on_release(key):
            key_str = self.get_key_string(key)
            if key_str:
                self.current_keys.discard(key_str)

        self.keyboard_listener = keyboard.Listener(
            on_press=on_press, on_release=on_release)
        self.keyboard_listener.start()

    def check_hotkeys(self):
        current_hotkey = '+'.join(sorted(self.current_keys))
        for entry in self.entries:
            if self.normalize_hotkey(entry["hotkey"]) == current_hotkey:
                pyperclip.copy(entry["text"])

    def normalize_hotkey(self, hotkey):
        # 将快捷键拆分为修饰键和普通键
        parts = hotkey.lower().split('+')
        modifiers = []
        others = []

        # 修饰键的优先顺序
        modifier_order = {'cmd': 0, 'ctrl': 1, 'alt': 2, 'shift': 3}

        # 分类键
        for part in parts:
            if part in modifier_order:
                modifiers.append(part)
            else:
                others.append(part)

        # 对修饰键按预定义顺序排序
        modifiers.sort(key=lambda x: modifier_order[x])

        # 组合修饰键和其他键
        return '+'.join(modifiers + others)

    def start_hotkey_recording(self, event):
        self.is_recording = True
        self.current_keys.clear()
        self.hotkey_input.setText("")
        self.hotkey_input.setStyleSheet("""
            QLineEdit {
                border: 2px solid #e74c3c;
                border-radius: 4px;
                padding: 8px;
                background-color: #fff3f3;
            }
        """)

    def add_preset_entry(self, text, hotkey):
        row = self.table.rowCount()
        self.table.insertRow(row)

        # 创建并设置文本项
        text_item = QTableWidgetItem(text)
        text_item.setTextAlignment(
            Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft)
        self.table.setItem(row, 0, text_item)

        # 创建并设置快捷键项
        hotkey_item = QTableWidgetItem(hotkey)
        hotkey_item.setTextAlignment(
            Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignHCenter)
        # 设置快捷键单元格可点击的视觉提示
        hotkey_item.setToolTip("点击设置新的快捷键")
        self.table.setItem(row, 1, hotkey_item)

        # 创建删除按钮
        delete_button = ModernButton("", delete=True)
        delete_button.clicked.connect(lambda: self.delete_entry(row))

        # 创建一个容器来居中放置删除按钮
        container = QWidget()
        layout = QHBoxLayout(container)
        layout.setContentsMargins(8, 4, 8, 4)  # 设置合适的边距
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(delete_button)

        self.table.setCellWidget(row, 2, container)
        self.entries.append({"text": text, "hotkey": hotkey})

    def add_entry(self):
        text = self.text_input.text()
        hotkey = self.hotkey_input.text()
        if text and hotkey:
            self.add_preset_entry(text, hotkey)
            self.text_input.clear()
            self.hotkey_input.clear()
            self.hotkey_input.setStyleSheet("""
                QLineEdit {
                    border: 2px solid #bdc3c7;
                    border-radius: 4px;
                    padding: 8px;
                    background-color: white;
                }
            """)

    def delete_entry(self, row):
        self.table.removeRow(row)
        del self.entries[row]

    def save_settings(self):
        with open("settings.json", "w", encoding="utf-8") as f:
            json.dump(self.entries, f, ensure_ascii=False, indent=2)

    def load_settings(self):
        try:
            with open("settings.json", "r", encoding="utf-8") as f:
                self.entries = json.load(f)
                for entry in self.entries:
                    row = self.table.rowCount()
                    self.table.insertRow(row)
                    self.table.setItem(row, 0, QTableWidgetItem(entry["text"]))
                    self.table.setItem(
                        row, 1, QTableWidgetItem(entry["hotkey"]))

                    delete_button = ModernButton("", delete=True)
                    delete_button.clicked.connect(
                        lambda: self.delete_entry(row))
                    self.table.setCellWidget(row, 2, delete_button)
        except FileNotFoundError:
            pass

    def closeEvent(self, event):
        if self.keyboard_listener:
            self.keyboard_listener.stop()
        super().closeEvent(event)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle(QStyleFactory.create("Fusion"))
    window = ClipboardManager()
    window.show()
    sys.exit(app.exec())
