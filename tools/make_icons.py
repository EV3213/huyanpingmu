#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
EyeGuard 图标 / 启动页素材生成器
---------------------------------
一次产出全平台所需尺寸，改配色或图形只需改本文件再运行：

    python tools/make_icons.py

产出：
  platforms/ios/EyeGuard/Assets.xcassets/AppIcon.appiconset/Icon-1024.png
  platforms/ipados/EyeGuard/Assets.xcassets/AppIcon.appiconset/Icon-1024.png
  platforms/android/app/src/main/res/mipmap-*/ic_launcher.png (+_round)
  platforms/android/app/src/main/res/drawable/launch_logo.png
  platforms/assets/brand/（商店用：特性图、图标大图、启动页 logo）
"""

import os
import json
from PIL import Image, ImageDraw, ImageFont

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# ── 品牌色 ────────────────────────────────────────────────────────────────
BG_TOP = (23, 105, 79)        # #17694F
BG_BOTTOM = (9, 58, 43)       # #0A3A2B
EYE_WHITE = (255, 255, 255)
IRIS = (18, 100, 74)          # #12644A
PUPIL = (8, 46, 34)           # #082E22

SS = 4                        # 超采样倍数（抗锯齿）


# ── 基础绘图工具 ──────────────────────────────────────────────────────────

def quad(p0, p1, p2, n=160):
    """二次贝塞尔采样点"""
    pts = []
    for i in range(n + 1):
        t = i / n
        mt = 1 - t
        x = mt * mt * p0[0] + 2 * mt * t * p1[0] + t * t * p2[0]
        y = mt * mt * p0[1] + 2 * mt * t * p1[1] + t * t * p2[1]
        pts.append((x, y))
    return pts


def almond(cx, cy, half_w, half_h, steps=160):
    """杏仁形（眼睛外形）多边形点集"""
    left = (cx - half_w, cy)
    right = (cx + half_w, cy)
    top = (cx, cy - half_h)
    bottom = (cx, cy + half_h)
    return quad(left, top, right, steps) + quad(right, bottom, left, steps)


def leaf(cx, cy, half_w, half_h, steps=100):
    """叶片形（瞳孔）多边形点集：上下两个尖点，左右外凸"""
    top = (cx, cy - half_h)
    bottom = (cx, cy + half_h)
    right = (cx + half_w, cy)
    left = (cx - half_w, cy)
    return quad(top, right, bottom, steps) + quad(bottom, left, top, steps)


def vertical_gradient(size, top, bottom):
    """竖直渐变图"""
    h = size
    strip = Image.new("RGB", (1, h))
    for y in range(h):
        t = y / max(1, h - 1)
        strip.putpixel((0, y), tuple(int(top[i] + (bottom[i] - top[i]) * t) for i in range(3)))
    return strip.resize((size, size), Image.BILINEAR)


def rounded_mask(size, radius_ratio):
    """圆角矩形遮罩"""
    m = Image.new("L", (size, size), 0)
    d = ImageDraw.Draw(m)
    r = int(size * radius_ratio)
    d.rounded_rectangle([0, 0, size - 1, size - 1], radius=r, fill=255)
    return m


# ── 图形绘制 ──────────────────────────────────────────────────────────────

def draw_mark(draw, size, scale=1.0, cx=None, cy=None):
    """
    绘制「眼睛 + 叶片瞳孔」标志。
    size: 画布边长；scale: 标志相对画布的大小比例（1.0 约等于铺满 76%）
    """
    cx = size / 2 if cx is None else cx
    cy = size / 2 if cy is None else cy
    half_w = size * 0.30 * scale
    half_h = size * 0.155 * scale
    iris_r = size * 0.105 * scale
    leaf_w = size * 0.045 * scale
    leaf_h = size * 0.070 * scale

    # 眼睛底色（白）
    draw.polygon(almond(cx, cy, half_w, half_h), fill=EYE_WHITE)
    # 虹膜
    draw.ellipse([cx - iris_r, cy - iris_r, cx + iris_r, cy + iris_r], fill=IRIS)
    # 叶片瞳孔
    draw.polygon(leaf(cx, cy, leaf_w, leaf_h), fill=PUPIL)


def render_icon(size, rounded=True, transparent=False, radius_ratio=0.225, scale=1.0):
    """生成一枚图标（返回 RGB / RGBA 图）"""
    w = size * SS
    if transparent:
        img = Image.new("RGBA", (w, w), (0, 0, 0, 0))
    else:
        bg = vertical_gradient(w, BG_TOP, BG_BOTTOM).convert("RGBA")
        if rounded:
            mask = rounded_mask(w, radius_ratio)
            img = Image.new("RGBA", (w, w), (0, 0, 0, 0))
            img.paste(bg, (0, 0), mask)
        else:
            img = bg

    layer = Image.new("RGBA", (w, w), (0, 0, 0, 0))
    draw_mark(ImageDraw.Draw(layer), w, scale=scale)
    img = Image.alpha_composite(img, layer)

    out = img.resize((size, size), Image.LANCZOS)
    return out


def render_splash_logo(size, color=(255, 255, 255)):
    """启动页 logo：透明底、单色眼睛（默认白色，用于深色启动背景）"""
    w = size * SS
    cx = cy = w / 2
    half_w = w * 0.30
    half_h = w * 0.155
    iris_r = w * 0.105
    leaf_w = w * 0.045
    leaf_h = w * 0.070

    # 用遮罩绘制，叶片做「打孔」处理
    mask = Image.new("L", (w, w), 0)
    md = ImageDraw.Draw(mask)
    md.polygon(almond(cx, cy, half_w, half_h), fill=255)
    md.ellipse([cx - iris_r, cy - iris_r, cx + iris_r, cy + iris_r], fill=255)
    md.polygon(leaf(cx, cy, leaf_w, leaf_h), fill=0)

    img = Image.new("RGBA", (w, w), color + (0,))
    img.putalpha(mask)
    return img.resize((size, size), Image.LANCZOS)


def font(sz, bold=True):
    """优先微软雅黑粗体"""
    for name in ("msyhbd.ttc" if bold else "msyh.ttc", "msyh.ttc", "simhei.ttf"):
        p = os.path.join("C:\\Windows\\Fonts", name)
        if os.path.exists(p):
            try:
                return ImageFont.truetype(p, sz)
            except Exception:
                continue
    return ImageFont.load_default()


def render_feature(width, height):
    """商店特性图 1024×500"""
    w, h = width * 2, height * 2
    # 渐变按宽生成正方形，裁到目标画布，避免纵向压扁
    img = vertical_gradient(w, BG_TOP, BG_BOTTOM).convert("RGBA").crop((0, 0, w, h))

    # 右侧图标 + 浅色衬底（与背景拉开层次；半透明需在独立图层上合成）
    card = int(h * 0.74)
    cx_card = w - card // 2 - int(h * 0.16)
    cy_card = h // 2
    card_layer = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    ImageDraw.Draw(card_layer).rounded_rectangle(
        [cx_card - card // 2, cy_card - card // 2,
         cx_card + card // 2, cy_card + card // 2],
        radius=int(card * 0.24), fill=(255, 255, 255, 34))
    img = Image.alpha_composite(img, card_layer)

    mark = render_icon(int(h * 0.58), rounded=True, radius_ratio=0.225, scale=1.0)
    img.alpha_composite(mark, (cx_card - mark.width // 2, cy_card - mark.height // 2))

    # 左侧文字（整组垂直居中）
    d = ImageDraw.Draw(img)
    tx = int(h * 0.20)
    d.text((tx, int(h * 0.36)), "护眼管家", font=font(int(h * 0.20)),
           fill=(255, 255, 255, 255), anchor="lm")
    d.text((tx, int(h * 0.575)), "EyeGuard", font=font(int(h * 0.105), False),
           fill=(168, 226, 203, 255), anchor="lm")
    d.text((tx, int(h * 0.715)), "看屏幕久了，强制休息一下", font=font(int(h * 0.058), False),
           fill=(220, 240, 232, 255), anchor="lm")

    return img.resize((width, height), Image.LANCZOS)


# ── 落盘 ──────────────────────────────────────────────────────────────────

def save(img, *parts):
    path = os.path.join(ROOT, *parts)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    if img.mode == "RGBA" and parts[-1].lower().endswith((".png",)):
        img.save(path, "PNG", optimize=True)
    else:
        img.convert("RGB").save(path, "PNG", optimize=True)
    kb = os.path.getsize(path) / 1024
    print("  %-64s %5.0f KB" % ("/".join(parts), kb))
    return path


APPICON_JSON = {
    "images": [
        {"filename": "Icon-1024.png", "idiom": "universal",
         "platform": "ios", "size": "1024x1024"}
    ],
    "info": {"author": "xcode", "version": 1},
}

CONTENTS_JSON = {
    "images": [
        {"idiom": "universal", "filename": "LaunchLogo.png",
         "scale": "1x"},
        {"idiom": "universal", "scale": "2x"},
        {"idiom": "universal", "scale": "3x"},
    ],
    "info": {"author": "xcode", "version": 1},
}


def main():
    print("生成图标 …")

    icon = render_icon(1024)                       # iOS 用，满版不透明
    save(icon.convert("RGB"), "platforms/assets/brand/icon-1024.png")

    for plat in ("ios", "ipados"):
        base = ("platforms", plat, "EyeGuard", "Assets.xcassets")
        save(icon.convert("RGB"), *base, "AppIcon.appiconset", "Icon-1024.png")
        with open(os.path.join(ROOT, *base, "AppIcon.appiconset", "Contents.json"), "w",
                  encoding="utf-8") as f:
            json.dump(APPICON_JSON, f, ensure_ascii=False, indent=2)

        # 启动页 logo（@1x/@2x/@3x）
        for scale, suffix in ((1, ""), (2, "@2x"), (3, "@3x")):
            logo = render_splash_logo(120 * scale)
            save(logo, *base, "LaunchLogo.imageset", "LaunchLogo%s.png" % suffix)
        with open(os.path.join(ROOT, *base, "LaunchLogo.imageset", "Contents.json"), "w",
                  encoding="utf-8") as f:
            json.dump(CONTENTS_JSON, f, ensure_ascii=False, indent=2)

    # Android：自适应图标前景（透明，标志收在安全区内）
    fg = render_icon(432, transparent=True, scale=0.80)
    save(fg, "platforms/android/app/src/main/res/drawable/ic_launcher_foreground.png")

    launch = render_splash_logo(480)
    save(launch, "platforms/android/app/src/main/res/drawable/launch_logo.png")

    # Android：传统 mipmap 各密度
    densities = {"mdpi": 48, "hdpi": 72, "xhdpi": 96, "xxhdpi": 144, "xxxhdpi": 192}
    for name, px in densities.items():
        save(render_icon(px), "platforms/android/app/src/main/res/mipmap-%s" % name, "ic_launcher.png")
        rnd = render_icon(px, radius_ratio=0.5)
        save(rnd, "platforms/android/app/src/main/res/mipmap-%s" % name, "ic_launcher_round.png")

    # 商店素材
    save(render_feature(1024, 500), "platforms/assets/brand/feature-graphic-1024x500.png")
    save(render_splash_logo(512), "platforms/assets/brand/logo-transparent-512.png")

    print("\n完成。")


if __name__ == "__main__":
    main()
