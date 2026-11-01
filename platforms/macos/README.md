# macOS 版（macOS build）

菜单栏常驻、静默监控，行为和 Windows 版一致（Menu-bar app, same behaviour as the Windows build）。

## 安装（Install）

```bash
cd platforms/macos
chmod +x install.sh
./install.sh
```

脚本会：检查/安装依赖 → 复制到 `~/Library/Application Support/EyeGuard/app` → 写 `~/Library/LaunchAgents/com.eyeguard.plist` → 启动。
（Checks deps → copies files → registers a LaunchAgent → starts.）

## 摄像头权限（Camera permission）

macOS 的相机权限是给「App」而不是给脚本的，所以首次要手动放行：

1. 系统设置 → 隐私与安全性 → 相机
2. 勾上你启动它的终端（Terminal / iTerm / VS Code）
3. 重新运行一次 `python3 "…/eyeguard.py" --install` 并重启程序

（Grant camera access to the terminal that launches it, or the process will fall back to timer-only.）

## 会用到的命令（Commands）

```bash
python3 "$HOME/Library/Application Support/EyeGuard/app/eyeguard.py" --status
python3 "$HOME/Library/Application Support/EyeGuard/app/eyeguard.py" --rest
python3 "$HOME/Library/Application Support/EyeGuard/app/eyeguard.py" --uninstall
```

## 依赖（Requirements）

- macOS 12+
- Python 3（`brew install python`）
- `opencv-python-headless`、`pystray`、`pillow`、`pyobjc-framework-Cocoa`（脚本自动装）
- Chrome / Edge / Brave 任一用于 kiosk 全屏（没有则 Tk 全屏兜底，用系统 TTS 朗读）

## 配置（Configuration）

`~/Library/Application Support/EyeGuard/config.json`

## 说明（Notes）

- 菜单栏图标（menu bar）而不是 Dock 图标，退出用菜单里的「退出护眼管家」。
- 首次运行会弹「想要访问摄像头」，点允许；拒绝后可在系统设置里补开。
- 若想要一个真正可双击的 `.app`（带独立图标与权限条目），可以用 `py2app` 打包，见仓库根 README 的「进阶」一节。
