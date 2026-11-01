# -*- coding: utf-8 -*-
"""
护眼管家 安装向导 / EyeGuard Setup
- 安装时选择语言（中文 / English）
- 写入 config.json 的语言设置
- 注册开机自启（当前用户，无需管理员）
用法：双击运行，或  python install.py
"""
import os
import sys
import json
import winreg

BASE = os.path.dirname(os.path.abspath(__file__))
CONFIG_PATH = os.path.join(BASE, "config.json")
RUN_KEY = r"Software\Microsoft\Windows\CurrentVersion\Run"
RUN_NAME = "EyeGuard"
MAIN_PY = os.path.join(BASE, "EyeGuard.pyw")

TEXT = {
    "zh": {
        "title": "护眼管家 安装向导",
        "pick": "请选择语言（输入 1 或 2）：\n  1) 中文\n  2) English\n> ",
        "checking": "正在检查文件...",
        "file_ok": "文件检查通过。",
        "file_missing": "缺少文件：{}  —— 请确认本压缩包已完整解压后再运行安装。",
        "write_cfg": "正在写入语言设置...",
        "reg": "正在注册开机自启...",
        "reg_ok": "开机自启已注册（下次开机自动运行，无窗口）。",
        "reg_fail": "开机自启注册失败：{}（程序仍可手动双击 EyeGuard.pyw 启动）",
        "done": "\n安装完成 ✔\n\n· 程序已按你选择的语言设置好。\n· 使用说明：使用说明（中文）.txt\n· 想立刻体验：双击 EyeGuard.pyw，然后右键托盘里的小绿点 → 立即休息。\n",
        "start_now": "现在就启动护眼管家吗？(y/N) > ",
        "started": "已启动，请查看右下角托盘区的小绿点。",
        "bye": "按回车键退出...",
    },
    "en": {
        "title": "EyeGuard Setup",
        "pick": "Select a language (enter 1 or 2):\n  1) 中文\n  2) English\n> ",
        "checking": "Checking files...",
        "file_ok": "All required files found.",
        "file_missing": "Missing file: {} -- please fully extract the archive before running setup.",
        "write_cfg": "Writing language setting...",
        "reg": "Registering auto-start at boot...",
        "reg_ok": "Auto-start registered (runs silently at your next boot).",
        "reg_fail": "Failed to register auto-start: {} (you can still launch EyeGuard.pyw manually)",
        "done": "\nInstallation complete ✔\n\n- The program is set to your chosen language.\n- User guide: README（English）.txt\n- To try it now: double-click EyeGuard.pyw, then right-click the green tray dot -> Take a break now.\n",
        "start_now": "Start EyeGuard now? (y/N) > ",
        "started": "Started - check the green dot in the system tray.",
        "bye": "Press Enter to exit...",
    },
}


def ask_lang():
    if "--lang" in sys.argv:
        v = sys.argv[sys.argv.index("--lang") + 1]
        return "en" if v.lower().startswith("e") else "zh"
    while True:
        raw = input(TEXT["zh"]["pick"]).strip()
        if raw == "1":
            return "zh"
        if raw == "2":
            return "en"


def main():
    lang = ask_lang()
    t = TEXT[lang]
    print("=" * 46)
    print(" " + t["title"])
    print("=" * 46)

    # 1. 文件检查
    print(t["checking"])
    required = [MAIN_PY, os.path.join(BASE, "rest.html"),
                os.path.join(BASE, "haarcascade_frontalface_default.xml")]
    for f in required:
        if not os.path.exists(f):
            print(t["file_missing"].format(os.path.basename(f)))
            input(t["bye"])
            return 1
    print(t["file_ok"])

    # 2. 写入语言
    print(t["write_cfg"])
    cfg = {"interval_min": 30, "break_sec": 20, "use_camera": True, "lang": lang}
    try:
        if os.path.exists(CONFIG_PATH):
            with open(CONFIG_PATH, "r", encoding="utf-8") as fp:
                cfg.update(json.load(fp))
        cfg["lang"] = lang
        with open(CONFIG_PATH, "w", encoding="utf-8") as fp:
            json.dump(cfg, fp, ensure_ascii=False, indent=2)
    except Exception as e:
        print("config error:", e)

    # 3. 注册开机自启
    print(t["reg"])
    try:
        pythonw = os.path.join(os.path.dirname(sys.executable), "pythonw.exe")
        if not os.path.exists(pythonw):
            pythonw = sys.executable
        cmd = f'"{pythonw}" "{MAIN_PY}"'
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, RUN_KEY, 0, winreg.KEY_SET_VALUE)
        winreg.SetValueEx(key, RUN_NAME, 0, winreg.REG_SZ, cmd)
        winreg.CloseKey(key)
        print(t["reg_ok"])
    except Exception as e:
        print(t["reg_fail"].format(e))

    print(t["done"])

    # 4. 可选立即启动
    if "--dry" not in sys.argv:
        try:
            ans = input(t["start_now"]).strip().lower()
            if ans in ("y", "yes", "是"):
                import subprocess
                pythonw = os.path.join(os.path.dirname(sys.executable), "pythonw.exe")
                subprocess.Popen([pythonw if os.path.exists(pythonw) else sys.executable, MAIN_PY],
                                 cwd=BASE)
                print(t["started"])
        except Exception:
            pass
    return 0


if __name__ == "__main__":
    code = main()
    if "--dry" in sys.argv:
        sys.exit(code)
    try:
        input(TEXT["zh"]["bye"])
    except Exception:
        pass
