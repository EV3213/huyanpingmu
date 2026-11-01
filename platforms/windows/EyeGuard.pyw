# -*- coding: utf-8 -*-
"""
护眼管家 EyeGuard（桌面版）
- 开机自启、无窗口静默运行（托盘图标可暂停/退出）
- 摄像头本地人脸检测（不联网、不保存画面），持续注视达阈值即强制休息
- 休息屏：Chrome Kiosk 全屏（覆盖任务栏）+ Aerial 风格实拍绿植视频 + 语音播报"休息一下"
"""
import os
import re
import sys
import json
import time
import hashlib
import secrets
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
        "interval": "普通时长",
        "entertainment": "娱乐时长（视频网页）",
        "smart": "识别全屏场景",
        "study_wait": "学习时最多延后",
        "no_limit": "不限制（等退出）",
        "pin_set": "设置访问密码…",
        "pin_change": "修改 / 取消访问密码…",
        "pin_title": "访问密码",
        "pin_prompt": "请输入访问密码：",
        "pin_new": "设置一个新密码（至少 4 位，留空 = 取消密码）：",
        "pin_repeat": "再输入一次：",
        "pin_wrong": "密码不对",
        "pin_too_short": "密码至少 4 位",
        "pin_mismatch": "两次输入不一致",
        "pin_saved": "密码已设置。之后改时间、暂停、退出都要先输密码。",
        "pin_cleared": "密码已取消",
        "minutes": " 分钟",
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
        "interval": "Normal interval",
        "entertainment": "Entertainment interval (video)",
        "smart": "Detect fullscreen app",
        "study_wait": "Max delay while studying",
        "no_limit": "No limit (wait for exit)",
        "pin_set": "Set access password…",
        "pin_change": "Change / remove password…",
        "pin_title": "Access password",
        "pin_prompt": "Enter the access password:",
        "pin_new": "New password (4+ chars, empty = remove):",
        "pin_repeat": "Repeat:",
        "pin_wrong": "Wrong password",
        "pin_too_short": "At least 4 characters",
        "pin_mismatch": "The two entries do not match",
        "pin_saved": "Password saved. Changing interval, pausing and exiting now ask for it.",
        "pin_cleared": "Password removed",
        "minutes": " min",
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
APP_VERSION = "1.1"

# ---------- 前台窗口 / 全屏场景识别 ----------
# 学习类程序（按进程名匹配，配置里 study_apps 可覆盖）
SMART_DEFAULT_STUDY_APPS = [
    "anki.exe", "xuexitong.exe", "chaoxing.exe", "mooc.exe", "coursera.exe",
    "duolingo.exe", "tencentclass.exe", "khanacademy.exe", "notability.exe",
    "chaoxing", "xuexitong",
]
# 浏览器里按标题判断：先学习，再娱乐，其余一律按工作（用普通时长）
SMART_STUDY_HINTS = [
    "学习通", "超星", "中国大学mooc", "mooc", "coursera", "可汗学院", "khan academy",
    "网易公开课", "腾讯课堂", "智慧树", "学堂在线", "anki", "备考",
    "course", "lecture", "课件", "网课",
]
SMART_ENTERTAINMENT_HINTS = [
    "哔哩哔哩", "bilibili", "b站", "youtube", "抖音", "douyin", "tiktok",
    "爱奇艺", "iqiyi", "优酷", "youku", "腾讯视频", "v.qq.com", "芒果", "mgtv",
    "netflix", "twitch", "斗鱼", "douyu", "虎牙", "huya", "西瓜视频",
    "网易云音乐", "music.163.com", "qq音乐", "y.qq.com", "咪咕", "快手", "kuaishou",
    "微博", "weibo", "小红书", "xiaohongshu", "搜狐视频", "acfun", "niconico",
]
SMART_WORK_HINTS = [
    "github", "gitlab", "gitee", "jira", "confluence", "notion", "飞书", "feishu",
    "lark", "腾讯文档", "docs.qq.com", "石墨", "shimo", "语雀", "yuque",
    "stack overflow", "stackoverflow", "掘金", "juejin", "csdn", "博客园", "cnblogs",
    "developer.mozilla", "mdn", "docs.google", "learn.microsoft", "docs.python",
    "w3school", "菜鸟教程", "runoob", "知网", "cnki", "arxiv", "ieee", "springer",
    "outlook", "gmail", "邮箱", "mail", "excel", "word", "powerpoint", "wps",
]
BROWSER_EXES = {
    "chrome.exe", "msedge.exe", "firefox.exe", "brave.exe", "opera.exe",
    "vivaldi.exe", "360se.exe", "360chrome.exe", "qqbrowser.exe", "sogouexplorer.exe",
}


