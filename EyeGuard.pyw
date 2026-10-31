# -*- coding: utf-8 -*-
"""
护眼管家 EyeGuard（桌面版）
- 开机自启、无窗口静默运行（托盘图标可暂停/退出）
- 摄像头本地人脸检测（不联网、不保存画面），持续注视达阈值即强制休息
- 休息屏：Chrome Kiosk 全屏（覆盖任务栏）+ Aerial 风格实拍绿植视频 + 语音播报"休息一下"
"""
import os
import sys
import json
import time
import logging
import threading
import subprocess
import ctypes
import urllib.parse

# ---------- 单实例守护 ----------
MUTEX = ctypes.windll.kernel32.CreateMutexW(None, False, "EyeGuard_SingleInstance")
if ctypes.windll.kernel32.GetLastError() == 183:  # ERROR_ALREADY_EXISTS
    sys.exit(0)

import cv2
import pystray
from PIL import Image, ImageDraw
from pystray import Menu as TrayMenu, MenuItem as TrayItem

BASE = os.path.dirname(os.path.abspath(__file__))
CONFIG_PATH = os.path.join(BASE, "config.json")
LOG_PATH = os.path.join(BASE, "eyeguard.log")
REST_HTML = os.path.join(BASE, "rest.html")

CHROME_CANDIDATES = [
    r"C:\Program Files\Google\Chrome\Application\chrome.exe",
    r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
    r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
    r"C:\Program Files\Microsoft\Edge\Application\msedge.exe",
]

logging.basicConfig(filename=LOG_PATH, level=logging.INFO,
                    format="%(asctime)s %(levelname)s %(message)s", encoding="utf-8")


def load_config():
    cfg = {"interval_min": 30, "break_sec": 20, "use_camera": True}
    try:
        with open(CONFIG_PATH, "r", encoding="utf-8") as f:
            cfg.update(json.load(f))
    except Exception:
        pass
    return cfg


def find_browser():
    for p in CHROME_CANDIDATES:
        if os.path.exists(p):
            return p
    return None


def sapi_speak(text):
    """备用语音：Windows SAPI（浏览器语音不可用时兜底）"""
    try:
        cmd = ("Add-Type -AssemblyName System.Speech; "
               "$s = New-Object System.Speech.Synthesis.SpeechSynthesizer; "
               "$s.Speak('{}');".format(text))
        subprocess.Popen(
            ["powershell", "-NoProfile", "-WindowStyle", "Hidden", "-Command", cmd],
            creationflags=subprocess.CREATE_NO_WINDOW)
    except Exception as e:
        logging.warning("SAPI TTS failed: %s", e)


class CameraMonitor(threading.Thread):
    """后台线程：每秒 1 次人脸检测（低占用），更新 face_seen 状态"""

    def __init__(self):
        super().__init__(daemon=True)
        self.face_seen = False
        self.face_lost_at = 0.0
        self.camera_ok = False
        self._stop = False

    def run(self):
        cap = None
        try:
            cascade = cv2.CascadeClassifier(
                cv2.data.haarcascades + "haarcascade_frontalface_default.xml")
            cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
            cap.set(cv2.CAP_PROP_FRAME_WIDTH, 320)
            cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 240)
            if not cap.isOpened():
                logging.warning("camera unavailable, fallback to pure timer")
                return
            self.camera_ok = True
            logging.info("camera opened")
            last = 0.0
            while not self._stop:
                time.sleep(0.2)
                now = time.time()
                if now - last < 1.0:
                    continue
                last = now
                ok, frame = cap.read()
                if not ok:
                    self.camera_ok = False
                    logging.warning("camera read failed, fallback to pure timer")
                    break
                gray = cv2.cvtColor(cv2.resize(frame, (320, 240)), cv2.COLOR_BGR2GRAY)
                faces = cascade.detectMultiScale(gray, 1.1, 5, minSize=(60, 60))
                seen = len(faces) > 0
                if seen:
                    self.face_seen = True
                else:
                    if self.face_seen:
                        self.face_lost_at = time.time()
                    self.face_seen = False
        except Exception as e:
            logging.warning("camera thread error: %s", e)
        finally:
            if cap is not None:
                cap.release()

    def stop(self):
        self._stop = True


