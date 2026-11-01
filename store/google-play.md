# Google Play 上架文案（Google Play listing）

> 语言：先发「简体中文（zh-CN）」，再用英文（en-US）发一份。两份内容一致。
> 图标与特性图见 `platforms/assets/brand/`。截图按手机 9:16 准备，至少 4 张。

---

## 一、简体中文（zh-CN）

**应用名称（30 字符内）**
```
护眼管家 EyeGuard
```

**简短说明（80 字符内）**
```
看屏幕久了就强制休息：本地人脸检测，到点全屏绿植 + 语音提醒，不联网。
```

**完整说明（4000 字符内）**
```
你有多久没从屏幕上抬起眼了？

护眼管家会安静地待在后头，用前置摄像头在本机判断你是否还坐在屏幕前。只要连续注视超过你设定的时长，它就会拉起一块全屏的实拍绿植画面，配上一句轻声提醒，让你真的离开屏幕看一会儿远处。

── 它怎么工作 ──
1. 前置摄像头每秒做一次本地人脸检测，只回答「有没有人」，画面不保存、不上传。
2. 连续注视达到设定时长（默认 30 分钟）就触发休息屏。
3. 你起身离开，计时会重新开始——它不会冤枉你。
4. 休息倒计时结束，自动回到原来的工作。

── 主要功能 ──
• 强制休息屏：全屏覆盖，倒计时结束前不打扰你，也无法误触关闭
• 实拍绿植背景：航拍森林与近景绿植两段视频随机播放，比纯色屏保更放松
• 语音提醒：预生成的神经网络语音，自然不机械；中途还会提醒你多眨眼
• 本地人脸检测：全部在本机完成，无网络请求、无画面留存
• 主题色自定义：10 套预设配色 + 自由取色，界面跟着你的喜好走
• 中英双语：一键切换，跟随你的习惯
• 开机自启：设一次，之后不用管

── 适合谁 ──
写代码的、赶稿的、刷题的、打游戏的——所有一坐下就忘了时间的人。

── 隐私 ──
摄像头画面只在本机内存中处理，检测完立即丢弃。应用不申请网络权限以外的任何敏感权限，不收集任何个人信息，不接入任何第三方统计或广告 SDK。没有摄像头权限时会自动降级为纯计时模式，功能照常。

── 关于权限 ──
• 相机：用于本地人脸检测（可拒绝，拒绝后为纯计时模式）
• 通知：休息提醒（Android 13 及以上需授权）
• 开机自启：重启后自动恢复监控

国产手机（小米 / 华为 / OPPO / vivo 等）还需在系统设置里给本应用开启「自启动」与「后台弹出界面」，并把省电策略设为「不限制」，否则休息屏可能被系统拦下。
```

**分类与标签**
- 应用类别：健康与健身（Health & Fitness）
- 标签：护眼、休息提醒、番茄钟、健康、效率
- 内容分级问卷：无暴力 / 无色情 / 无赌博 / 无用户生成内容 → 通常评为「所有人」
- 广告：不含广告
- 应用内购买：无

**数据安全表单（Data safety）**
| 项目 | 填写 |
|---|---|
| 是否收集或共享用户数据 | 否 |
| 相机 | 仅在设备上处理，不收集、不共享 |
| 数据是否加密传输 | 不适用（无传输） |
| 是否可请求删除数据 | 不适用（无服务端数据） |

**更新日志（首次发布）**
```
1.0.0
• 强制休息屏：全屏绿植视频 + 倒计时 + 语音提醒
• 本地人脸检测，判断你是否真的在看屏幕
• 10 套主题色 + 自定义取色
• 中英双语、开机自启
```

---

## 二、English (en-US)

**App name (30)**
```
EyeGuard — Eye Break Timer
```

**Short description (80)**
```
Force a real break: on-device face detection, full-screen greenery and a soft voice.
```

**Full description (4000)**
```
How long has it been since you looked away from the screen?

EyeGuard sits quietly in the background and uses the front camera — entirely on your device — to tell whether you are still there. Once you have been looking at the screen longer than your chosen interval, it takes over the display with real footage of greenery and a gentle spoken reminder, so you actually look away for a moment.

HOW IT WORKS
1. The front camera runs a local face check about once a second. It only answers "is someone there" — frames are never saved or uploaded.
2. Continuous viewing for your interval (30 minutes by default) triggers the break screen.
3. Stand up and walk away and the timer resets — it will not blame you.
4. When the countdown ends, you are back to work automatically.

FEATURES
• Forced break screen — full screen, cannot be dismissed by accident
• Real greenery footage — aerial forest and close-up plants, played at random
• Natural voice — pre-generated neural speech, with a mid-break "remember to blink"
• On-device only — no network calls, no frames kept
• Custom theme colour — 10 presets plus a free colour picker
• Bilingual — Chinese and English, one tap to switch
• Starts with your device — set it once

WHO IT IS FOR
Developers, writers, students, gamers — anyone who sits down and forgets the clock.

PRIVACY
Camera frames are processed in memory and discarded immediately. No personal data is collected, no analytics or ad SDKs are bundled. Without camera permission the app falls back to a pure timer and keeps working.

NOTE FOR SOME ROMs
On Xiaomi / Huawei / OPPO / vivo devices, allow "autostart" and "display over other apps", and set battery saver to unrestricted, otherwise the break screen may be blocked by the system.
```

**Category & tags**
- Category: Health & Fitness
- Tags: eye care, break reminder, pomodoro, wellness, productivity
- Content rating: Everyone (no violence, no adult content, no UGC)
- Ads: none · In-app purchases: none

**Data safety**
| Item | Answer |
|---|---|
| Collects or shares data | No |
| Camera | Processed on device only |
| Data encrypted in transit | Not applicable |
| Data deletion request | Not applicable |

**What's new**
```
1.0.0
• Forced break screen with greenery video, countdown and voice
• On-device face detection
• 10 theme colours plus custom picker
• Bilingual UI, autostart on boot
```
