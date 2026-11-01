# Linux 版（Linux build）

一台跑得动 OpenCV 的 Linux 桌面机就能用（Runs on any Linux desktop with Python 3）。

## 安装（Install）

```bash
cd platforms/linux
chmod +x install.sh
./install.sh
```

脚本会：检查/安装依赖 → 复制文件到 `~/.local/share/eyeguard` → 写 `~/.config/autostart/eyeguard.desktop` → 后台启动。
（Checks deps → copies files → registers XDG autostart → starts in background.）

## 会用到的命令（Commands）

```bash
python3 ~/.local/share/eyeguard/eyeguard.py --status     # 查看状态（status）
python3 ~/.local/share/eyeguard/eyeguard.py --rest       # 立刻休息一次（try a break）
python3 ~/.local/share/eyeguard/eyeguard.py --uninstall  # 取消开机自启（remove autostart）
```

## 依赖（Requirements）

- `python3`、`python3-tk`（没有 Chromium 系浏览器时用 Tk 全屏兜底）
- `opencv-python-headless`、`pystray`、`pillow`（脚本会自动 `pip install --user`）
- 托盘图标：GNOME 需要扩展 *AppIndicator and KStatusNotifierItem Support*；KDE / XFCE 原生支持
- 浏览器：Chrome / Chromium / Brave / Edge 任一（kiosk 全屏更漂亮）；都没有则自动用 Tk 全屏

## 配置（Configuration）

`~/.config/eyeguard/config.json`

```json
{ "interval_min": 30, "break_sec": 20, "use_camera": true, "lang": "zh" }
```

## 说明（Notes）

- 摄像头走 V4L2，设备不存在或没权限（`video` 组）时自动降级为纯计时模式。
- 与 Windows 版行为一致：静默运行、托盘图标、双语音、预生成神经语音。