class EyeGuard:
    def __init__(self):
        self.cfg = load_config()
        self.interval_sec = int(self.cfg["interval_min"]) * 60
        self.break_sec = int(self.cfg["break_sec"])
        self.watched = 0
        self.paused = False
        self.rest_active = False
        self.cam = CameraMonitor()
        if self.cfg.get("use_camera", True):
            self.cam.start()
        self._build_tray()

    # ---------- 计时线程 ----------
    def _timer_loop(self):
        while True:
            time.sleep(1)
            if self.paused or self.rest_active:
                continue
            watching = True
            if self.cam.camera_ok:
                away = (not self.cam.face_seen) and \
                       (time.time() - self.cam.face_lost_at > 10)
                watching = not away
            if watching:
                self.watched += 1
                if self.watched >= self.interval_sec:
                    self.start_rest()
            else:
                self.watched = 0

    # ---------- 托盘 ----------
    def _build_tray(self):
        img = Image.new("RGBA", (64, 64), (0, 0, 0, 0))
        d = ImageDraw.Draw(img)
        d.ellipse([4, 4, 60, 60], fill=(26, 127, 90, 255))
        d.ellipse([22, 22, 42, 42], fill=(232, 245, 238, 255))

        def toggle_pause(icon, item):
            self.paused = not self.paused

        menu = TrayMenu(
            TrayItem("立即休息", action=lambda i, it: self.start_rest()),
            TrayItem("暂停监控", action=toggle_pause,
                     checked=lambda item: self.paused),
            TrayItem("退出护眼管家", action=lambda i, it: self.quit(i)),
        )
        self.icon = pystray.Icon("EyeGuard", img, "护眼管家", menu)
        self.icon.run_detached()

    def quit(self, icon=None):
        logging.info("exit")
        self.cam.stop()
        try:
            self.icon.stop()
        except Exception:
            pass
        os._exit(0)

    # ---------- 强制休息 ----------
    def start_rest(self):
        if self.rest_active:
            return
        self.rest_active = True
        logging.info("break triggered after %ss watching", self.watched)

        browser = find_browser()
        if browser is None or not os.path.exists(REST_HTML):
            logging.error("no browser or rest.html, SAPI fallback")
            sapi_speak("休息一下，请离开屏幕，望向远处放松眼睛")
            time.sleep(self.break_sec)
            sapi_speak("休息完成，欢迎回来")
            self.rest_active = False
            self.watched = 0
            return

        # Kiosk 全屏：无边框、置顶、覆盖任务栏
        params = urllib.parse.urlencode({"break": self.break_sec})
        url = "file:///" + REST_HTML.replace("\\", "/") + "?" + params
        profile = os.path.join(BASE, "Profile")
        try:
            proc = subprocess.Popen([
                browser, "--kiosk", url,
                f"--user-data-dir={profile}",
                "--no-first-run", "--no-default-browser-check",
                "--autoplay-policy=no-user-gesture-required",
                "--disable-features=TranslateUI",
            ])
        except Exception as e:
            logging.error("browser launch failed: %s", e)
            sapi_speak("休息一下，请离开屏幕，望向远处放松眼睛")
            time.sleep(self.break_sec)
            self.rest_active = False
            self.watched = 0
            return

        # 休息倒计时结束后自动关闭全屏窗口（+2.5s 缓冲让页面播完提示）
        def _close_later():
            time.sleep(self.break_sec + 2.5)
            try:
                proc.terminate()
                proc.wait(timeout=5)
            except Exception:
                try:
                    proc.kill()
                except Exception:
                    pass
            logging.info("break finished, timer reset")
            self.watched = 0
            self.rest_active = False

        threading.Thread(target=_close_later, daemon=True).start()

    def run(self):
        self._timer_loop()


if __name__ == "__main__":
    if "--selftest" in sys.argv:
        g = EyeGuard()
        print("config:", g.cfg, flush=True)
        print("opencv:", cv2.__version__, flush=True)
        time.sleep(2)  # 给摄像头 2 秒初始化
        print("camera_open:", g.cam.camera_ok, flush=True)
        print("browser:", find_browser(), flush=True)
        print("rest.html:", os.path.exists(REST_HTML), flush=True)
        g.quit()
    else:
        EyeGuard().run()
