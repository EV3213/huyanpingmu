package com.eyeguard.app

import android.Manifest
import android.content.Intent
import android.content.pm.PackageManager
import android.graphics.Color
import android.os.Build
import android.os.Bundle
import android.provider.Settings
import android.text.InputType
import android.widget.Button
import android.widget.EditText
import android.widget.SeekBar
import android.widget.Switch
import android.widget.TextView
import android.widget.Toast
import androidx.appcompat.app.AlertDialog
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
    private lateinit var themeBtn: Button
    private lateinit var pinBtn: Button
    private lateinit var usageBtn: Button
    private lateinit var intervalSeek: SeekBar
    private lateinit var breakSeek: SeekBar
    private lateinit var cameraSwitch: Switch
    private lateinit var sceneSwitch: Switch

    /** 解锁后 3 分钟内免密（和桌面版一致） */
    private var unlockedAt = 0L

    /** 程序内部回滚开关状态时，忽略回调 */
    private var ignoreSwitch = false

    private val unlockMs = 3 * 60 * 1000L

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setTheme(R.style.Theme_EyeGuard)            // 结束启动页主题
        setContentView(R.layout.activity_main)
        prefs = Prefs(this)

        intervalLabel = findViewById(R.id.intervalLabel)
        breakLabel = findViewById(R.id.breakLabel)
        statusView = findViewById(R.id.statusText)
        startBtn = findViewById(R.id.startButton)
        langBtn = findViewById(R.id.langButton)
        themeBtn = findViewById(R.id.themeButton)
        pinBtn = findViewById(R.id.pinButton)
        usageBtn = findViewById(R.id.usageButton)

        intervalSeek = findViewById(R.id.intervalSeek)
        breakSeek = findViewById(R.id.breakSeek)
        cameraSwitch = findViewById(R.id.cameraSwitch)
        sceneSwitch = findViewById(R.id.sceneSwitch)
        val restBtn = findViewById<Button>(R.id.restButton)

        intervalSeek.max = 59                       // 1..60 分钟
        intervalSeek.progress = prefs.intervalMin - 1
        breakSeek.max = 55                          // 5..60 秒
        breakSeek.progress = prefs.breakSec - 5
        cameraSwitch.isChecked = prefs.useCamera
        sceneSwitch.isChecked = prefs.smartScene

        intervalSeek.setOnSeekBarChangeListener(object : SimpleSeek() {
            override fun onProgressChanged(sb: SeekBar?, p: Int, fromUser: Boolean) {
                if (!fromUser) return
                prefs.intervalMin = p + 1
                renderLabels()
            }
        })
        breakSeek.setOnSeekBarChangeListener(object : SimpleSeek() {
            override fun onProgressChanged(sb: SeekBar?, p: Int, fromUser: Boolean) {
                if (!fromUser) return
                prefs.breakSec = p + 5
                renderLabels()
            }
        })
        cameraSwitch.setOnCheckedChangeListener { _, checked ->
            if (ignoreSwitch) return@setOnCheckedChangeListener
            if (!unlocked()) {
                ignoreSwitch = true
                cameraSwitch.isChecked = prefs.useCamera
                ignoreSwitch = false
                askPinFor { prefs.useCamera = checked; renderAll() }
                return@setOnCheckedChangeListener
            }
            prefs.useCamera = checked
        }
        sceneSwitch.setOnCheckedChangeListener { _, checked ->
            if (ignoreSwitch) return@setOnCheckedChangeListener
            if (!unlocked()) {
                ignoreSwitch = true
                sceneSwitch.isChecked = prefs.smartScene
                ignoreSwitch = false
                askPinFor { prefs.smartScene = checked; renderAll() }
                return@setOnCheckedChangeListener
            }
            prefs.smartScene = checked
        }

        startBtn.setOnClickListener {
            if (prefs.enabled) {
                // 停止监控等于关掉这层保护，需要密码
                guard {
                    MonitorService.stop(this)
                    prefs.enabled = false
                    renderStatus()
                    renderAll()
                }
            } else {
                ensurePermissions()
                prefs.enabled = true
                MonitorService.start(this)
                renderStatus()
                renderAll()
            }
        }

        restBtn.setOnClickListener { MonitorService.restNow(this) }

        langBtn.setOnClickListener {
            guard {
                prefs.lang = if (prefs.isZh()) "en" else "zh"
                renderAll()
            }
        }

        themeBtn.setOnClickListener {
            guard {
                ThemeColor.showPicker(this, prefs.isZh(),
                    onPreview = { renderAll() },
                    onPicked = { renderAll() })
            }
        }

        usageBtn.setOnClickListener {
            startActivity(Intent(Settings.ACTION_USAGE_ACCESS_SETTINGS))
        }

        pinBtn.setOnClickListener { onPinButton() }

        renderAll()
        ensurePermissions()
    }

    override fun onResume() {
        super.onResume()
        renderAll()
    }

    // ---------- 家长密码 ----------

    private fun unlocked(): Boolean =
        !prefs.hasPin || System.currentTimeMillis() - unlockedAt < unlockMs

    private fun guard(action: () -> Unit) {
        if (unlocked()) action() else askPinFor(action)
    }

    /** 弹密码框，验证通过才执行 action */
    private fun askPinFor(action: () -> Unit) {
        val input = EditText(this).apply {
            inputType = InputType.TYPE_CLASS_NUMBER or InputType.TYPE_NUMBER_VARIATION_PASSWORD
            hint = prefs.tr("4 位以上数字", "4+ digits")
        }
        AlertDialog.Builder(this)
            .setTitle(prefs.tr("输入家长密码", "Enter parent PIN"))
            .setView(input)
            .setPositiveButton(prefs.tr("确定", "OK")) { _, _ ->
                if (prefs.checkPin(input.text.toString())) {
                    unlockedAt = System.currentTimeMillis()
                    action()
                    renderAll()
                } else {
                    toast(prefs.tr("密码不对", "Wrong PIN"))
                }
            }
            .setNegativeButton(prefs.tr("取消", "Cancel"), null)
            .show()
    }

    private fun onPinButton() {
        if (!prefs.hasPin) {
            askNewPin()
            return
        }
        // 已设密码：先解锁，再问要改还是关
        guard {
            AlertDialog.Builder(this)
                .setTitle(prefs.tr("家长密码", "Parent PIN"))
                .setItems(
                    arrayOf(
                        prefs.tr("修改密码", "Change PIN"),
                        prefs.tr("关闭密码（孩子也能改了）", "Turn PIN off")
                    )
                ) { _, which ->
                    if (which == 0) {
                        askNewPin()
                    } else {
                        prefs.clearPin()
                        toast(prefs.tr("已关闭家长密码", "PIN turned off"))
                        renderAll()
                    }
                }
                .show()
        }
    }

    private fun askNewPin() {
        val input = EditText(this).apply {
            inputType = InputType.TYPE_CLASS_NUMBER or InputType.TYPE_NUMBER_VARIATION_PASSWORD
            hint = prefs.tr("4~8 位数字", "4-8 digits")
        }
        AlertDialog.Builder(this)
            .setTitle(prefs.tr("设置家长密码", "Set parent PIN"))
            .setMessage(
                prefs.tr(
                    "设好之后，改时长、换主题、停止监控都要先输这个密码。",
                    "Once set, changing the timer, theme or stopping monitoring needs this PIN."
                )
            )
            .setView(input)
            .setPositiveButton(prefs.tr("保存", "Save")) { _, _ ->
                val pin = input.text.toString()
                if (!Pin.valid(pin)) {
                    toast(prefs.tr("请设 4~8 位数字", "Use 4-8 digits"))
                    return@setPositiveButton
                }
                prefs.setPin(pin)
                unlockedAt = System.currentTimeMillis()
                toast(prefs.tr("家长密码已设置", "PIN saved"))
                renderAll()
            }
            .setNegativeButton(prefs.tr("取消", "Cancel"), null)
            .show()
    }

    private fun toast(msg: String) =
        Toast.makeText(this, msg, Toast.LENGTH_SHORT).show()

    // ---------- 权限 / 状态 ----------

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
        applyThemeColors()
        renderLabels()
        renderStatus()
        val zh = prefs.isZh()
        langBtn.text = if (zh) "语言：中文" else "Language: English"
        themeBtn.text = if (zh) "主题色" else "Theme color"
        startBtn.text = when {
            prefs.enabled && zh -> "停止监控"
            prefs.enabled -> "Stop monitoring"
            zh -> "开始监控"
            else -> "Start monitoring"
        }
        findViewById<TextView>(R.id.titleText).text = if (zh) "护眼管家" else "EyeGuard"
        findViewById<TextView>(R.id.subtitleText).text =
            if (zh) "看屏幕久了，强制休息一下" else "Take a break before your eyes complain"

        // 学习端锁定：没解锁时，所有会影响规则的控件都点不动
        val editable = unlocked()
        intervalSeek.isEnabled = editable
        breakSeek.isEnabled = editable
        cameraSwitch.isEnabled = editable
        sceneSwitch.isEnabled = editable
        langBtn.isEnabled = true          // 语言本身有 guard
        themeBtn.isEnabled = true

        pinBtn.text = when {
            prefs.hasPin && !editable && zh -> "🔒 输入家长密码解锁"
            prefs.hasPin && !editable -> "🔒 Unlock with parent PIN"
            prefs.hasPin && zh -> "家长密码（已开启）"
            prefs.hasPin -> "Parent PIN (on)"
            zh -> "设置家长密码"
            else -> "Set parent PIN"
        }

        // 场景识别需要系统权限，没给就给出入口
        val usageOk = SceneDetector(this).hasPermission()
        usageBtn.visibility = if (prefs.smartScene && !usageOk) android.view.View.VISIBLE
        else android.view.View.GONE

        val vName = try {
            packageManager.getPackageInfo(packageName, 0).versionName
        } catch (e: Exception) {
            "1.2"
        }
        findViewById<TextView>(R.id.versionText).text =
            if (zh) "版本 $vName · 家长密码与场景识别" else "Version $vName · PIN and scene detection"
    }

    /** 把当前主题色刷到所有界面元素上 */
    private fun applyThemeColors() {
        val primary = ThemeColor.primary(this)
        val deep = ThemeColor.deep(this)
        val container = ThemeColor.container(this)
        val surface = ThemeColor.surface(this)

        findViewById<TextView>(R.id.titleText).setTextColor(deep)
        startBtn.backgroundTintList = android.content.res.ColorStateList.valueOf(primary)
        val restBtn = findViewById<Button>(R.id.restButton)
        restBtn.backgroundTintList = android.content.res.ColorStateList.valueOf(container)
        restBtn.setTextColor(deep)
        for (b in listOf(langBtn, themeBtn, pinBtn, usageBtn)) {
            b.backgroundTintList = android.content.res.ColorStateList.valueOf(surface)
            b.setTextColor(deep)
        }

        val tints = android.content.res.ColorStateList.valueOf(primary)
        intervalSeek.thumbTintList = tints
        intervalSeek.progressTintList = tints
        breakSeek.thumbTintList = tints
        breakSeek.progressTintList = tints
        cameraSwitch.thumbTintList = tints
        sceneSwitch.thumbTintList = tints
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
        val sceneOn = prefs.smartScene && SceneDetector(this).hasPermission()
        statusView.text = when {
            prefs.isZh() && prefs.enabled && cam && sceneOn -> "运行中 · 摄像头 + 场景识别"
            prefs.isZh() && prefs.enabled && cam -> "运行中 · 摄像头监测"
            prefs.isZh() && prefs.enabled -> "运行中 · 纯计时模式（未授权摄像头）"
            prefs.isZh() -> "已停止"
            prefs.enabled && cam && sceneOn -> "Running · camera + scene"
            prefs.enabled && cam -> "Running · camera monitoring"
            prefs.enabled -> "Running · timer only (no camera permission)"
            else -> "Stopped"
        }
        statusView.setTextColor(if (prefs.enabled) ThemeColor.deep(this) else Color.parseColor("#5C7A6E"))
    }

    private abstract class SimpleSeek : SeekBar.OnSeekBarChangeListener {
        override fun onStartTrackingTouch(sb: SeekBar?) {}
        override fun onStopTrackingTouch(sb: SeekBar?) {}
    }
}
