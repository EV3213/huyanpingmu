# 共享素材（Shared assets）

各平台共用这一份媒体与模型，安装/构建时各自取用，避免同一段视频塞六份。

| 文件（File） | 用途（Used by） | 大小（Size） |
|---|---|---|
| rest-aerial.mp4 | 休息屏背景 · 航拍绿植（break screen · aerial） | 1.2 MB |
| rest-plant.mp4 | 休息屏背景 · 实拍绿植（break screen · plant） | 2.2 MB |
| rest-bg.png | 静态兜底图（fallback poster） | 2.6 MB |

## 各端怎么用（How each platform consumes them）

- **Windows**：把三个文件放进 `platforms/windows/`（和 rest.html 同级）
- **Linux / macOS**：`install.sh` 自动从 `platforms/assets/` 复制到安装目录
- **Android**：可选，`cp platforms/assets/rest-aerial.mp4 platforms/android/app/src/main/res/raw/rest_aerial.mp4`
- **iOS / iPadOS**：可选，把 mp4 拖进 Xcode 工程的 Copy Bundle Resources

语音文件（voice_*.mp3）已经分别放在各桌面端目录里，Android / iOS 用系统 TTS 兜底。
