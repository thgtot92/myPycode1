import time
import ctypes
import psutil
import win32gui
import win32process
import win32con
import re
from PyQt5 import QtWidgets, QtCore, QtGui
import sys
import datetime
from collections import defaultdict
from PyQt5.QtWidgets import QMessageBox

PROCESS_VM_READ = 0x0010
PROCESS_QUERY_INFORMATION = 0x0400

keyword_stats = defaultdict(int)
HIGHLIGHT_RULES = {}

AUTO_REPLY_RULES = {
    "통당": "통당 관심있어요" # {Keyword} 관심있어요.
    #"21-7": "21-7 채권 관련 내용 확인했습니다. 응답 드립니다.",
    #"CP": "CP 발행 관련 정보 감사합니다."
}

recent_messages = set()
last_response_times = {}
response_cooldown_sec = 3

user_name = input("사용자 이름을 입력하세요: ").strip()

def find_input_control(hwnd_main):
    result = []
    def callback(hwnd, lparam):
        class_name = win32gui.GetClassName(hwnd)
        if "Edit" in class_name or "RichEdit" in class_name:
            result.append(hwnd)
        return True
    win32gui.EnumChildWindows(hwnd_main, callback, None)
    return result[0] if result else None

def is_from_other_user(msg_line):
    if any(response in msg_line for response in AUTO_REPLY_RULES.values()):
        return False
    match = re.match(r"\[\d{2}:\d{2}:\d{2}\] ([^:(]+)\(", msg_line)
    if match:
        sender = match.group(1)
        return sender != user_name
    return False

