#!/usr/bin/env bash
# 护眼管家 EyeGuard - macOS 安装（Installer for macOS）
set -e

HERE="$(cd "$(dirname "$0")" && pwd)"
ASSETS="$HERE/../assets"
TARGET="$HOME/Library/Application Support/EyeGuard/app"
PY="${PYTHON:-python3}"

echo "== 护眼管家 EyeGuard · macOS =="
echo "安装到（Install path）: $TARGET"

if ! command -v "$PY" >/dev/null 2>&1; then
  echo "缺少 python3，请先安装（brew install python 或从 python.org 下载）"
  exit 1
fi

echo "→ 检查依赖（Checking dependencies）"
if ! "$PY" - <<'EOF'
import importlib, sys
missing = [m for m in ("cv2", "pystray", "PIL") if importlib.util.find_spec(m) is None]
print("缺失（missing）:", ", ".join(missing) if missing else "无")
sys.exit(1 if missing else 0)
EOF
then
  echo "→ 安装依赖（Installing dependencies）"
  "$PY" -m pip install --user --upgrade opencv-python-headless pystray pillow pyobjc-framework-Cocoa
fi

echo "→ 复制文件（Copying files）"
mkdir -p "$TARGET"
cp "$HERE/eyeguard.py" "$HERE/rest.html" "$TARGET/"
cp "$HERE/haarcascade_frontalface_default.xml" "$TARGET/" 2>/dev/null || true
cp "$HERE"/voice_*.mp3 "$TARGET/" 2>/dev/null || true
for f in rest-aerial.mp4 rest-plant.mp4 rest-bg.png; do
  [ -f "$ASSETS/$f" ] && cp "$ASSETS/$f" "$TARGET/" || true
done
chmod +x "$TARGET/eyeguard.py"

echo "→ 注册开机自启（Registering LaunchAgent）"
"$PY" "$TARGET/eyeguard.py" --install

echo "→ 启动（Starting）"
nohup "$PY" "$TARGET/eyeguard.py" >/dev/null 2>&1 &

cat <<EOF

完成（Done）。
  菜单栏图标（Menu bar）: 右上角绿色圆点
  查看状态（status）    : $PY "$TARGET/eyeguard.py" --status
  立即休息（try now）   : $PY "$TARGET/eyeguard.py" --rest
  卸载自启（uninstall） : $PY "$TARGET/eyeguard.py" --uninstall
  配置（config）        : ~/Library/Application Support/EyeGuard/config.json

摄像头权限（Camera permission）：
  系统设置 → 隐私与安全性 → 相机，把运行它的终端（Terminal / iTerm）勾上。
  macOS 13+ 首次启动会弹窗，允许即可。
EOF
