#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""预生成护眼管家的语音（神经语音，比系统 SAPI 自然得多）

用法：python make_voice.py
依赖：pip install edge-tts
产物：rest_zh.mp3 / mid_zh.mp3 / done_zh.mp3
      rest_en.mp3 / mid_en.mp3 / done_en.mp3
"""
import asyncio
import os

import edge_tts

BASE = os.path.dirname(os.path.abspath(__file__))

ZH_VOICE = "zh-CN-XiaoxiaoNeural"   # 温柔女声，可选：zh-CN-XiaoyiNeural
EN_VOICE = "en-US-AriaNeural"       # 自然女声，可选：en-GB-SoniaNeural

LINES = {
    "zh": {
        "rest": "休息一下，离开屏幕，看看远处，让眼睛放松一下吧",
        "mid": "再坚持一下，记得多眨眨眼",
        "done": "休息完成，欢迎回来",
    },
    "en": {
        "rest": "Time for a break. Please look away from the screen and relax your eyes.",
        "mid": "Hang in there a little longer. Remember to blink.",
        "done": "Break finished. Welcome back.",
    },
}


async def build():
    proxy = (os.environ.get("HTTPS_PROXY") or os.environ.get("https_proxy")
             or os.environ.get("HTTP_PROXY") or os.environ.get("http_proxy") or None)
    for lang, items in LINES.items():
        voice = ZH_VOICE if lang == "zh" else EN_VOICE
        for key, text in items.items():
            out = os.path.join(BASE, "voice_%s_%s.mp3" % (key, lang))
            comm = edge_tts.Communicate(text, voice, rate="-8%", pitch="+0Hz",
                                        proxy=proxy, connect_timeout=30)
            await comm.save(out)
            print("已生成 %s  (%d KB)" % (os.path.basename(out), os.path.getsize(out) // 1024))


if __name__ == "__main__":
    asyncio.run(build())
