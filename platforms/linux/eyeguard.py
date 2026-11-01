#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""护眼管家 EyeGuard（Linux / macOS 桌面版）

- 后台静默运行，托盘图标（pystray）可暂停 / 立即休息 / 切换语言 / 退出
- 摄像头本地人脸检测（OpenCV Haar），持续注视达阈值即强制休息
- 休息屏：浏览器 kiosk 全屏播放 rest.html（Aerial 风格实拍绿植 + 神经语音）
  没有浏览器时退回 Tk 全屏 + 音频播放 / 系统 TTS
- 开机自启：Linux 写 XDG autostart，macOS 写 LaunchAgent

用法：
    ./install.sh            # 安装（复制文件 + 注册自启）
    eyeguard.py --status    # 查看状态
    eyeguard.py --rest      # 立刻休息一次（测试）
    eyeguard.py --uninstall # 卸载自启
"""
from __future__ import annotations

import json
import logging
import os
import platform
import shutil
import subprocess
import sys
import threading
import time
import urllib.parse

APP_ID = "eyeguard"
IS_MAC = platform.system() == "Darwin"
IS_LINUX = platform.system() == "Linux"

HERE = os.path.dirname(os.path.abspath(__file__))

# 配置放在用户目录，升级程序不丢设置
CFG_DIR = os.path.join(
    os.path.expanduser("~"),
    "Library/Application Support/EyeGuard" if IS_MAC else ".config/eyeguard",
)
LOG_PATH = os.path.join(CFG_DIR, "eyeguard.log")
CONFIG_PATH = os.path.join(CFG_DIR, "config.json")
LOCK_PATH = os.path.join(CFG_DIR, "eyeguard.lock")

REST_HTML = os.path.join(HERE, "rest.html")
MODEL_PATH = os.path.join(HERE, "haarcascade_frontalface_default.xml")

DEFAULT_CFG = {
    "interval_min": 30,
    "break_sec": 20,
    "use_camera": True,
    "lang": "zh",
    "theme_color": "#12644A",
}

I18N = {
    "zh": {
        "app": "护眼管家",
        "rest_now": "立即休息",
        "pause": "暂停监控",
        "resume": "继续监控",
        "language": "语言 / Language：中文",
        "theme": "主题色",
        "theme_custom": "自定义颜色…",
        "exit": "退出护眼管家",
        "big": "休息一下",
        "tip": "请离开屏幕，望向 6 米以外的远处",
        "done": "休息完成，欢迎回来",
        "speak_rest": "休息一下，离开屏幕，看看远处，让眼睛放松一下吧",
        "speak_mid": "再坚持一下，记得多眨眨眼",
        "speak_done": "休息完成，欢迎回来",
    },
    "en": {
        "app": "EyeGuard",
        "rest_now": "Take a break now",
        "pause": "Pause monitoring",
        "resume": "Resume monitoring",
        "language": "Language / 语言：English",
        "theme": "Theme color",
        "theme_custom": "Custom color…",
        "exit": "Exit EyeGuard",
        "big": "Take a Break",
        "tip": "Look away from the screen at something 6 meters away",
        "done": "Break finished. Welcome back.",
        "speak_rest": "Time for a break. Please look away from the screen and relax your eyes.",
        "speak_mid": "Hang in there a little longer. Remember to blink.",
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

BROWSERS = [
    "google-chrome",
    "google-chrome-stable",
    "chromium",
    "chromium-browser",
    "brave-browser",
    "microsoft-edge",
    "vivaldi",
]
MAC_BROWSERS = [
    "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
    "/Applications/Microsoft Edge.app/Contents/MacOS/Microsoft Edge",
    "/Applications/Brave Browser.app/Contents/MacOS/Brave Browser",
    "/Applications/Chromium.app/Contents/MacOS/Chromium",
]

os.makedirs(CFG_DIR, exist_ok=True)
logging.basicConfig(
    filename=LOG_PATH,
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s",
    encoding="utf-8",
)


# ---------------- 配置 ----------------
def load_config() -> dict:
    cfg = dict(DEFAULT_CFG)
    try:
        with open(CONFIG_PATH, "r", encoding="utf-8") as f:
            cfg.update(json.load(f))
    except Exception:
        pass
    if cfg.get("lang") not in I18N:
        cfg["lang"] = "zh"
    cfg["theme_color"] = normalize_theme(cfg.get("theme_color"))
    return cfg


def save_config(cfg: dict) -> None:
    try:
        with open(CONFIG_PATH, "w", encoding="utf-8") as f:
            json.dump(cfg, f, ensure_ascii=False, indent=2)
    except Exception as e:
        logging.warning("save config failed: %s", e)


def tr(cfg: dict, key: str) -> str:
    return I18N[cfg.get("lang", "zh")][key]


# ---------------- 单实例 ----------------
def acquire_lock() -> bool:
    try:
        if os.path.exists(LOCK_PATH):
            with open(LOCK_PATH, "r", encoding="utf-8") as f:
                old = int((f.read() or "0").strip() or 0)
            if old and old != os.getpid():
                try:
                    os.kill(old, 0)
                    return False  # 进程还活着
                except OSError:
                    pass  # 僵尸锁，接管
        with open(LOCK_PATH, "w", encoding="utf-8") as f:
            f.write(str(os.getpid()))
        return True
    except Exception:
        return True


def release_lock() -> None:
    try:
        if os.path.exists(LOCK_PATH):
            os.remove(LOCK_PATH)
    except Exception:
        pass


# ---------------- 音频 / 语音 ----------------
def play_file(path: str) -> bool:
    """用系统播放器播 mp3（比 TTS 自然得多），成功返回 True。"""
    if not os.path.exists(path):
        return False
    players = ["afplay"] if IS_MAC else []
    players += ["ffplay", "mpg123", "mpv", "paplay"]
    for p in players:
        exe = shutil.which(p)
        if not exe:
            continue
        try:
            if p == "ffplay":
                cmd = [exe, "-nodisp", "-autoexit", "-loglevel", "quiet", path]
            elif p == "mpv":
                cmd = [exe, "--no-video", "--really-quiet", path]
            else:
                cmd = [exe, path]
            subprocess.Popen(cmd,
                             stdout=subprocess.DEVNULL,
                             stderr=subprocess.DEVNULL,
                             start_new_session=True)
            return True
        except Exception:
            continue
    return False


def speak(cfg: dict, key: str) -> None:
    """优先播预生成语音，其次系统 TTS。"""
    path = os.path.join(HERE, "voice_%s_%s.mp3" % (
        {"speak_rest": "rest", "speak_mid": "mid", "speak_done": "done"}[key],
        cfg.get("lang", "zh"),
    ))
    if play_file(path):
        return
    text = tr(cfg, key)
    try:
        if IS_MAC:
            voice = "Tingting" if cfg.get("lang") == "zh" else "Samantha"
            subprocess.Popen(["say", "-v", voice, "-r", "165", text],
                             stdout=subprocess.DEVNULL,
                             stderr=subprocess.DEVNULL)
        else:
            for cmd in (["espeak-ng", "-v", "cmn", "-s", "150", text],
                        ["spd-say", "-w", text]):
                if shutil.which(cmd[0]):
                    subprocess.Popen(cmd, stdout=subprocess.DEVNULL,
                                     stderr=subprocess.DEVNULL)
                    return
    except Exception as e:
        logging.warning("tts failed: %s", e)


# ---------------- 摄像头 ----------------
class CameraMonitor(threading.Thread):
    """每秒 1 帧做人脸检测，更新 face_seen / camera_ok。"""

    def __init__(self) -> None:
        super().__init__(daemon=True)
        self.face_seen = False
        self.face_lost_at = 0.0
        self.camera_ok = False
        self._stop = False

    def run(self) -> None:
        cap = None
        try:
            import cv2
        except Exception as e:
            logging.warning("opencv unavailable: %s", e)
            return

        cascade = None
        for path in (MODEL_PATH, getattr(cv2, "data", None) and
                     os.path.join(cv2.data.haarcascades,
                                  "haarcascade_frontalface_default.xml")):
            if path and os.path.exists(path):
                c = cv2.CascadeClassifier(path)
                if not c.empty():
                    cascade = c
                    logging.info("face model loaded: %s", path)
                    break
        if cascade is None:
            logging.warning("face model missing, pure timer mode")
            return

        backend = cv2.CAP_AVFOUNDATION if IS_MAC else cv2.CAP_V4L2
        try:
            cap = cv2.VideoCapture(0, backend)
        except Exception:
            cap = cv2.VideoCapture(0)
        if not cap or not cap.isOpened():
            if cap:
                cap.release()
            cap = cv2.VideoCapture(0)  # 换默认后端再试一次
        if not cap or not cap.isOpened():
            logging.warning("camera unavailable, pure timer mode")
            return

        cap.set(cv2.CAP_PROP_FRAME_WIDTH, 320)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 240)
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
                logging.warning("camera read failed, pure timer mode")
                break
            gray = cv2.cvtColor(cv2.resize(frame, (320, 240)), cv2.COLOR_BGR2GRAY)
            faces = cascade.detectMultiScale(gray, 1.1, 5, minSize=(60, 60))
            if len(faces) > 0:
                self.face_seen = True
            else:
                if self.face_seen:
                    self.face_lost_at = time.time()
                self.face_seen = False

        if cap is not None:
            cap.release()

    def stop(self) -> None:
        self._stop = True


# ---------------- 休息屏 ----------------
def find_browser() -> str | None:
    if IS_MAC:
        for p in MAC_BROWSERS:
            if os.path.exists(p):
                return p
        return None
    for name in BROWSERS:
        exe = shutil.which(name)
        if exe:
            return exe
    return None


def tk_fallback(cfg: dict, break_sec: int) -> None:
    """没有 Chromium 系浏览器时：Tk 全屏 + 图片 + 倒计时 + 语音。"""
    speak(cfg, "speak_rest")
    try:
        import tkinter as tk
        from PIL import Image, ImageTk
    except Exception:
        time.sleep(break_sec)
        speak(cfg, "speak_done")
        return

    root = tk.Tk()
    root.attributes("-fullscreen", True)
    root.configure(bg="black")
    root.attributes("-topmost", True)
    try:
        img = Image.open(os.path.join(HERE, "rest-bg.png"))
        img = img.resize((root.winfo_screenwidth(), root.winfo_screenheight()))
        photo = ImageTk.PhotoImage(img)
        tk.Label(root, image=photo, bd=0).pack(fill="both", expand=True)
        root._photo = photo  # 防 GC
    except Exception:
        pass
    label = tk.Label(root, text=tr(cfg, "big"), font=("Helvetica", 54, "bold"),
                     fg="white", bg="black")
    label.place(relx=0.5, rely=0.42, anchor="center")
    counter = tk.Label(root, text=str(break_sec), font=("Helvetica", 34),
                       fg="#cfe9dd", bg="black")
    counter.place(relx=0.5, rely=0.55, anchor="center")

    def tick(n: int) -> None:
        if n <= 0:
            speak(cfg, "speak_done")
            root.destroy()
            return
        counter.config(text=str(n))
        if n == break_sec // 2:
            speak(cfg, "speak_mid")
        root.after(1000, tick, n - 1)

    root.after(1000, tick, break_sec - 1)
    root.mainloop()


def show_break(cfg: dict, break_sec: int) -> None:
    browser = find_browser()
    if not browser or not os.path.exists(REST_HTML):
        logging.info("no chromium browser, tk fallback")
        tk_fallback(cfg, break_sec)
        return
    q = urllib.parse.urlencode({"break": break_sec, "lang": cfg.get("lang", "zh"),
                                "theme": cfg.get("theme_color", DEFAULT_THEME).lstrip("#")})
    url = "file://" + REST_HTML + "?" + q
    profile = os.path.join(CFG_DIR, "browser-profile")
    args = [
        browser, "--kiosk", url,
        "--user-data-dir=" + profile,
        "--no-first-run", "--no-default-browser-check",
        "--autoplay-policy=no-user-gesture-required",
        "--disable-features=TranslateUI",
    ]
    try:
        proc = subprocess.Popen(args, stdout=subprocess.DEVNULL,
                                stderr=subprocess.DEVNULL)
    except Exception as e:
        logging.warning("browser launch failed: %s", e)
        tk_fallback(cfg, break_sec)
        return
    try:
        proc.wait(timeout=break_sec + 6)
    except subprocess.TimeoutExpired:
        proc.terminate()
        try:
            proc.wait(timeout=4)
        except Exception:
            proc.kill()


# ---------------- 主程序 ----------------
class EyeGuard:
    def __init__(self) -> None:
        self.cfg = load_config()
        self.interval_sec = max(1, int(self.cfg["interval_min"])) * 60
        self.break_sec = max(5, int(self.cfg["break_sec"]))
        self.watched = 0
        self.paused = False
        self.rest_active = False
        self.cam = CameraMonitor()
        if self.cfg.get("use_camera", True):
            self.cam.start()
        self.icon = None
        self._build_tray()

    # ---- 托盘图标：主题色底 + 白色眼睛 ----
    def _icon_image(self):
        from PIL import Image, ImageDraw
        try:
            rgb = tuple(int(self.cfg["theme_color"][i:i + 2], 16) for i in (1, 3, 5))
        except Exception:
            rgb = (18, 100, 74)
        img = Image.new("RGBA", (64, 64), (0, 0, 0, 0))
        d = ImageDraw.Draw(img)
        d.ellipse([4, 4, 60, 60], fill=rgb + (255,))
        d.ellipse([22, 22, 42, 42], fill=(255, 255, 255, 255))
        return img

    def _refresh_tray(self) -> None:
        try:
            self.icon.icon = self._icon_image()
            self.icon.update_menu()
        except Exception:
            pass

    def _build_tray(self) -> None:
        try:
            import pystray
            from pystray import Menu, MenuItem
        except Exception as e:
            logging.warning("pystray unavailable, headless mode: %s", e)
            return

        def toggle_pause(icon, item):
            self.paused = not self.paused
            icon.update_menu()

        def toggle_lang(icon, item):
            self.cfg["lang"] = "en" if self.cfg.get("lang") == "zh" else "zh"
            save_config(self.cfg)
            icon.update_menu()

        # 主题色子菜单：预设 + 自定义
        def make_theme_menu():
            items = []
            for zh_name, en_name, hexv in THEME_PRESETS:
                def set_color(icon=None, item=None, _h=hexv):
                    self.cfg["theme_color"] = _h
                    save_config(self.cfg)
                    logging.info("theme color -> %s", _h)
                    self._refresh_tray()
                items.append(MenuItem(
                    lambda i, _h=hexv, _z=zh_name, _e=en_name:
                        ("%s %s" % ("●" if self.cfg.get("theme_color") == _h else "○",
                                    _z if self.cfg.get("lang", "zh") == "zh" else _e)),
                    set_color))
            return items

        def custom_color(icon=None, item=None):
            try:
                import tkinter as tk
                from tkinter import colorchooser
                root = tk.Tk()
                root.withdraw()
                _, hexv = colorchooser.askcolor(
                    color=self.cfg.get("theme_color", DEFAULT_THEME),
                    title=tr(self.cfg, "theme"))
                root.destroy()
                if hexv:
                    self.cfg["theme_color"] = normalize_theme(
                        hexv if hexv.startswith("#") else "#" + hexv)
                    save_config(self.cfg)
                    logging.info("theme color -> %s", self.cfg["theme_color"])
                    self._refresh_tray()
            except Exception as e:
                logging.warning("custom color failed: %s", e)

        menu = Menu(
            MenuItem(lambda i: tr(self.cfg, "rest_now"),
                     lambda i, it: threading.Thread(
                         target=self.start_rest, daemon=True).start()),
            MenuItem(lambda i: tr(self.cfg, "pause") if not self.paused
                     else tr(self.cfg, "resume"),
                     toggle_pause, checked=lambda i: self.paused),
            MenuItem(lambda i: tr(self.cfg, "language"), toggle_lang),
            MenuItem(lambda i: tr(self.cfg, "theme"),
                     Menu(*make_theme_menu(),
                          MenuItem(lambda i: tr(self.cfg, "theme_custom"),
                                   custom_color))),
            MenuItem(lambda i: tr(self.cfg, "exit"), lambda i, it: self.quit()),
        )
        self.icon = pystray.Icon(APP_ID, self._icon_image(),
                                 tr(self.cfg, "app"), menu)
        self.icon.run_detached()

    def _timer_loop(self) -> None:
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

    def start_rest(self) -> None:
        if self.rest_active:
            return
        self.rest_active = True
        logging.info("break triggered after %ss watching", self.watched)
        try:
            show_break(self.cfg, self.break_sec)
        except Exception as e:
            logging.warning("break screen error: %s", e)
            speak(self.cfg, "speak_rest")
            time.sleep(self.break_sec)
            speak(self.cfg, "speak_done")
        finally:
            self.watched = 0
            self.rest_active = False
            logging.info("break finished, timer reset")

    def quit(self) -> None:
        logging.info("exit")
        self.cam.stop()
        if self.icon:
            try:
                self.icon.stop()
            except Exception:
                pass
        release_lock()
        os._exit(0)

    def run(self) -> None:
        self._timer_loop()


# ---------------- 自启项 ----------------
def autostart_path() -> str:
    if IS_MAC:
        return os.path.expanduser("~/Library/LaunchAgents/com.eyeguard.plist")
    return os.path.expanduser("~/.config/autostart/eyeguard.desktop")


def install_autostart() -> bool:
    py = sys.executable
    script = os.path.join(HERE, "eyeguard.py")
    try:
        if IS_MAC:
            os.makedirs(os.path.dirname(autostart_path()), exist_ok=True)
            plist = f"""<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0"><dict>
  <key>Label</key><string>com.eyeguard</string>
  <key>ProgramArguments</key>
  <array><string>{py}</string><string>{script}</string></array>
  <key>RunAtLoad</key><true/>
  <key>KeepAlive</key><false/>
  <key>StandardOutPath</key><string>{LOG_PATH}</string>
  <key>StandardErrorPath</key><string>{LOG_PATH}</string>
