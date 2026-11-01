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

## 访问密码（Parental lock）

不想让孩子自己把时间改长或把程序退掉，就设一个密码：

1. 托盘右键 →「设置访问密码…」→ 输两遍，至少 4 位。
2. 之后「普通时长 / 娱乐时长 / 识别全屏场景 / 学习时最多延后 / 暂停监控 / 退出」都要先输密码；输对一次 3 分钟内免重复。
3. 「立即休息 / 语言 / 主题色」不锁，方便日常用。
4. 改密码或取消：同一项菜单，先输当前密码，新密码留空即取消。
5. 密码忘了：关掉程序，删掉 config.json 里的 admin_pin_sha256 与 admin_salt（或整份 config.json）。

密码只存盐 + SHA-256 摘要，不联网、不上传。它能挡住随手改设置，但挡不住会编辑配置文件或直接结束进程的人。

## 依赖（Requirements）

- Windows 10 / 11
- WorkBuddy 自带 Python 运行时（或自行安装 Python 3.9+ 与 opencv-python、pystray、pillow）
- Chrome 或 Edge（kiosk 全屏播放休息屏）