class _RECT(ctypes.Structure):
    _fields_ = [("left", ctypes.c_long), ("top", ctypes.c_long),
                ("right", ctypes.c_long), ("bottom", ctypes.c_long)]


class _MONITORINFO(ctypes.Structure):
    _fields_ = [("cbSize", ctypes.c_ulong), ("rcMonitor", _RECT),
                ("rcWork", _RECT), ("dwFlags", ctypes.c_ulong)]


def _window_process_name(hwnd):
    """取窗口所属进程的可执行文件名"""
    try:
        pid = ctypes.c_ulong()
        ctypes.windll.user32.GetWindowThreadProcessId(hwnd, ctypes.byref(pid))
        if not pid.value:
            return ""
        handle = ctypes.windll.kernel32.OpenProcess(0x1000, False, pid.value)
        if not handle:
            return ""
        try:
            buf = ctypes.create_unicode_buffer(1024)
            size = ctypes.c_ulong(1024)
            if ctypes.windll.kernel32.QueryFullProcessImageNameW(
                    handle, 0, buf, ctypes.byref(size)):
                return os.path.basename(buf.value).lower()
        finally:
            ctypes.windll.kernel32.CloseHandle(handle)
    except Exception:
        pass
    return ""


def get_foreground_info():
    """当前前台窗口：{exe, title, fullscreen}；失败返回 None"""
    try:
        u = ctypes.windll.user32
        hwnd = u.GetForegroundWindow()
        if not hwnd:
            return None
        n = u.GetWindowTextLengthW(hwnd)
        buf = ctypes.create_unicode_buffer(n + 1)
        u.GetWindowTextW(hwnd, buf, n + 1)
        rect = _RECT()
        u.GetWindowRect(hwnd, ctypes.byref(rect))
        full = False
        mi = _MONITORINFO()
        mi.cbSize = ctypes.sizeof(_MONITORINFO)
        mon = u.MonitorFromWindow(hwnd, 2)  # MONITOR_DEFAULTTONEAREST
        if mon and u.GetMonitorInfoW(mon, ctypes.byref(mi)):
            mw = mi.rcMonitor.right - mi.rcMonitor.left
            mh = mi.rcMonitor.bottom - mi.rcMonitor.top
            ww = rect.right - rect.left
            wh = rect.bottom - rect.top
            full = ww >= mw - 4 and wh >= mh - 4
        return {"exe": _window_process_name(hwnd),
                "title": buf.value or "",
                "fullscreen": full}
    except Exception:
        return None


def _hit(text, keywords):
    """关键词命中：中文按包含匹配，英文要求整词边界
    （否则 huya 会命中 huyanpingmu 这类无关文字）"""
    if not text:
        return False
    for kw in keywords:
        k = str(kw).lower().strip()
        if not k:
            continue
        try:
            k.encode("ascii")
            if re.search(r"(?<![a-z0-9])" + re.escape(k) + r"(?![a-z0-9])", text):
                return True
        except UnicodeEncodeError:
            if k in text:
                return True
    return False


def classify_scene(info, cfg):
    """归类：study（学习）/ entertainment（娱乐）/ work（工作）/ normal（普通）"""
    if not info:
        return "normal"
    exe = (info.get("exe") or "").lower()
    title = (info.get("title") or "").lower()
    study_apps = cfg.get("study_apps")
    if not isinstance(study_apps, list) or not study_apps:
        study_apps = SMART_DEFAULT_STUDY_APPS
    if _hit(exe, study_apps) or _hit(title, study_apps):
        return "study"
    is_browser = exe in BROWSER_EXES or any(b in exe for b in ("chrome", "edge", "firefox"))
    if is_browser:
        if _hit(title, SMART_STUDY_HINTS):
            return "study"
        if _hit(title, SMART_ENTERTAINMENT_HINTS):
            return "entertainment"
        # 浏览器里的其它内容（含各类工作站点）一律按普通时长
        return "work"
    return "normal"


