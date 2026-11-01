#!/usr/bin/env bash
# 护眼管家 EyeGuard - Linux 安装（Installer for Linux）
set -e

HERE="$(cd "$(dirname "$0")" && pwd)"
ASSETS="$HERE/../assets"
TARGET="$HOME/.local/share/eyeguard"
PY="${PYTHON:-python3}"

echo "== 护眼管家 EyeGuard · Linux =="
echo "安装到（Install path）: $TARGET"

if ! command -v "$PY" >/dev/null 2>&1; then
  echo "缺少 python3，请先安装（Ubuntu/Debian: sudo apt install python3 python3-pip python3-tk）"
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
  "$PY" -m pip install --user --upgrade opencv-python-headless pystray pillow
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

echo "→ 注册开机自启（Registering autostart）"
"$PY" "$TARGET/eyeguard.py" --install

echo "→ 启动（Starting）"
nohup "$PY" "$TARGET/eyeguard.py" >/dev/null 2>&1 &

cat <<EOF

完成（Done）。
  托盘图标（Tray）     : 屏幕右上角绿色圆点
  查看状态（status）   : $PY "$TARGET/eyeguard.py" --status
  立即休息（try now）  : $PY "$TARGET/eyeguard.py" --rest
  卸载自启（uninstall）: $PY "$TARGET/eyeguard.py" --uninstall
  配置（config）       : ~/.config/eyeguard/config.json
EOF
