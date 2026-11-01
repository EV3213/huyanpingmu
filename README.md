# 护眼管家（EyeGuard）

**一句话：一个真的「管得住」的多平台护眼提醒工具。**
（In one line: a cross-platform eye-care reminder that actually holds you to it.）

官网（Official site）：**https://eyeguard-app.app.workbuddy.host** —— 支持中英切换与主题色实时预览。
（The official site supports language switching and a live theme-colour preview.）

开机静默自启，用摄像头本地判断你是否在看屏幕；连续注视满 30 分钟，强制弹出全屏「Aerial 风格」绿植实拍休息屏，并用人声提醒你休息。
（Starts silently at boot, detects whether you are looking at the screen via webcam; after 30 minutes of continuous viewing it forces a full-screen Aerial-style nature break screen with a spoken reminder.）

---

## 简介（Introduction）

大多数护眼软件活不过三天，原因很简单：它们弹出来的东西太好关了。一条右上角的小通知、一次可以随手点掉的弹窗，你眼睛都不用离开代码，手指就已经把它关掉了。护眼管家想解决的就是这个「知道了但做不到」的问题。

（Most eye-care apps do not survive three days, for one simple reason: what they show you is too easy to dismiss. A tiny notification in the corner, a popup you can close without moving your eyes. EyeGuard targets exactly that gap between knowing and doing.）

它的做法是把「提醒」变成「接管」。程序先用摄像头在本地做一次人脸检测，确认你确实坐在这块屏幕前，才开始计时；你起身倒水、转头接电话，计时会自动暂停，回来再接着算。连续注视累计满 30 分钟，整块屏幕被一段实拍绿植或航拍画面接管，倒计时从 20 秒开始，同时一句自然的神经网络语音响起来——不是系统那种一个字一个字往外蹦的机械朗读。这段时间里你没法一边「休息」一边刷消息，因为屏幕不在你手上。

（EyeGuard turns a reminder into a takeover. A local face detection pass first confirms you are really sitting at this screen, and only then does the clock start. Stand up for water, turn away for a call, and the timer pauses itself, resuming when you are back. After 30 minutes of accumulated viewing, the whole display is taken over by real footage of plants or an aerial landscape, a 20-second countdown begins, and a natural neural-network voice speaks up — not the word-by-word robotic reading of a system voice. During those seconds you cannot "rest" while scrolling, because the screen is not yours.）

整个程序只做了三件不妥协的事：

- **不外传（Nothing leaves the machine）** —— 摄像头画面全部在本机内存里处理，不联网、不落盘、不上传，代码可查。
- **不打扰（Silent until it matters）** —— 没有窗口、没有任务栏图标，平时只在托盘区留一个绿色小圆点；不想被管的时候，右键就能暂停监控。
- **不将就（Looks like something you keep）** —— 休息屏是真拍的绿植和航拍素材，语音是预生成的神经语音，十套主题色随意换，连托盘图标的颜色都跟着变。

（Three non-negotiables: frames never leave the machine; it stays invisible until it actually matters; and it looks good enough that you will not uninstall it.）

**适合谁（Who it is for）**：每天在屏幕前坐八小时以上的开发者、设计师、写作者、学生，以及那些装过三四个护眼插件、最后都被自己关掉的人。也适合装在家人的电脑上——它不啰嗦，到点才说话。

（For anyone who spends eight hours a day in front of a screen — developers, designers, writers, students — and for everyone who has installed three or four eye-care extensions and dismissed them all. It also works well on a family member's machine: it says nothing until it is time.）

**现在支持（What it runs on）**：Windows、Linux、macOS、Android、iOS、iPadOS 六个平台，同一套色板、同一套语音、同一套交互逻辑。
（Six platforms — Windows, Linux, macOS, Android, iOS, iPadOS — sharing one palette, one voice set, one interaction model.）

---

## 各平台版本（Platforms）

| 平台（Platform） | 目录（Folder） | 技术（Stack） | 状态（Status） |
|---|---|---|---|
| Windows | platforms/windows | Python + Chrome kiosk | 已发布（released） |
| Linux | platforms/linux | Python + 浏览器 kiosk / Tk | 可直接安装（installable） |
| macOS | platforms/macos | Python + LaunchAgent | 可直接安装（installable） |
| Android | platforms/android | Kotlin + CameraX + ML Kit | 需 Android Studio 构建 |
| iOS | platforms/ios | SwiftUI + Vision | 需 Xcode 构建 |
| iPadOS | platforms/ipados | SwiftUI + Vision（大屏适配） | 需 Xcode 构建 |
| 共享素材 | platforms/assets | 视频 / 海报图 | — |

每端都有独立 README，含安装/构建步骤和平台限制（Each platform ships its own README）.

