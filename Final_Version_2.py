############# version1
# import time
# import win32gui
# import win32con
# import ctypes
# from PyQt5 import QtWidgets, QtCore
# import sys
# import datetime
# import hashlib

# HIGHLIGHT_KEYWORDS = ["팔자", "매도"]
# HIGHLIGHT_KEYWORDS_2 = ["사자", "발행"]

# class MonitorWindow(QtWidgets.QWidget):
#     def __init__(self, window_title):
#         super().__init__()
#         self.window_title = window_title
#         self.init_ui()

#     def init_ui(self):
#         self.setWindowTitle(f'{self.window_title} Monitor')
#         self.setGeometry(300, 300, 600, 400)
#         self.layout = QtWidgets.QVBoxLayout()
#         self.text_list = QtWidgets.QListWidget()
#         self.layout.addWidget(self.text_list)
#         self.setLayout(self.layout)

#         # 타이머로 현재 시간 업데이트
#         self.timer = QtCore.QTimer(self)
#         self.timer.timeout.connect(self.update_title)
#         self.timer.start(1000)

#     def update_title(self):
#         now = datetime.datetime.now().strftime("%H:%M:%S")
#         self.setWindowTitle(f'{self.window_title} Monitor - {now}')

#     def add_message(self, message):
#         item = QtWidgets.QListWidgetItem(message)
#         if any(keyword in message for keyword in HIGHLIGHT_KEYWORDS):
#             item.setForeground(QtCore.Qt.red)
#         if any(keyword in message for keyword in HIGHLIGHT_KEYWORDS_2):
#             item.setForeground(QtCore.Qt.blue)
#         self.text_list.addItem(item)
#         self.text_list.scrollToBottom()

# class MessageMonitor(QtCore.QThread):
#     new_message = QtCore.pyqtSignal(str)

#     def __init__(self, hwnd_list):
#         super().__init__()
#         self.hwnd_list = hwnd_list
#         self.running = True

#     def run(self):
#         last_texts = ["" for _ in self.hwnd_list]

#         while self.running:
#             for idx, hwnd in enumerate(self.hwnd_list):
#                 buffer_size = 131072  # 128KB로 확장
#                 buffer = ctypes.create_unicode_buffer(buffer_size)
#                 text_length = win32gui.SendMessage(hwnd, win32con.WM_GETTEXTLENGTH, 0, 0)

#                 if text_length > 0:
#                     try:
#                         win32gui.SendMessage(hwnd, win32con.WM_GETTEXT, buffer_size, buffer)
#                         text = buffer.value.strip()
#                     except Exception as e:
#                         print(f"⚠️ 텍스트 읽기 오류 발생: {e}")
#                         text = ""  # 읽기 실패 시 그냥 빈 문자열 처리

#                     if text != last_texts[idx]:
#                         new_part = text[len(last_texts[idx]):]

#                         for line in new_part.splitlines():
#                             line = line.strip()
#                             if line:
#                                 now = datetime.datetime.now()
#                                 date_str = now.strftime("%Y-%m-%d")
#                                 time_str = now.strftime("%H:%M:%S")
#                                 filename = f"{date_str}_messenger_messages.txt"

#                                 with open(filename, "a", encoding="utf-8") as f:
#                                     f.write(f"[{time_str}] {line}\n")

#                                 self.new_message.emit(f"[{time_str}] {line}")

#                         last_texts[idx] = text
#             time.sleep(1)

#     def stop(self):
#         self.running = False

# def list_all_window_titles():
#     titles = []

#     def enum_callback(hwnd, lparam):
#         if win32gui.IsWindowVisible(hwnd):
#             title = win32gui.GetWindowText(hwnd)
#             if title:
#                 titles.append(title)
#         return True

#     win32gui.EnumWindows(enum_callback, None)
#     return titles

# def find_all_edit_controls(window_title):
#     hwnd_main = win32gui.FindWindow(None, window_title)
#     edit_controls = []

#     if hwnd_main:
#         def callback(hwnd, lparam):
#             class_name = win32gui.GetClassName(hwnd)
#             if "RichEdit" in class_name:
#                 edit_controls.append(hwnd)
#             return True

#         win32gui.EnumChildWindows(hwnd_main, callback, None)
#     else:
#         print(f"❌ 창 '{window_title}'을(를) 찾을 수 없습니다.")

#     return edit_controls

# if __name__ == "__main__":
#     print("현재 열려있는 창 목록:")
#     for title in list_all_window_titles():
#         print(f"- {title}")

#     app = QtWidgets.QApplication(sys.argv)

#     window_title = input("모니터링할 메신저 창 이름을 입력하세요: ").strip()
#     hwnd_list = find_all_edit_controls(window_title)

#     if hwnd_list:
#         window = MonitorWindow(window_title)
#         window.show()
#         monitor = MessageMonitor(hwnd_list)
#         monitor.new_message.connect(window.add_message)
#         monitor.start()
#         sys.exit(app.exec_())
#     else:
#         print("❌ Edit 컨트롤을 찾을 수 없습니다.")

## Richtext Controls.
import time
import ctypes
import psutil
import win32gui
import win32process
import win32con
from PyQt5 import QtWidgets, QtCore
import sys
import datetime

PROCESS_VM_READ = 0x0010
PROCESS_QUERY_INFORMATION = 0x0400

HIGHLIGHT_KEYWORDS = ["팔자", "매도"]
HIGHLIGHT_KEYWORDS_2 = ["사자", "발행"]

class MonitorWindow(QtWidgets.QWidget):
    def __init__(self, window_title):
        super().__init__()
        self.window_title = window_title
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle(f'{self.window_title} Monitor')
        self.setGeometry(300, 300, 600, 400)
        self.layout = QtWidgets.QVBoxLayout()
        self.text_list = QtWidgets.QListWidget()
        self.layout.addWidget(self.text_list)
        self.setLayout(self.layout)

        self.timer = QtCore.QTimer(self)
        self.timer.timeout.connect(self.update_title)
        self.timer.start(1000)

    def update_title(self):
        now = datetime.datetime.now().strftime("%H:%M:%S")
        self.setWindowTitle(f'{self.window_title} Monitor - {now}')

    def add_message(self, message):
        item = QtWidgets.QListWidgetItem(message)
        if any(keyword in message for keyword in HIGHLIGHT_KEYWORDS):
            item.setForeground(QtCore.Qt.red)
        elif any(keyword in message for keyword in HIGHLIGHT_KEYWORDS_2):
            item.setForeground(QtCore.Qt.blue)
        self.text_list.addItem(item)
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
                                filename = f"{date_str}_messenger_messages.txt"

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

    app = QtWidgets.QApplication(sys.argv)
    window_title = input("모니터링할 메신저 창 이름을 입력하세요: ").strip()
    hwnd_list, hwnd_main = find_all_edit_controls(window_title)

    if hwnd_list:
        pid = get_pid_from_hwnd(hwnd_main)
        window = MonitorWindow(window_title)
        window.show()
        monitor = MessageMonitor(hwnd_list, pid)
        monitor.new_message.connect(window.add_message)
        monitor.start()
        sys.exit(app.exec_())
    else:
        print("❌ Edit 컨트롤을 찾을 수 없습니다.")
