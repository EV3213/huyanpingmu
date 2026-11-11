# Windows 版（Windows build）

Windows 端成品，双击即用（Ready to run on Windows）。

## 文件（Files）

| 文件（File） | 作用（Purpose） |
|---|---|
| EyeGuard.pyw | 主程序（main program，pythonw 静默运行；默认 = 学习端） |
| parent_ui.ps1 | 家长端设置窗口（parent settings window） |
| ask.ps1 | 密码 / 输入弹窗（password & prompt dialog） |
| 安装到本机.bat | 双击安装（double-click installer） |
| 家长端.bat | 打开家长端（launch parent app） |
| install.py | 安装脚本（installer：选语言 + 写开机自启） |
| rest.html | 休息屏（break screen，kiosk 全屏） |
| config.json | 配置（configuration） |
| state.json | 学习端上报的今日进度（today stats，学习端运行时生成） |
| haarcascade_frontalface_default.xml | 人脸模型（face model） |
| voice_*.mp3 | 预生成语音（neural voice clips） |
| 使用说明（中文）.txt / README（English）.txt | 详细说明（manuals） |

## 用（Use）

1. 把 `../assets/` 里的 `rest-aerial.mp4`、`rest-plant.mp4`、`rest-bg.png` 一起放到本文件夹（休息屏要用）。
   （Copy the three media files from `../assets/` into this folder.）
2. 双击「安装到本机.bat」，选 1（中文）或 2（English）。
   （Run the installer bat and choose 1 or 2.）
3. 之后开机自启的是**学习端**：托盘绿色圆点右键只有今日进度、立即休息、打开家长端、退出（要密码）。
   （Auto-starts at boot as the study app; the tray menu is read-only except "take a break" and "open parent app".）
4. 家长设置（Parent settings）：双击「家长端.bat」，第一次要求设置家长密码，之后在这里改一切。

## 场景识别（Scene detection）

程序每秒读一次前台窗口，按正在用的东西决定时长：

| 场景（Scene） | 规则（Rule） |
|---|---|
| 普通软件（Normal app） | 普通时长，默认 30 分钟（托盘「普通时长」可改） |
| 工作网页（Work page） | 同普通时长 |
| 娱乐网页（Entertainment） | 25 分钟（托盘「娱乐时长」可改，15–45） |
| 学习软件（Study） | 到点不打断，退出学习软件后立刻播休息屏；最长延后 30 分钟可调 |

- 学习类默认认这些进程 / 标题：anki、学习通、超星、中国大学 MOOC、Coursera、可汗学院、网易公开课、腾讯课堂、智慧树、学堂在线；可在 config.json 的 study_apps 里加自己的。
- 娱乐类按标题认：哔哩哔哩 / B 站 / YouTube / 抖音 / 爱奇艺 / 优酷 / 腾讯视频 / Netflix / 虎牙 / 斗鱼 / 网易云音乐等。
- 想关掉整个功能：托盘菜单里取消勾选「识别全屏场景」，或把 config.json 的 smart_scene 设为 false。
- 只读窗口标题和进程名，不读页面内容、不联网。

## 家长端与学习端（Parent & study app）

1.2 起 Windows 端分成两个入口，共用一份 config.json：

- **学习端（study app）**：开机自启的就是它。托盘菜单没有任何可改的项——没有暂停、没有时长，退出要输家长密码。孩子能看到今天专注了多久、休息了几次。
- **家长端（parent app）**：双击「家长端.bat」（或托盘里的「打开家长端…」），输密码进入设置窗口。学习计划、学习软件清单、主题色、密码都在这里改。
- 家长点「保存」后，学习端约 1 秒内自动生效，不用重启。
- 密码忘了：关掉学习端，删掉 config.json 里的 admin_pin_sha256 与 admin_salt（或整份 config.json）。

密码只存盐 + SHA-256 摘要，不联网、不上传。它能挡住随手改设置和退出程序，但挡不住会编辑配置文件或直接结束进程的人。

## 依赖（Requirements）

- Windows 10 / 11
- WorkBuddy 自带 Python 运行时（或自行安装 Python 3.9+ 与 opencv-python、pystray、pillow）
- Chrome 或 Edge（kiosk 全屏播放休息屏）