**Android 手机直接装（Install on Android right away）**：到 [Releases 页面](https://github.com/EV3213/huyanpingmu/releases/latest) 下载 **EyeGuard-1.0.apk**（41 MB，正式签名 v2，最低 Android 8.0），传到手机点开即可安装，不需要 Android Studio、不需要 Google 服务。首次安装需在系统里允许「安装未知应用」。仓库里也留了一份 [apk/护眼管家-1.0.apk](platforms/android/apk/护眼管家-1.0.apk) 作为备份。

## 功能（Features）

- 摄像头监测（Webcam monitoring）：本地人脸检测，离开屏幕即暂停计时，回来继续；画面不外传、不保存。
- 场景识别（Smart scene detection）：识别当前全屏在用什么程序 / 网页，学习类自动把休息推到你退出之后，娱乐视频网页提前 5 分钟提醒。见下节。
- 强制休息屏（Forced break screen）：全屏播放实拍绿植 / 航拍视频，20 秒倒计时，Aerial 屏保风格。
- 自然语音（Natural voice）：预生成神经网络语音，不是系统机械朗读音；离线播放，无需联网。
- 主题色自定义（Theme colour）：10 套预设配色 + 自由取色，托盘 / 设置页 / 休息屏全部跟随；桌面端图标颜色也会跟着变。
- 双语支持（Bilingual）：中英文界面与语音一键切换，选择会被记住。
- 静默运行（Runs silently）：无窗口、无任务栏图标，只在托盘区显示一个绿色圆点。
- 开机自启（Auto-start）：写入注册表自启项，重启后仍然生效。

## 场景识别（Smart scene detection）

程序每秒读一次前台窗口（Windows 端已实现），按「你在干什么」决定什么时候该休息。

（Every second the Windows build reads the foreground window and decides when to intervene.）

| 场景（Scene） | 判定依据（How it is detected） | 计时规则（Rule） |
|---|---|---|
| 普通软件（Normal app） | 其它任何程序 | 按普通时长，默认 30 分钟，可在托盘自定义 |
| 工作网页（Work page） | Chrome / Edge 等浏览器里除下面两类之外的页面 | 同普通时长 |
| 娱乐网页（Entertainment） | 标题命中哔哩哔哩、B 站、YouTube、抖音、爱奇艺、优酷、腾讯视频、Netflix、虎牙、斗鱼、网易云音乐等 | 25 分钟（可在托盘改成 15–45） |
| 学习软件（Study） | 进程或标题命中 Anki、学习通、超星、中国大学 MOOC、Coursera、可汗学院、网易公开课、腾讯课堂、智慧树、学堂在线等 | 到点先不打断，**等你退出学习软件后立刻播放休息屏** |

几个细节（Details）：

- 学习场景的等待有上限（默认 30 分钟），到点还没退出就会强制休息一次——否则连续学一整天等于没有休息。可在托盘「学习时最多延后」里改成 15 / 30 / 45 / 60 分钟，或选「不限制（等退出）」。
- 学习途中起身接水不算「退出」：只要 3 分钟内回来，休息屏仍然待播；离开超过 3 分钟则视为已经歇过，重新计时。
- 浏览器靠标签页标题判断，所以标题里没写站点名的页面会被当成工作网页（用普通时长）。想加自己的站点，改 EyeGuard.pyw 顶部的关键词表，或直接改托盘开关关掉这个功能。
- 判定不依赖网络，也不读取页面内容，只读窗口标题和进程名。（No network access; only the window title and process name are read.）
- 目前只有 Windows 端做了场景识别；Linux / macOS 用各自的窗口查询接口（xdotool / AppleScript），Android 需要无障碍服务，iOS 根本无法读取别的 App，这三端暂时只有固定时长。

## 主题色（Theme colour）

所有平台共享同一套色板（All platforms share the same palette）：

| 名称（Name） | 色值（Hex） |
|---|---|
| 森林绿（Forest，默认） | #12644A |
| 青竹（Bamboo） | #2E7D5B |
| 松石青（Teal） | #0E6B6B |
| 远山蓝（Azure） | #2A5CAA |
| 靛蓝（Indigo） | #4B3FA8 |
| 葡萄紫（Grape） | #7A3E9D |
| 玫瑰红（Rose） | #A63B63 |
| 暖橙（Amber） | #B85C1E |
| 琥珀黄（Ochre） | #A8791B |
| 石墨灰（Graphite） | #3C4744 |

- Android：设置页「主题色」按钮，预设色块 + RGB 滑杆自定义取色。
- iOS / iPadOS：设置页预设色板 + 系统原生取色器（ColorPicker）。
- Windows / Linux / macOS：托盘「主题色」子菜单，10 个预设 + 「自定义颜色…」弹系统取色器；托盘图标与休息屏倒计时颜色跟随主题。
- 也可直接改 config.json 里的 theme_color（如 #2A5CAA）。

## 官网与品牌素材（Site & brand assets）

- 官网源码（Site source）：site/index.html，纯静态单页，含主题色演示。
- 图标生成器（Icon generator）：tools/make_icons.py，改配色或图形后运行一次即可重出全平台图标、启动页 logo、商店特性图。
- 商店文案（Store listings）：store/google-play.md、store/app-store.md，中英双语；隐私政策在 store/privacy-policy.md。

## 语音音色（Voice）

三种场景的台词（Lines for the three moments）：

| 场景（Scene） | 中文（Chinese） | 英文（English） |
|---|---|---|
| 开始休息（Break starts） | 休息一下，离开屏幕，看看远处，让眼睛放松一下吧 | Time for a break. Please look away from the screen and relax your eyes. |
| 中途提醒（Halfway） | 再坚持一下，记得多眨眨眼 | Hang in there a little longer. Remember to blink. |
| 休息结束（Break ends） | 休息完成，欢迎回来 | Break finished. Welcome back. |

对应的音频文件（Matching audio files）：

| 场景（Scene） | 中文文件（Chinese file） | 英文文件（English file） |
|---|---|---|
| 开始休息（Break starts） | voice_rest_zh.mp3 | voice_rest_en.mp3 |
| 中途提醒（Halfway） | voice_mid_zh.mp3 | voice_mid_en.mp3 |
| 休息结束（Break ends） | voice_done_zh.mp3 | voice_done_en.mp3 |

- 音色（Voice model）：中文用「晓晓」（zh-CN-XiaoxiaoNeural），英文用「Aria」（en-US-AriaNeural）。
- 语速（Rate）：比默认慢 8%，听起来更柔和。
- 试听（Listen）：也可以在「语音（Voice）」文件夹里直接点开中文命名的副本试听。
- 重新生成（Regenerate）：编辑 make_voice.py 里的台词与音色，联网运行一次 python make_voice.py（需先安装 edge-tts）。

## 安装（Install）

1. 双击「安装到本机.bat」，按提示选择 1（中文）或 2（English）。
   （Double-click the installer bat file and choose 1 for Chinese or 2 for English.）
2. 安装完成后自动写入开机自启，下次开机自动运行。
   （Auto-start is registered; it will run from the next boot.）
3. 想立刻启动（To start now）：双击桌面上的「护眼管家.bat」。
   （Do NOT double-click EyeGuard.pyw directly — .pyw has no file association on most systems.）

## 使用（Usage）

托盘绿色圆点右键（Right-click the green tray icon）：

- 立即休息（Take a break now）
- 暂停监控（Pause / resume monitoring）
- 普通时长（Normal interval）
- 娱乐时长（Entertainment interval）
- 识别全屏场景（Detect fullscreen app）开关
- 学习时最多延后（Max delay while studying）
- 语言 / Language（中文 / English）
- 退出护眼管家（Exit）

## 设置（Configuration）

编辑 config.json（Edit config.json）：

| 键（Key） | 说明（Description） | 默认（Default） |
|---|---|---|
| interval_min | 注视多久后休息（minutes of viewing before a break） | 30 |
| entertainment_min | 娱乐网页的时长（entertainment interval） | 25 |
| smart_scene | 是否识别全屏场景（enable scene detection） | true |
| study_max_wait_min | 学习中最多延后多久（0 = 一直等到退出） | 30 |
| study_apps | 自定义学习类进程名（extra study processes，数组） | 内置一张表 |
| break_sec | 休息时长秒数（break length in seconds） | 20 |
| use_camera | 是否启用摄像头（enable webcam detection） | true |
| lang | 语言（language）：zh / en | zh |
| theme_color | 主题色（theme colour，#RRGGBB） | #12644A |

## 隐私（Privacy）

摄像头画面仅在本机内存中处理，不联网、不写入磁盘、不上传。
（Webcam frames are processed in memory only — no network, no disk writes, no uploads.）

## 卸载（Uninstall）

1. 托盘图标右键 → 退出护眼管家（Exit from the tray menu）。
2. 运行 regedit，删除 HKEY_CURRENT_USER\Software\Microsoft\Windows\CurrentVersion\Run 下的 EyeGuard 项。
3. 删除 C:\Users\Public\EyeGuard 文件夹。

## 文件说明（Files）

| 文件（File） | 作用（Purpose） |
|---|---|
| EyeGuard.pyw | 主程序（main program） |
| install.py | 安装脚本（installer） |
| rest.html | 休息屏（break screen） |
| config.json | 配置（configuration） |
| make_voice.py | 语音生成脚本（voice generator） |
| voice_*.mp3 | 预生成语音（pre-generated voice clips） |
| rest-*.mp4 / rest-bg.png | 休息屏素材（break screen media） |
| haarcascade_frontalface_default.xml | 人脸检测模型（face detection model） |
| 使用说明（中文）.txt / README（English）.txt | 详细说明（detailed manual） |
