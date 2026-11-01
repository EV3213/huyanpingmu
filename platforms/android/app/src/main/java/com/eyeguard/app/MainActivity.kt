package com.eyeguard.app

import android.Manifest
import android.content.pm.PackageManager
import android.os.Build
import android.os.Bundle
import android.widget.Button
import android.widget.SeekBar
import android.widget.Switch
import android.widget.TextView
import androidx.appcompat.app.AppCompatActivity
import androidx.core.app.ActivityCompat
import androidx.core.content.ContextCompat

class MainActivity : AppCompatActivity() {

    private lateinit var prefs: Prefs
    private lateinit var intervalLabel: TextView
    private lateinit var breakLabel: TextView
    private lateinit var statusView: TextView
    private lateinit var startBtn: Button
    private lateinit var langBtn: Button

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_main)
        prefs = Prefs(this)

        intervalLabel = findViewById(R.id.intervalLabel)
        breakLabel = findViewById(R.id.breakLabel)
        statusView = findViewById(R.id.statusText)
        startBtn = findViewById(R.id.startButton)
        langBtn = findViewById(R.id.langButton)

        val intervalSeek = findViewById<SeekBar>(R.id.intervalSeek)
        val breakSeek = findViewById<SeekBar>(R.id.breakSeek)
        val cameraSwitch = findViewById<Switch>(R.id.cameraSwitch)
        val restBtn = findViewById<Button>(R.id.restButton)

        intervalSeek.max = 59                       // 1..60 分钟
        intervalSeek.progress = prefs.intervalMin - 1
        breakSeek.max = 55                          // 5..60 秒
        breakSeek.progress = prefs.breakSec - 5
        cameraSwitch.isChecked = prefs.useCamera

        intervalSeek.setOnSeekBarChangeListener(object : SimpleSeek() {
            override fun onProgressChanged(sb: SeekBar?, p: Int, fromUser: Boolean) {
                prefs.intervalMin = p + 1
                renderLabels()
            }
        })
        breakSeek.setOnSeekBarChangeListener(object : SimpleSeek() {
            override fun onProgressChanged(sb: SeekBar?, p: Int, fromUser: Boolean) {
                prefs.breakSec = p + 5
                renderLabels()
            }
        })
        cameraSwitch.setOnCheckedChangeListener { _, checked -> prefs.useCamera = checked }

        startBtn.setOnClickListener {
            if (prefs.enabled) {
                MonitorService.stop(this)
                prefs.enabled = false
            } else {
                ensurePermissions()
                prefs.enabled = true
                MonitorService.start(this)
            }
            renderStatus()
        }

        restBtn.setOnClickListener { MonitorService.restNow(this) }

        langBtn.setOnClickListener {
            prefs.lang = if (prefs.isZh()) "en" else "zh"
            renderAll()
        }

        renderAll()
        ensurePermissions()
    }

    override fun onResume() {
        super.onResume()
        renderAll()
    }

    private fun ensurePermissions() {
        val wanted = mutableListOf(Manifest.permission.CAMERA)
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.TIRAMISU) {
            wanted.add(Manifest.permission.POST_NOTIFICATIONS)
        }
        val missing = wanted.filter {
            ContextCompat.checkSelfPermission(this, it) != PackageManager.PERMISSION_GRANTED
        }
        if (missing.isNotEmpty()) {
            ActivityCompat.requestPermissions(this, missing.toTypedArray(), 42)
        }
    }

    private fun renderAll() {
        renderLabels()
        renderStatus()
        langBtn.text = if (prefs.isZh()) "语言：中文" else "Language: English"
        startBtn.text = when {
            prefs.enabled && prefs.isZh() -> "停止监控"
            prefs.enabled -> "Stop monitoring"
            prefs.isZh() -> "开始监控"
            else -> "Start monitoring"
        }
        findViewById<TextView>(R.id.titleText).text =
            if (prefs.isZh()) "护眼管家" else "EyeGuard"
        findViewById<TextView>(R.id.subtitleText).text =
            if (prefs.isZh()) "看屏幕久了，强制休息一下" else "Take a break before your eyes complain"
    }

    private fun renderLabels() {
        intervalLabel.text = if (prefs.isZh())
            "注视 ${prefs.intervalMin} 分钟后休息"
        else
            "Break after ${prefs.intervalMin} min of viewing"
        breakLabel.text = if (prefs.isZh())
            "每次休息 ${prefs.breakSec} 秒"
        else
            "Each break lasts ${prefs.breakSec} s"
    }

    private fun renderStatus() {
        val cam = ContextCompat.checkSelfPermission(this, Manifest.permission.CAMERA) ==
                PackageManager.PERMISSION_GRANTED
        statusView.text = when {
            prefs.isZh() && prefs.enabled && cam -> "运行中 · 摄像头监测"
            prefs.isZh() && prefs.enabled -> "运行中 · 纯计时模式（未授权摄像头）"
            prefs.isZh() -> "已停止"
            prefs.enabled && cam -> "Running · camera monitoring"
            prefs.enabled -> "Running · timer only (no camera permission)"
            else -> "Stopped"
        }
    }

    private abstract class SimpleSeek : SeekBar.OnSeekBarChangeListener {
        override fun onStartTrackingTouch(sb: SeekBar?) {}
        override fun onStopTrackingTouch(sb: SeekBar?) {}
    }
}
