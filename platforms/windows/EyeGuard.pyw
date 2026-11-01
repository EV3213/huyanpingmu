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

# ---------- 多语言文案 ----------
I18N = {
    "zh": {
        "tray_title": "护眼管家",
        "rest_now": "立即休息",
        "pause": "暂停监控",
        "exit": "退出护眼管家",
        "language": "语言 / Language：中文",
        "theme": "主题色",
        "theme_custom": "自定义颜色…",
        "speak_rest": "休息一下，离开屏幕，看看远处，让眼睛放松一下吧",
        "speak_done": "休息完成，欢迎回来",
    },
    "en": {
        "tray_title": "EyeGuard",
        "rest_now": "Take a break now",
        "pause": "Pause monitoring",
        "exit": "Exit EyeGuard",
        "language": "Language / 语言：English",
        "theme": "Theme color",
        "theme_custom": "Custom color…",
        "speak_rest": "Time for a break. Please look away from the screen and relax your eyes.",
        "speak_done": "Break finished. Welcome back.",
    },
}

# 主题色预设（与移动端一致）
THEME_PRESETS = [
    ("森林绿", "Forest", "#12644A"),
    ("青竹", "Bamboo", "#2E7D5B"),
    ("松石青", "Teal", "#0E6B6B"),
    ("远山蓝", "Azure", "#2A5CAA"),
    ("靛蓝", "Indigo", "#4B3FA8"),
    ("葡萄紫", "Grape", "#7A3E9D"),
    ("玫瑰红", "Rose", "#A63B63"),
    ("暖橙", "Amber", "#B85C1E"),
    ("琥珀黄", "Ochre", "#A8791B"),
    ("石墨灰", "Graphite", "#3C4744"),
]
DEFAULT_THEME = "#12644A"


def normalize_theme(value):
    """校验主题色，非法时回退默认"""
    if isinstance(value, str) and len(value) == 7 and value.startswith("#"):
        try:
            int(value[1:], 16)
            return value.upper()
        except ValueError:
            pass
    return DEFAULT_THEME


def save_config(cfg):
    try:
        with open(CONFIG_PATH, "w", encoding="utf-8") as f:
            json.dump(cfg, f, ensure_ascii=False, indent=2)
    except Exception as e:
        logging.warning("save config failed: %s", e)


def load_config():
    cfg = {"interval_min": 30, "break_sec": 20, "use_camera": True,
           "lang": "zh", "theme_color": DEFAULT_THEME}
    try:
        with open(CONFIG_PATH, "r", encoding="utf-8") as f:
            cfg.update(json.load(f))
    except Exception:
        pass
    if cfg.get("lang") not in I18N:
        cfg["lang"] = "zh"
    cfg["theme_color"] = normalize_theme(cfg.get("theme_color"))
    return cfg


def find_browser():
    for p in CHROME_CANDIDATES:
        if os.path.exists(p):
            return p
    return None


