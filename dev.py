import sys
import time
import subprocess
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler


class ChangeHandler(FileSystemEventHandler):
    def __init__(self):
        self.process = None
        self.restart_program()

    def restart_program(self):
        if self.process:
            self.process.kill()
            self.process.wait()

        # 启动主程序
        self.process = subprocess.Popen([sys.executable, 'dota2_clipboard.py'])

    def on_modified(self, event):
        if event.src_path.endswith('.py'):
            print(f"\n检测到文件变化: {event.src_path}")
            print("重启应用...")
            self.restart_program()


if __name__ == "__main__":
    print("启动开发模式...")
    print("监控文件变化中...")

    event_handler = ChangeHandler()
    observer = Observer()
    observer.schedule(event_handler, path='.', recursive=False)
    observer.start()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
        if event_handler.process:
            event_handler.process.kill()
    observer.join()
