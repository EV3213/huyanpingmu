# Windows 版（Windows build）

Windows 端成品，双击即用（Ready to run on Windows）。

## 文件（Files）

| 文件（File） | 作用（Purpose） |
|---|---|
| EyeGuard.pyw | 主程序（main program，pythonw 静默运行） |
| install.py | 安装脚本（installer：选语言 + 写开机自启） |
| 安装到本机.bat | 双击安装（double-click installer） |
| rest.html | 休息屏（break screen，kiosk 全屏） |
| config.json | 配置（configuration） |
| haarcascade_frontalface_default.xml | 人脸模型（face model） |
| voice_*.mp3 | 预生成语音（neural voice clips） |
| 使用说明（中文）.txt / README（English）.txt | 详细说明（manuals） |

## 用（Use）

1. 把 `../assets/` 里的 `rest-aerial.mp4`、`rest-plant.mp4`、`rest-bg.png` 一起放到本文件夹（休息屏要用）。
   （Copy the three media files from `../assets/` into this folder.）
2. 双击「安装到本机.bat」，选 1（中文）或 2（English）。
   （Run the installer bat and choose 1 or 2.）
3. 之后开机自启；托盘绿色圆点右键可暂停 / 立即休息 / 切语言 / 退出。
   （Auto-starts at boot; right-click the green tray dot for options.）

## 依赖（Requirements）

- Windows 10 / 11
- WorkBuddy 自带 Python 运行时（或自行安装 Python 3.9+ 与 opencv-python、pystray、pillow）
- Chrome 或 Edge（kiosk 全屏播放休息屏）
