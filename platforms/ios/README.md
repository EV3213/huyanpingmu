# iOS 版（iOS build）

iPhone 上的护眼提醒（Eye-care reminder for iPhone）。

## 真话先说（Honest limits）

iOS 不允许第三方 App 在后台常开摄像头，也不允许弹窗盖住别的 App。所以 iOS 版和桌面版不是同一套机制：

| 桌面版（Windows / macOS / Linux） | iOS 版 |
|---|---|
| 后台摄像头判断你在不在看屏幕 | 仅前台可用摄像头（App 打开时） |
| 强制全屏休息屏 | 前台到点直接全屏休息页；后台靠本地通知 |
| 静默常驻 | 不能常驻，靠系统通知唤醒你 |

想要「后台也真的挡住你」只能走苹果的**屏幕使用时间**（Screen Time / FamilyControls），需要单独申请 entitlement，见本文末。

## 构建（Build）

需要 Mac + Xcode 15+，用 [XcodeGen](https://github.com/yonaskolb/XcodeGen) 生成工程：

```bash
brew install xcodegen
cd platforms/ios
xcodegen generate
open EyeGuard.xcodeproj
```

然后在 Xcode 里选你的开发者账号（Signing & Capabilities）→ 连上 iPhone → Run。

## 功能（Features）

- 计时监控：可调注视时长（1–60 分钟）与休息时长（5–60 秒）
- 前台摄像头人脸检测（Vision，本机处理，不上传）
- 休息页：全屏大字 + 倒计时 + 中文/英文语音（AVSpeechSynthesizer）
- 休息页背景：把 `../assets/rest-aerial.mp4`、`rest-plant.mp4` 拖进 Xcode 工程（Copy Bundle Resources），会自动作为背景循环播放
- 后台到点：本地通知提醒（需允许通知权限）
- 中英双语一键切换

## 文件（Files）

| 文件（File） | 作用（Purpose） |
|---|---|
| EyeGuard/EyeGuardApp.swift | App 入口（entry point） |
| EyeGuard/ContentView.swift | 设置界面（settings UI） |
| EyeGuard/Monitor.swift | 计时 + 摄像头 + 通知（timer / camera / notifications） |
| EyeGuard/BreakView.swift | 全屏休息页（break screen） |
| project.yml | XcodeGen 工程描述（project spec） |

## 进阶：真正「挡住你」（Optional: Screen Time shielding）

1. 到 Apple Developer 后台为 App ID 勾选 **Family Controls**（个人开发者也可申请，需说明用途）
2. Xcode → Signing & Capabilities → 添加 Family Controls
3. 用 `FamilyControls` + `DeviceActivity` + `ManagedSettings` 实现：到点给指定 App 套上盾牌（Shield），盾牌上写「休息一下」

这套 API 才是 App Store 上护眼类 App 的正规做法，但它授予的是「限制 App 使用」的权限，需要用户点一次授权。
