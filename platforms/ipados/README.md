# iPadOS 版（iPadOS build）

给 iPad 的版本：同一套逻辑，界面按大屏重排（Same app, laid out for iPad）。

## 与 iOS 版的区别（Differences from the iOS build）

| 项（Item） | iOS 版 | iPadOS 版 |
|---|---|---|
| 设备类型（Device family） | iPhone | iPad（`TARGETED_DEVICE_FAMILY = 2`） |
| Bundle ID | com.eyeguard.app | com.eyeguard.app.ipad |
| 布局（Layout） | 单列紧凑 | 单列加宽（820pt）+ 40pt 边距，横竖屏都可用 |
| 方向（Orientation） | 竖屏为主 | 四向全支持（含倒置） |

两者代码一致，方便你只维护一份逻辑；工程描述各自独立，可分别出包。

## 构建（Build）

```bash
brew install xcodegen
cd platforms/ipados
xcodegen generate
open EyeGuardHD.xcodeproj
```

Xcode 里选你的账号 → 选 iPad（或模拟器 iPad Pro）→ Run。

## 功能（Features）

- 计时监控：注视 1–60 分钟 → 强制休息 5–60 秒
- 前台摄像头人脸检测（Vision，本机处理）
- 全屏休息页 + 中英双语语音
- 后台到点用本地通知提醒（iOS 限制，见 iOS 版 README 的「真话先说」）
- 把 `../assets/` 里的绿植视频拖进工程即可作为休息页背景

## 小提示（Tips）

- iPad 上很适合做「书桌模式」：把 iPad 立在支架上，`use_camera` 打开，脸离开屏幕就暂停计时。
- 想让它像屏保一样自动出来，可以配合「引导式访问」把一个计时页锁定，或直接用系统「屏幕使用时间」限制娱乐 App。