</dict></plist>
"""
            with open(autostart_path(), "w", encoding="utf-8") as f:
                f.write(plist)
            subprocess.run(["launchctl", "unload", autostart_path()],
                           capture_output=True)
            subprocess.run(["launchctl", "load", autostart_path()],
                           capture_output=True)
        else:
            os.makedirs(os.path.dirname(autostart_path()), exist_ok=True)
            entry = f"""[Desktop Entry]
Type=Application
Name=EyeGuard
Name[zh_CN]=护眼管家
Comment=Eye care break reminder
Exec={py} {script}
X-GNOME-Autostart-enabled=true
Terminal=false
"""
            with open(autostart_path(), "w", encoding="utf-8") as f:
                f.write(entry)
            os.chmod(autostart_path(), 0o644)
        logging.info("autostart installed")
        return True
    except Exception as e:
        logging.warning("install autostart failed: %s", e)
        return False


def uninstall_autostart() -> bool:
    try:
        if IS_MAC and os.path.exists(autostart_path()):
            subprocess.run(["launchctl", "unload", autostart_path()],
                           capture_output=True)
        if os.path.exists(autostart_path()):
            os.remove(autostart_path())
        return True
    except Exception as e:
        logging.warning("uninstall autostart failed: %s", e)
        return False


# ---------------- CLI ----------------
def status() -> None:
    cfg = load_config()
    print("platform      :", platform.system(), platform.release())
    print("python        :", sys.version.split()[0])
    print("config        :", CONFIG_PATH)
    print("config values :", json.dumps(cfg, ensure_ascii=False))
    print("autostart     :", "ON" if os.path.exists(autostart_path()) else "OFF",
          "->", autostart_path())
    print("browser       :", find_browser() or "(none, will use tk fallback)")
    print("rest.html     :", "OK" if os.path.exists(REST_HTML) else "MISSING")
    print("face model    :", "OK" if os.path.exists(MODEL_PATH) else "MISSING")
    voices = sorted(f for f in os.listdir(HERE) if f.startswith("voice_"))
    print("voice files   :", ", ".join(voices) or "(none)")
    running = False
    if os.path.exists(LOCK_PATH):
        try:
            with open(LOCK_PATH, encoding="utf-8") as f:
                pid = int(f.read().strip() or 0)
            if pid:
                os.kill(pid, 0)
                running = True
        except Exception:
            pass
    print("running       :", "YES" if running else "NO")


def selftest() -> int:
    print("== EyeGuard selftest ==", flush=True)
    status()
    try:
        import cv2
        print("opencv        :", cv2.__version__)
    except Exception as e:
        print("opencv        : MISSING (%s)" % e)
    try:
        import pystray  # noqa: F401
        print("pystray       : OK")
    except Exception as e:
        print("pystray       : MISSING (%s)" % e)
    cam = CameraMonitor()
    cam.start()
    time.sleep(2.5)
    print("camera        :", "OK" if cam.camera_ok else "unavailable (纯计时模式)")
    cam.stop()
    return 0


def main() -> int:
    args = sys.argv[1:]
    if "--status" in args:
        status()
        return 0
    if "--selftest" in args:
        return selftest()
    if "--install" in args:
        return 0 if install_autostart() else 1
    if "--uninstall" in args:
        return 0 if uninstall_autostart() else 1
    if "--rest" in args:
        cfg = load_config()
        print("playing break screen for %ss ..." % cfg["break_sec"])
        show_break(cfg, int(cfg["break_sec"]))
        return 0

    if not acquire_lock():
        print("EyeGuard 已在运行（单实例）。")
        return 0
    try:
        EyeGuard().run()
    except KeyboardInterrupt:
        release_lock()
    return 0


if __name__ == "__main__":
    sys.exit(main())
