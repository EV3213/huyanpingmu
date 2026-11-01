package com.eyeguard.app

import android.app.Activity
import android.content.res.Configuration
import android.graphics.Color
import android.media.MediaPlayer
import android.net.Uri
import android.os.Bundle
import android.os.Handler
import android.os.Looper
import android.speech.tts.TextToSpeech
import android.view.View
import android.view.WindowManager
import android.widget.TextView
import android.widget.VideoView
import java.util.Locale
import kotlin.math.max

/**
 * 全屏休息页：置顶覆盖、亮屏、倒计时 + 语音提醒。
 * 若把绿植视频放进 res/raw（rest_aerial.mp4 / rest_plant.mp4）会自动作为背景播放。
 */
class BreakActivity : Activity() {

    companion object {
        const val EXTRA_LANG = "lang"
        const val EXTRA_SECONDS = "seconds"
    }

    private val handler = Handler(Looper.getMainLooper())
    private var tts: TextToSpeech? = null
    private var left = 20
    private var total = 20
    private var isZh = true

    private lateinit var titleView: TextView
    private lateinit var tipView: TextView
    private lateinit var countView: TextView
    private lateinit var doneView: TextView
    private lateinit var video: VideoView

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        isZh = (intent.getStringExtra(EXTRA_LANG) ?: "zh") != "en"
        total = max(5, intent.getIntExtra(EXTRA_SECONDS, 20))
        left = total

        window.addFlags(WindowManager.LayoutParams.FLAG_KEEP_SCREEN_ON)
        setContentView(R.layout.activity_break)
        enterFullscreen()

        titleView = findViewById(R.id.breakTitle)
        tipView = findViewById(R.id.breakTip)
        countView = findViewById(R.id.breakCount)
        doneView = findViewById(R.id.breakDone)
        video = findViewById(R.id.breakVideo)

        titleView.text = if (isZh) "休息一下" else "Take a Break"
        tipView.text = if (isZh)
            "请离开屏幕，望向 6 米以外的远处\n多眨眼 · 伸展肩颈 · 喝口水"
        else
            "Look away from the screen at something 6 meters away\nBlink more · Stretch · Take a sip of water"
        doneView.text = if (isZh) "✨ 休息完成，马上回到工作" else "✨ Break finished — back to work"
        updateCount()

        playBackgroundVideo()
        initTts()
        handler.postDelayed({ tick() }, 1000)
    }

    private fun enterFullscreen() {
        @Suppress("DEPRECATION")
        window.decorView.systemUiVisibility = (
                View.SYSTEM_UI_FLAG_LAYOUT_STABLE
                        or View.SYSTEM_UI_FLAG_LAYOUT_HIDE_NAVIGATION
                        or View.SYSTEM_UI_FLAG_LAYOUT_FULLSCREEN
                        or View.SYSTEM_UI_FLAG_HIDE_NAVIGATION
                        or View.SYSTEM_UI_FLAG_FULLSCREEN
                        or View.SYSTEM_UI_FLAG_IMMERSIVE_STICKY)
        window.statusBarColor = Color.BLACK
        window.navigationBarColor = Color.BLACK
    }

    private fun playBackgroundVideo() {
        val candidates = listOf("rest_aerial", "rest_plant", "rest_bg")
        val name = candidates.firstOrNull {
            resources.getIdentifier(it, "raw", packageName) != 0
        } ?: return
        val type = if (name == "rest_bg") "drawable" else "raw"
        val id = resources.getIdentifier(name, type, packageName)
        if (id == 0) return
        val uri = Uri.parse("android.resource://$packageName/$id")
        video.visibility = View.VISIBLE
        video.setVideoURI(uri)
        video.setOnPreparedListener { mp: MediaPlayer ->
            mp.isLooping = true
            mp.setVolume(0f, 0f)
            video.start()
        }
        video.setOnErrorListener { _, _, _ ->
            video.visibility = View.GONE
            true
        }
    }

    private fun initTts() {
        tts = TextToSpeech(this) { status ->
            if (status == TextToSpeech.SUCCESS) {
                val loc = if (isZh) Locale.SIMPLIFIED_CHINESE else Locale.US
                tts?.language = loc
                tts?.setSpeechRate(0.92f)
                tts?.setPitch(1.03f)
                speak(if (isZh)
                    "休息一下，离开屏幕，看看远处，让眼睛放松一下吧"
                else
                    "Time for a break. Please look away from the screen and relax your eyes.")
            }
        }
    }

    private fun speak(text: String) {
        tts?.speak(text, TextToSpeech.QUEUE_FLUSH, null, "eyeguard")
    }

    private fun updateCount() {
        countView.text = if (isZh) "休息倒计时 $left 秒" else "Break ends in $left s"
    }

    private fun tick() {
        left--
        if (left <= 0) {
            finishSelf()
            return
        }
        updateCount()
        if (left == total / 2) {
            speak(if (isZh) "再坚持一下，记得多眨眨眼" else "Hang in there a little longer. Remember to blink.")
        }
        handler.postDelayed({ tick() }, 1000)
    }

    private fun finishSelf() {
        countView.visibility = View.GONE
        doneView.visibility = View.VISIBLE
        speak(if (isZh) "休息完成，欢迎回来" else "Break finished. Welcome back.")
        handler.postDelayed({
            finish()
            overridePendingTransition(0, 0)
        }, 2200)
    }

    override fun onConfigurationChanged(newConfig: Configuration) {
        super.onConfigurationChanged(newConfig)
        enterFullscreen()
    }

    override fun onDestroy() {
        handler.removeCallbacksAndMessages(null)
        try {
            video.stopPlayback()
        } catch (_: Exception) {
        }
        tts?.stop()
        tts?.shutdown()
        super.onDestroy()
    }
}