def _pin_hash(pin, salt):
    """密码只存摘要，配置文件里看不到明文"""
    return hashlib.sha256(("%s|%s" % (salt, pin)).encode("utf-8")).hexdigest()


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
           "lang": "zh", "theme_color": DEFAULT_THEME,
           "smart_scene": True, "entertainment_min": 25,
           "study_max_wait_min": 30,
           "admin_salt": "", "admin_pin_sha256": "",
           "study_apps": list(SMART_DEFAULT_STUDY_APPS)}
    try:
        with open(CONFIG_PATH, "r", encoding="utf-8") as f:
            cfg.update(json.load(f))
    except Exception:
        pass
    if cfg.get("lang") not in I18N:
        cfg["lang"] = "zh"
    cfg["theme_color"] = normalize_theme(cfg.get("theme_color"))
    for key, default in (("interval_min", 30), ("entertainment_min", 25),
                         ("break_sec", 20)):
        try:
            val = int(cfg.get(key, default))
            cfg[key] = val if val > 0 else default
        except (TypeError, ValueError):
            cfg[key] = default
    try:
        wait = int(cfg.get("study_max_wait_min", 30))
    except (TypeError, ValueError):
        wait = 30
    cfg["study_max_wait_min"] = wait if wait >= 0 else 30
    if not isinstance(cfg.get("admin_salt"), str):
        cfg["admin_salt"] = ""
    if not isinstance(cfg.get("admin_pin_sha256"), str):
        cfg["admin_pin_sha256"] = ""
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
        self.scene = {"exe": "", "title": "", "fullscreen": False}
        self.scene_kind = "normal"     # study / entertainment / work / normal
        self.pending = False           # 到点了但在等学习软件退出
        self.pending_since = 0.0
        self.away_since = 0.0
        self._unlocked_at = 0.0        # 输对密码后的免密时间窗口
        self.cam = CameraMonitor()
        if self.cfg.get("use_camera", True):
            self.cam.start()
        self._build_tray()

    # ---------- 计时线程 ----------
    def required_seconds(self):
        """当前场景要求的注视时长：娱乐 25 分钟，其余用普通设置"""
        if self.cfg.get("smart_scene", True) and self.scene_kind == "entertainment":
            return max(1, int(self.cfg.get("entertainment_min", 25))) * 60
        return max(1, int(self.cfg.get("interval_min", 30))) * 60

    def pending_limit(self):
        """学习中最多再延后多久；0 表示不限制（一直等到学习软件退出）"""
        try:
            mins = int(self.cfg.get("study_max_wait_min", 30))
        except (TypeError, ValueError):
            mins = 30
        return mins * 60 if mins > 0 else 0

    def _refresh_scene(self):
        """每秒采样一次前台窗口，识别正在全屏的应用/网页类型"""
        if not self.cfg.get("smart_scene", True):
            self.scene_kind = "normal"
            return
        info = get_foreground_info()
        if not info:
            self.scene_kind = "normal"
            return
        kind = classify_scene(info, self.cfg)
        changed = kind != self.scene_kind
        self.scene = info
        self.scene_kind = kind
        if changed:
            logging.info("scene -> %s (%s | %s | fullscreen=%s)", kind,
                         info.get("exe"), (info.get("title") or "")[:60],
                         info.get("fullscreen"))
            self._update_tooltip()

    def _update_tooltip(self):
        label = {"study": "学习中", "entertainment": "娱乐中",
                 "work": "工作中", "normal": "普通"}.get(self.scene_kind, "")
        if self.cfg.get("lang", "zh") == "en":
            label = {"study": "studying", "entertainment": "watching",
                     "work": "working", "normal": "normal"}.get(self.scene_kind, "")
        if self.pending:
            label = "学习中 · 待休息" if self.cfg.get("lang", "zh") == "zh" \
                else "studying · break pending"
        try:
            self.icon.title = "%s · %s %d%s · v%s" % (
                self.tr("tray_title"), label, self.required_seconds() // 60,
                self.tr("minutes"), APP_VERSION)
        except Exception:
            pass

    def _timer_loop(self):
        while True:
            time.sleep(1)
            try:
                self._refresh_scene()
            except Exception as e:
                logging.debug("scene refresh failed: %s", e)
            try:
                self._tick(time.time())
            except Exception as e:
                logging.warning("tick failed: %s", e)

    def _tick(self, now):
        """每秒一次的心跳：累加注视时长，按场景决定是否进入休息"""
        if self.paused or self.rest_active:
            return
        watching = True
        if self.cam.camera_ok:
            away = (not self.cam.face_seen) and \
                   (now - self.cam.face_lost_at > 10)
            watching = not away
        if not watching:
            if self.pending:
                # 学习途中起身接杯水不该丢掉待播的休息；离开超过 3 分钟
                # 说明已经真的歇过了，才把待播状态清掉
                if not self.away_since:
                    self.away_since = now
                elif now - self.away_since > 180:
                    logging.info("away >3min while break was pending, dropped")
                    self.pending = False
                    self.watched = 0
                    self.away_since = 0.0
            else:
                self.watched = 0
                self.away_since = 0.0
            return
        self.away_since = 0.0
        self.watched += 1
        # 已经到点、正在学习：等学习软件退出，一退出就立刻播放休息屏
        if self.pending:
            waited = now - self.pending_since
            limit = self.pending_limit()
            if self.scene_kind != "study":
                logging.info("study app left, playing deferred break "
                             "(waited %ss, watched %ss)",
                             int(waited), self.watched)
                self.pending = False
                self.start_rest()
            elif limit and waited >= limit:
                logging.info("studied %ss past threshold, forcing break",
                             int(waited))
                self.pending = False
                self.start_rest()
            return
        if self.watched >= self.required_seconds():
            if self.scene_kind == "study":
                self.pending = True
                self.pending_since = now
                logging.info("time is up but studying (%s | %s), deferred",
                             self.scene.get("exe"),
                             (self.scene.get("title") or "")[:50])
                self._update_tooltip()
            else:
                self.start_rest()

    # ---------- 多语言 ----------
    def tr(self, key):
        return I18N[self.cfg.get("lang", "zh")][key]

    # ---------- 访问密码 ----------
    def pin_enabled(self):
        return bool(self.cfg.get("admin_pin_sha256"))

    def _pin_ok(self, pin):
        if not self.pin_enabled():
            return True
        salt = self.cfg.get("admin_salt") or ""
        return _pin_hash(pin, salt) == self.cfg.get("admin_pin_sha256")

    def _ask_text(self, prompt, show="*"):
        """弹一个输入框；取消返回 None"""
        try:
            import tkinter as tk
            from tkinter import simpledialog
            root = tk.Tk()
            root.withdraw()
            root.attributes("-topmost", True)
            value = simpledialog.askstring(self.tr("pin_title"), prompt,
                                           show=show, parent=root)
            root.destroy()
            return value
        except Exception as e:
            logging.warning("ask dialog failed: %s", e)
            return None

    def _notify(self, text):
        try:
            import tkinter as tk
            from tkinter import messagebox
            root = tk.Tk()
            root.withdraw()
            root.attributes("-topmost", True)
            messagebox.showinfo(self.tr("tray_title"), text, parent=root)
            root.destroy()
        except Exception as e:
            logging.warning("notify failed: %s", e)

    def require_pin(self, force=False):
        """需要密码的操作先过这里；没设密码直接放行，输对后 3 分钟内免重复输入"""
        if not self.pin_enabled():
            return True
        now = time.time()
        if not force and now - self._unlocked_at < 180:
            return True
        pin = self._ask_text(self.tr("pin_prompt"))
        if pin is None:
            return False
        if self._pin_ok(pin):
            self._unlocked_at = now
            logging.info("access granted by password")
            return True
        logging.warning("wrong password entered")
        self._notify(self.tr("pin_wrong"))
        return False

    def guard(self, fn):
        """把需要密码的动作包一层"""
        def wrapped(icon=None, item=None):
            if not self.require_pin():
                return None
            return fn(icon, item)
        return wrapped

    def edit_pin(self, icon=None, item=None):
        if self.pin_enabled() and not self.require_pin(force=True):
            return
        first = self._ask_text(self.tr("pin_new"))
        if first is None:
            return
        if first == "":
            self.cfg["admin_salt"] = ""
            self.cfg["admin_pin_sha256"] = ""
            save_config(self.cfg)
            logging.info("password removed")
            self._notify(self.tr("pin_cleared"))
            self._refresh_tray()
            return
        if len(first) < 4:
            self._notify(self.tr("pin_too_short"))
            return
        again = self._ask_text(self.tr("pin_repeat"))
        if again != first:
            self._notify(self.tr("pin_mismatch"))
            return
        salt = secrets.token_hex(8)
        self.cfg["admin_salt"] = salt
        self.cfg["admin_pin_sha256"] = _pin_hash(first, salt)
        save_config(self.cfg)
        logging.info("password set")
        self._notify(self.tr("pin_saved"))
        self._refresh_tray()

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
                def make_setter(_h):
                    def set_color(icon=None, item=None):
                        self.cfg["theme_color"] = _h
                        save_config(self.cfg)
                        logging.info("theme color -> %s", _h)
                        self._refresh_tray()
                    return set_color
                items.append(TrayItem(
                    lambda item, _h=hexv, _z=zh_name, _e=en_name:
                        ("%s %s" % ("●" if self.cfg.get("theme_color") == _h else "○",
                                    _z if self.cfg.get("lang", "zh") == "zh" else _e)),
                    action=make_setter(hexv)))
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

        def make_interval_menu(key, options):
            items = []
            for mins in options:
                def make_setter(_m):
                    def set_minutes(icon=None, item=None):
                        self.cfg[key] = _m
                        save_config(self.cfg)
                        logging.info("%s -> %s min", key, _m)
                        self._update_tooltip()
                        self._refresh_tray()
                    return set_minutes
                items.append(TrayItem(
                    lambda item, _m=mins: "%d%s" % (_m, self.tr("minutes")),
                    action=self.guard(make_setter(mins)),
                    checked=lambda item, _m=mins, _k=key:
                        int(self.cfg.get(_k, 0)) == _m,
                    radio=True))
            return TrayMenu(*items)

        def toggle_smart(icon=None, item=None):
            self.cfg["smart_scene"] = not self.cfg.get("smart_scene", True)
            save_config(self.cfg)
            logging.info("smart_scene -> %s", self.cfg["smart_scene"])
            self._refresh_tray()

        def make_wait_menu():
            """学习场景下最多延后多久再强制休息；0 = 一直等到学习软件退出"""
            items = []
            for mins in (15, 30, 45, 60, 0):
                def make_setter(_m):
                    def set_wait(icon=None, item=None):
                        self.cfg["study_max_wait_min"] = _m
                        save_config(self.cfg)
                        logging.info("study_max_wait_min -> %s", _m)
                    return set_wait
                items.append(TrayItem(
                    lambda item, _m=mins: self.tr("no_limit") if _m == 0
                    else "%d%s" % (_m, self.tr("minutes")),
                    action=self.guard(make_setter(mins)),
                    checked=lambda item, _m=mins:
                        int(self.cfg.get("study_max_wait_min", 30)) == _m,
                    radio=True))
            return TrayMenu(*items)

        menu = TrayMenu(
            TrayItem(lambda item: self.tr("rest_now"), action=lambda i, it: self.start_rest()),
            TrayItem(lambda item: self.tr("pause"), action=self.guard(toggle_pause),
                     checked=lambda item: self.paused),
            TrayMenu.SEPARATOR,
            TrayItem(lambda item: self.tr("interval"),
                     TrayMenu(*make_interval_menu("interval_min",
                                                  [15, 20, 25, 30, 45, 60]).items)),
            TrayItem(lambda item: self.tr("entertainment"),
                     TrayMenu(*make_interval_menu("entertainment_min",
                                                  [15, 20, 25, 30, 45]).items)),
            TrayItem(lambda item: self.tr("smart"), action=self.guard(toggle_smart),
                     checked=lambda item: bool(self.cfg.get("smart_scene", True))),
            TrayItem(lambda item: self.tr("study_wait"),
                     TrayMenu(*make_wait_menu().items)),
            TrayMenu.SEPARATOR,
            TrayItem(lambda item: self.tr("language"), action=self.toggle_lang),
            TrayItem(lambda item: self.tr("theme"),
                     TrayMenu(*make_theme_menu(),
                              TrayItem(lambda item: self.tr("theme_custom"),
                                       action=custom_color))),
            TrayItem(lambda item: self.tr("pin_change") if self.pin_enabled()
                     else self.tr("pin_set"), action=self.edit_pin),
            TrayItem(lambda item: self.tr("exit"), action=self.guard(
                lambda i, it: self.quit(i))),
            TrayMenu.SEPARATOR,
            TrayItem(lambda item: "%s v%s" % (self.tr("tray_title"), APP_VERSION),
                     action=None),
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
        samples = [
            ("chrome.exe", "哔哩哔哩 (゜-゜)つロ 干杯~ - Google Chrome", True),
            ("msedge.exe", "中国大学MOOC(慕课)_国家精品课程在线学习平台 - Microsoft Edge", True),
            ("msedge.exe", "GitHub - EV3213/huyanpingmu - Microsoft Edge", True),
            ("anki.exe", "Anki", True),
            ("notepad.exe", "无标题 - 记事本", False),
        ]
        for exe, title, full in samples:
            print("scene %-14s %-44s -> %s" % (
                exe, title[:42],
                classify_scene({"exe": exe, "title": title,
                                "fullscreen": full}, g.cfg)), flush=True)
        g.quit()
    elif "--probe" in sys.argv:
        # 实时打印前台窗口与判定结果，用于核对识别是否准确
        cfg = load_config()
        for i in range(20):
            info = get_foreground_info()
            print("%2ds %s -> %s" % (i, info, classify_scene(info, cfg)), flush=True)
            time.sleep(1)
    else:
        EyeGuard().run()
