# Android 版（Android build）

原生 Kotlin 工程：前台服务常驻监控 + 摄像头人脸检测 + 全屏休息页（Native Kotlin）。

## 直接安装（Install the ready-made APK）

仓库里已经放好编译好的正式签名包，不用装 Android Studio：

**apk/护眼管家-1.0.apk**（43 MB，包名 com.eyeguard.app，最低 Android 8.0，v2 签名）

装法（任选一种）：

1. **手机直接下载**：在手机浏览器打开本仓库这个文件，点「Download」→ 下载完点开安装（需在系统里允许「安装未知应用」）。
2. **电脑传手机**：USB 数据线拷到手机任意目录，用文件管理器点开安装。
3. **adb**：`adb install -r "apk/护眼管家-1.0.apk"`。

> 为什么不是 20 MB 以内：人脸检测用的是 ML Kit **离线随包**模型（不依赖 Google 服务，国内手机也能用），模型本身约 20 MB。
> 首次打开如果提示风险，是因为这个包不来自应用商店——源码全在仓库里，可自行核对或重新编译。

## 从源码构建（Build from source）

需要一个 JDK 17 和 Android SDK（Platform 34 + Build-Tools 34.0.0）。

1. 用 Android Studio（Koala 或更新）打开 `platforms/android`
2. 等 Gradle 同步完成（首次会下载 CameraX / ML Kit）
3. 连手机 → Run

命令行：

```bash
cd platforms/android
gradle wrapper --gradle-version 8.7   # 首次生成 wrapper
./gradlew assembleDebug              # 产物：app/build/outputs/apk/debug/app-debug.apk
./gradlew assembleRelease            # 正式包（需自行配置 signingConfig）
```

## 需要的权限（Permissions）

首次打开会申请：相机、通知。另外建议手动开启：

- 设置 → 应用 → 护眼管家 → 电池 → **不限制 / 允许后台运行**（否则国产 ROM 会杀掉服务）
- 设置 → 应用 → 护眼管家 → 其他权限 → **后台弹出界面**（小米 / OPPO / vivo 必须开，否则休息页弹不出来）

## 功能（Features）

- 前台服务常驻，通知栏显示「正在监测」
- CameraX + ML Kit 人脸检测（离线，画面不保存、不上传），每秒 1 帧
- 摄像头不可用 / 未授权 → 自动降级纯计时
- 到点拉起全屏休息页：大字 + 倒计时 + 中英双语 TTS
- 开机自启（BootReceiver，需用户先点过「开始监控」）
- 设置项：注视时长 1–60 分钟、休息 5–60 秒、摄像头开关、中英文切换

## 休息页背景视频（Optional video background）

把 `../assets/rest-aerial.mp4` 复制成 `app/src/main/res/raw/rest_aerial.mp4`（文件名只能小写字母/数字/下划线），重新编译即可作为全屏背景循环播放；不放也能正常休息（用深绿渐变）。

```bash
cp ../assets/rest-aerial.mp4 app/src/main/res/raw/rest_aerial.mp4
```

## 文件（Files）

| 文件（File） | 作用（Purpose） |
|---|---|
| app/src/main/java/com/eyeguard/app/MainActivity.kt | 设置界面（settings） |
| .../MonitorService.kt | 前台服务：摄像头 + 计时（foreground service） |
| .../BreakActivity.kt | 全屏休息页（break screen） |
| .../BootReceiver.kt | 开机自启（boot autostart） |
| .../Prefs.kt | 配置存储（preferences） |
| app/src/main/AndroidManifest.xml | 权限与组件声明（manifest） |
