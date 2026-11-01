# 隐私政策 / Privacy Policy

最后更新（Last updated）：2026-11-01
适用产品（Products）：护眼管家 EyeGuard（Windows / Linux / macOS / Android / iOS / iPadOS）

---

## 简体中文

### 一句话总结
护眼管家不收集、不存储、不传输你的任何个人信息。

### 1. 我们处理什么
本应用唯一的传感器访问是**摄像头**，用途单一：判断画面中是否有人脸，从而知道你是否还坐在屏幕前。

- 画面**只在本机内存**中处理，检测完成后立即丢弃；
- **不写入磁盘**，不保存截图、视频或任何帧；
- **不上传**，应用不发起任何网络请求；
- 不使用云端人脸识别，检测模型随安装包一起提供。

### 2. 我们不收集什么
- 不收集姓名、邮箱、电话、账号等身份信息；
- 不收集设备标识符、位置、通讯录、短信、相册；
- 不接入第三方统计、广告或推送 SDK；
- 不设置追踪 Cookie，不做跨应用追踪。

### 3. 本机保存的设置
应用会在你的设备上保存少量配置：注视时长、休息时长、是否启用摄像头、界面语言、主题色。
这些数据仅存于本机（Windows 为程序目录下的 `config.json`；Android 为应用私有 SharedPreferences；iOS/iPadOS 为应用 UserDefaults），不会离开你的设备，卸载即删除。

### 4. 权限说明
| 平台 | 权限 | 用途 | 拒绝后 |
|---|---|---|---|
| 全部 | 相机 | 本机人脸检测 | 自动降级为纯计时模式，功能照常 |
| Android 13+ | 通知 | 显示休息提醒 | 仍可用，仅无通知 |
| Android | 开机自启 | 重启后恢复监控 | 需手动启动 |
| Android | 前台服务（相机） | 保证长时间稳定监控 | 系统可能在后台回收 |

### 5. 儿童
本应用不面向 13 岁以下儿童单独收集任何数据（事实上不收集任何数据）。

### 6. 你的权利
由于我们不在服务端保存任何数据，无需「导出」或「删除账户」。删除应用即清除本机全部配置。

### 7. 变更
若未来版本引入需要联网的功能，我们会在应用内与仓库 README 中明确说明，并先更新本政策。

### 8. 联系方式
通过仓库 Issues 联系：https://github.com/EV3213/huyanpingmu/issues

---

## English

### Summary
EyeGuard does not collect, store, or transmit any personal information.

### 1. What we process
The only sensor the app uses is the **camera**, for one purpose: to detect whether a face is present, so it knows you are still at the screen.

- Frames are processed **in memory only** and discarded immediately after detection;
- **Never written to disk** — no screenshots, clips or frames are stored;
- **Never uploaded** — the app makes no network requests;
- No cloud face recognition; the detection model ships inside the installer.

### 2. What we do not collect
- No name, email, phone number or account information;
- No device identifiers, location, contacts, messages or photos;
- No third-party analytics, advertising or push SDKs;
- No tracking cookies, no cross-app tracking.

### 3. Settings stored on your device
The app stores a few settings locally: viewing interval, break length, camera toggle, UI language, theme colour.
They live only on your device (Windows: `config.json` next to the program; Android: private SharedPreferences; iOS/iPadOS: UserDefaults). They never leave the device and are removed when you uninstall.

### 4. Permissions
| Platform | Permission | Purpose | If denied |
|---|---|---|---|
| All | Camera | On-device face detection | Falls back to timer-only mode |
| Android 13+ | Notifications | Show break reminders | App still works |
| Android | Boot completed | Resume monitoring after reboot | Start manually |
| Android | Foreground service (camera) | Keep monitoring stable | System may reclaim it |

### 5. Children
The app does not knowingly collect data from children under 13 — in fact it collects no data at all.

### 6. Your rights
Because nothing is stored on a server, there is no account to export or delete. Uninstalling removes all local settings.

### 7. Changes
If a future version introduces anything that needs the network, we will state it clearly in the app and in the repository README, and update this policy first.

### 8. Contact
Open an issue: https://github.com/EV3213/huyanpingmu/issues