def sapi_speak(text):
    """备用语音：Windows SAPI（浏览器语音不可用时兜底，语气放缓）"""
    try:
        cmd = ("Add-Type -AssemblyName System.Speech; "
               "$s = New-Object System.Speech.Synthesis.SpeechSynthesizer; "
               "$s.Rate = -1; $s.Volume = 95; "
               "foreach ($n in @('Microsoft Xiaoxiao', 'Microsoft Huihui', 'Microsoft Yaoyao')) { "
               "  try { $s.SelectVoice($n); break } catch {} }; "
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
            cascade = None
            candidates = [os.path.join(BASE, "haarcascade_frontalface_default.xml")]
            try:
                candidates.append(cv2.data.haarcascades +
                                  "haarcascade_frontalface_default.xml")
            except Exception:
                pass
            for path in candidates:
                if path and os.path.exists(path):
                    c = cv2.CascadeClassifier(path)
                    if not c.empty():
                        cascade = c
                        logging.info("face model loaded: %s" % path)
                        break
            if cascade is None:
                logging.warning("face model unavailable, fallback to pure timer")
                return
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

    # ---------- 多语言 ----------
    def tr(self, key):
        return I18N[self.cfg.get("lang", "zh")][key]

    def toggle_lang(self, icon=None, item=None):
        self.cfg["lang"] = "en" if self.cfg.get("lang") == "zh" else "zh"
        save_config(self.cfg)
        logging.info("language switched to %s", self.cfg["lang"])
        try:
            self.icon.update_menu()
        except Exception:
            pass

    # ---------- 托盘 ----------
    def _tray_image(self):
        """托盘图标跟随主题色"""
        try:
            rgb = tuple(int(self.cfg["theme_color"][i:i + 2], 16) for i in (1, 3, 5))
        except Exception:
            rgb = (18, 100, 74)
        img = Image.new("RGBA", (64, 64), (0, 0, 0, 0))
        d = ImageDraw.Draw(img)
        d.ellipse([4, 4, 60, 60], fill=rgb + (255,))
        d.ellipse([22, 22, 42, 42], fill=(255, 255, 255, 255))
        return img

    def _refresh_tray(self):
        try:
            self.icon.icon = self._tray_image()
            self.icon.update_menu()
        except Exception:
            pass

    def _build_tray(self):
        def toggle_pause(icon, item):
            self.paused = not self.paused

        # 主题色子菜单：预设 + 自定义
        def make_theme_menu():
            items = []
            for zh_name, en_name, hexv in THEME_PRESETS:
                def set_color(icon=None, item=None, _h=hexv):
                    self.cfg["theme_color"] = _h
                    save_config(self.cfg)
                    logging.info("theme color -> %s", _h)
                    self._refresh_tray()
                items.append(TrayItem(
                    lambda item, _h=hexv, _z=zh_name, _e=en_name:
                        ("%s %s" % ("●" if self.cfg.get("theme_color") == _h else "○",
                                    _z if self.cfg.get("lang", "zh") == "zh" else _e)),
                    action=set_color))
            return items

        def custom_color(icon=None, item=None):
            try:
                import tkinter as tk
                from tkinter import colorchooser
                root = tk.Tk()
                root.withdraw()
                _, hexv = colorchooser.askcolor(
                    color=self.cfg.get("theme_color", DEFAULT_THEME),
                    title=self.tr("theme"))
                root.destroy()
                if hexv:
                    self.cfg["theme_color"] = normalize_theme(
                        hexv if hexv.startswith("#") else "#" + hexv)
                    save_config(self.cfg)
                    logging.info("theme color -> %s", self.cfg["theme_color"])
                    self._refresh_tray()
            except Exception as e:
                logging.warning("custom color failed: %s", e)

        menu = TrayMenu(
            TrayItem(lambda item: self.tr("rest_now"), action=lambda i, it: self.start_rest()),
            TrayItem(lambda item: self.tr("pause"), action=toggle_pause,
                     checked=lambda item: self.paused),
            TrayItem(lambda item: self.tr("language"), action=self.toggle_lang),
            TrayItem(lambda item: self.tr("theme"),
                     TrayMenu(*make_theme_menu(),
                              TrayItem(lambda item: self.tr("theme_custom"),
                                       action=custom_color))),
            TrayItem(lambda item: self.tr("exit"), action=lambda i, it: self.quit(i)),
        )
        self.icon = pystray.Icon("EyeGuard", self._tray_image(),
                                 self.tr("tray_title"), menu)
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
            sapi_speak(self.tr("speak_rest"))
            time.sleep(self.break_sec)
            sapi_speak(self.tr("speak_done"))
            self.rest_active = False
            self.watched = 0
            return

        # Kiosk 全屏：无边框、置顶、覆盖任务栏
        params = urllib.parse.urlencode({"break": self.break_sec,
                                         "lang": self.cfg.get("lang", "zh"),
                                         "theme": self.cfg.get("theme_color", DEFAULT_THEME).lstrip("#")})
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
            sapi_speak(self.tr("speak_rest"))
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
