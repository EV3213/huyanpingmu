# 护眼管家（EyeGuard）

一个 Windows 后台护眼提醒程序（A background eye-care reminder for Windows）。

官网（Official site）：**https://eyeguard-app.app.workbuddy.host** —— 支持中英切换与主题色实时预览。
（The official site supports language switching and a live theme-colour preview.）

开机静默自启，用摄像头本地判断你是否在看屏幕；连续注视满 30 分钟，强制弹出全屏「Aerial 风格」绿植实拍休息屏，并用人声提醒你休息。
（Starts silently at boot, detects whether you are looking at the screen via webcam; after 30 minutes of continuous viewing it forces a full-screen Aerial-style nature break screen with a spoken reminder.）

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

## 功能（Features）

- 摄像头监测（Webcam monitoring）：本地人脸检测，离开屏幕即暂停计时，回来继续；画面不外传、不保存。
- 强制休息屏（Forced break screen）：全屏播放实拍绿植 / 航拍视频，20 秒倒计时，Aerial 屏保风格。
- 自然语音（Natural voice）：预生成神经网络语音，不是系统机械朗读音；离线播放，无需联网。
- 主题色自定义（Theme colour）：10 套预设配色 + 自由取色，托盘 / 设置页 / 休息屏全部跟随；桌面端图标颜色也会跟着变。
- 双语支持（Bilingual）：中英文界面与语音一键切换，选择会被记住。
- 静默运行（Runs silently）：无窗口、无任务栏图标，只在托盘区显示一个绿色圆点。
- 开机自启（Auto-start）：写入注册表自启项，重启后仍然生效。

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
- 语言 / Language（中文 / English）
- 退出护眼管家（Exit）

## 设置（Configuration）

编辑 config.json（Edit config.json）：

| 键（Key） | 说明（Description） | 默认（Default） |
|---|---|---|
| interval_min | 注视多久后休息（minutes of viewing before a break） | 30 |
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