class AutoCloseMessageBox(QMessageBox):
    def __init__(self, timeout=2, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setWindowTitle("실시간 알림")
        self.setIcon(QMessageBox.Information)
        self.setStandardButtons(QMessageBox.Ok)
        self.timer = QtCore.QTimer(self)
        self.timer.timeout.connect(self.accept)
        self.timer.start(timeout * 1000)

class MonitorWindow(QtWidgets.QWidget):
    def __init__(self, window_title, input_hwnd):
        super().__init__()
        self.window_title = window_title
        self.input_hwnd = input_hwnd
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle(f'{self.window_title} Monitor')
        self.setGeometry(300, 300, 600, 500)
        self.layout = QtWidgets.QVBoxLayout()

        self.text_list = QtWidgets.QListWidget()
        self.stats_label = QtWidgets.QLabel("키워드 통계:")
        self.layout.addWidget(self.text_list)
        self.layout.addWidget(self.stats_label)

        self.setLayout(self.layout)

        self.timer = QtCore.QTimer(self)
        self.timer.timeout.connect(self.update_title)
        self.timer.start(1000)

        self.stats_timer = QtCore.QTimer(self)
        self.stats_timer.timeout.connect(self.update_stats)
        self.stats_timer.start(5000)

    def update_title(self):
        now = datetime.datetime.now().strftime("%H:%M:%S")
        self.setWindowTitle(f'{self.window_title} Monitor - {now}')

    def update_stats(self):
        stats_text = " | ".join([f"{k}: {v}" for k, v in keyword_stats.items()])
        self.stats_label.setText(f"키워드 통계: {stats_text}")

    def show_popup(self, message):
        if not is_from_other_user(message):
            return
        box = AutoCloseMessageBox(timeout=2)
        box.setText(message)
        box.exec_()

    def add_message(self, message):
        if message in recent_messages:
            return
        recent_messages.add(message)

        item = QtWidgets.QListWidgetItem(message)
        font = item.font()

        for pattern, (color, bold) in HIGHLIGHT_RULES.items():
            if re.search(pattern, message):
                item.setForeground(color)
                if bold:
                    font.setBold(True)
                    item.setFont(font)
                keyword_stats[pattern] += 1
                self.show_popup(message)
                break

        self.text_list.addItem(item)

        if is_from_other_user(message):
            now = time.time()
            for keyword, response in AUTO_REPLY_RULES.items():
                if keyword in message:
                    last_time = last_response_times.get(keyword, 0)
                    if now - last_time >= response_cooldown_sec:
                        last_response_times[keyword] = now
                        reply_item = QtWidgets.QListWidgetItem(f"[AutoReply] {response}")
                        reply_font = reply_item.font()
                        reply_font.setItalic(True)
                        reply_item.setFont(reply_font)
                        reply_item.setForeground(QtCore.Qt.darkCyan)
                        self.text_list.addItem(reply_item)

                        if self.input_hwnd:
                            win32gui.SendMessage(self.input_hwnd, win32con.WM_SETTEXT, 0, response)
                            win32gui.PostMessage(self.input_hwnd, win32con.WM_KEYDOWN, 0x0D, 0)
                            win32gui.PostMessage(self.input_hwnd, win32con.WM_KEYUP, 0x0D, 0)

        self.text_list.scrollToBottom()
        if self.text_list.count() > 500:
            self.text_list.takeItem(0)

class MessageMonitor(QtCore.QThread):
    new_message = QtCore.pyqtSignal(str)

    def __init__(self, hwnd_list, pid):
        super().__init__()
        self.hwnd_list = hwnd_list
        self.pid = pid
        self.running = True

    def run(self):
        previous_last_lines = ["" for _ in self.hwnd_list]
        k32 = ctypes.WinDLL('kernel32', use_last_error=True)
        process_handle = k32.OpenProcess(PROCESS_VM_READ | PROCESS_QUERY_INFORMATION, False, self.pid)

        while self.running:
            for idx, hwnd in enumerate(self.hwnd_list):
                buffer_size = 131072
                buffer = ctypes.create_unicode_buffer(buffer_size)
                text_length = win32gui.SendMessage(hwnd, win32con.WM_GETTEXTLENGTH, 0, 0)

                if text_length > 0:
                    try:
                        win32gui.SendMessage(hwnd, win32con.WM_GETTEXT, buffer_size, buffer)
                        current_text = buffer.value.strip()
                    except Exception as e:
                        print(f"⚠️ 텍스트 읽기 오류 발생: {e}")
                        current_text = ""

                    if current_text:
                        curr_lines = current_text.splitlines()
                        if curr_lines:
                            last_line = curr_lines[-1].strip()
                            if last_line != previous_last_lines[idx]:
                                now = datetime.datetime.now()
                                date_str = now.strftime("%Y-%m-%d")
                                time_str = now.strftime("%H:%M:%S")
                                filename = f"{date_str}_messenger_messages_Auto.txt"
                                with open(filename, "a", encoding="utf-8") as f:
                                    f.write(f"[{time_str}] {last_line}\n")
                                self.new_message.emit(f"[{time_str}] {last_line}")
                                previous_last_lines[idx] = last_line
            time.sleep(1)

        k32.CloseHandle(process_handle)

    def stop(self):
        self.running = False

def list_all_window_titles():
    titles = []
    def enum_callback(hwnd, lparam):
        if win32gui.IsWindowVisible(hwnd):
            title = win32gui.GetWindowText(hwnd)
            if title:
                titles.append(title)
        return True
    win32gui.EnumWindows(enum_callback, None)
    return titles

def find_all_edit_controls(window_title):
    hwnd_main = win32gui.FindWindow(None, window_title)
    edit_controls = []
    if hwnd_main:
        def callback(hwnd, lparam):
            class_name = win32gui.GetClassName(hwnd)
            if "RichEdit" in class_name:
                edit_controls.append(hwnd)
            return True
        win32gui.EnumChildWindows(hwnd_main, callback, None)
    else:
        print(f"❌ 창 '{window_title}'을(를) 찾을 수 없습니다.")
    return edit_controls, hwnd_main

def get_pid_from_hwnd(hwnd):
    _, pid = win32process.GetWindowThreadProcessId(hwnd)
    return pid

if __name__ == "__main__":
    print("현재 열려있는 창 목록:")
    for title in list_all_window_titles():
        print(f"- {title}")

    keywords_input = input("모니터링할 키워드(공백 또는 쉼표 구분) 입력: ").strip()
    keywords = re.split(r",|\s", keywords_input)
    keywords = list(filter(None, keywords))

    for kw in keywords:
        pattern = kw  # 정규표현식 그대로 사용 (부분 포함 허용)
        HIGHLIGHT_RULES[pattern] = (QtCore.Qt.magenta, True)
        AUTO_REPLY_RULES[pattern] = f"{kw} 관심있어요"

    app = QtWidgets.QApplication(sys.argv)
    window_title = input("모니터링할 메신저 창 이름을 입력하세요: ").strip()
    hwnd_list, hwnd_main = find_all_edit_controls(window_title)

    if hwnd_list:
        pid = get_pid_from_hwnd(hwnd_main)
        input_hwnd = find_input_control(hwnd_main)
        window = MonitorWindow(window_title, input_hwnd)
        window.show()
        monitor = MessageMonitor(hwnd_list, pid)
        monitor.new_message.connect(window.add_message)
        monitor.start()
        sys.exit(app.exec_())
    else:
        print("❌ Edit 컨트롤을 찾을 수 없습니다.")
