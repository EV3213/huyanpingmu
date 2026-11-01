package com.eyeguard.app

import android.app.Activity
import android.content.Context
import android.graphics.Color
import android.graphics.drawable.GradientDrawable
import android.view.Gravity
import android.view.View
import android.view.ViewGroup
import android.widget.Button
import android.widget.LinearLayout
import android.widget.SeekBar
import android.widget.TextView
import androidx.appcompat.app.AlertDialog

/**
 * 主题色：10 个预设色板 + 自定义取色。
 * 颜色以 hex 存在 SharedPreferences，所有界面从这里取色，
 * 保证「用户选了什么色，哪里都是什么色」。
 */
object ThemeColor {

    /** 预设色板：名称（中文 / English）+ hex */
    val PRESETS = listOf(
        Triple("森林绿", "Forest", "#12644A"),
        Triple("青竹", "Bamboo", "#2E7D5B"),
        Triple("松石青", "Teal", "#0E6B6B"),
        Triple("远山蓝", "Azure", "#2A5CAA"),
        Triple("靛蓝", "Indigo", "#4B3FA8"),
        Triple("葡萄紫", "Grape", "#7A3E9D"),
        Triple("玫瑰红", "Rose", "#A63B63"),
        Triple("暖橙", "Amber", "#B85C1E"),
        Triple("琥珀黄", "Ochre", "#A8791B"),
        Triple("石墨灰", "Graphite", "#3C4744"),
    )

    const val DEFAULT = "#12644A"
    private const val KEY = "theme_color"

    // ── 存取 ─────────────────────────────────────────────────────────────

    fun getHex(ctx: Context): String =
        ctx.getSharedPreferences("eyeguard", Context.MODE_PRIVATE)
            .getString(KEY, DEFAULT) ?: DEFAULT

    fun setHex(ctx: Context, hex: String) {
        ctx.getSharedPreferences("eyeguard", Context.MODE_PRIVATE)
            .edit().putString(KEY, hex).apply()
    }

    // ── 取色 ─────────────────────────────────────────────────────────────

    /** 主色 */
    fun primary(ctx: Context): Int = parse(getHex(ctx))

    /** 深一档（标题、强调文字用） */
    fun deep(ctx: Context): Int = shade(primary(ctx), 0.78f)

    /** 容器色：主色混白 12%（次级按钮底色） */
    fun container(ctx: Context): Int = mix(primary(ctx), Color.WHITE, 0.88f)

    /** 表面色：主色混白 6%（三级按钮底色） */
    fun surface(ctx: Context): Int = mix(primary(ctx), Color.WHITE, 0.94f)

    fun parse(hex: String): Int = try {
        Color.parseColor(hex)
    } catch (_: Exception) {
        Color.parseColor(DEFAULT)
    }

    fun toHex(color: Int): String =
        String.format("#%06X", 0xFFFFFF and color)

    /** 变暗 / 变亮：factor<1 变暗，>1 变亮 */
    fun shade(color: Int, factor: Float): Int {
        val f = factor.coerceIn(0f, 2f)
        val r = (Color.red(color) * f).toInt().coerceIn(0, 255)
        val g = (Color.green(color) * f).toInt().coerceIn(0, 255)
        val b = (Color.blue(color) * f).toInt().coerceIn(0, 255)
        return Color.rgb(r, g, b)
    }

    /** 与白色混合：keep 为保留原色比例（0..1） */
    fun mix(color: Int, other: Int, keep: Float): Int = Color.rgb(
        (Color.red(color) * keep + Color.red(other) * (1 - keep)).toInt(),
        (Color.green(color) * keep + Color.green(other) * (1 - keep)).toInt(),
        (Color.blue(color) * keep + Color.blue(other) * (1 - keep)).toInt(),
    )

    /** 亮度 0..1（判断深浅以决定文字颜色） */
    fun luminance(color: Int): Float =
        (0.299f * Color.red(color) + 0.587f * Color.green(color) + 0.114f * Color.blue(color)) / 255f

    /** 圆形色块 drawable（sizePx<=0 时跟随 View 尺寸） */
    fun circleDrawable(color: Int, sizePx: Int, stroke: Int = 0, strokeColor: Int = 0): GradientDrawable =
        GradientDrawable().apply {
            shape = GradientDrawable.OVAL
            setColor(color)
            if (stroke > 0) setStroke(stroke, strokeColor)
            if (sizePx > 0) setSize(sizePx, sizePx)
        }

    // ── 取色对话框 ───────────────────────────────────────────────────────

    /**
     * 弹出主题色选择：上半部分预设色块（两行五列），下半部分 RGB 滑杆自定义。
     * 选色实时回调 onPreview，确认后回调 onPicked。
     */
    fun showPicker(activity: Activity, isZh: Boolean,
                   onPreview: (Int) -> Unit, onPicked: (String) -> Unit) {
        val ctx = activity
        val dp = ctx.resources.displayMetrics.density
        var current = primary(ctx)

        val root = LinearLayout(ctx).apply {
            orientation = LinearLayout.VERTICAL
            setPadding((20 * dp).toInt(), (12 * dp).toInt(), (20 * dp).toInt(), 0)
        }

        // ── 预设色块 ──
        val presetLabel = TextView(ctx).apply {
            text = if (isZh) "预设色板" else "Presets"
            setTextColor(Color.DKGRAY)
            textSize = 13f
        }
        root.addView(presetLabel)

        val rows = PRESETS.chunked(5)
        val swatches = mutableListOf<Pair<String, View>>()   // hex → 色块
        rows.forEach { rowColors ->
            val row = LinearLayout(ctx).apply {
                orientation = LinearLayout.HORIZONTAL
                gravity = Gravity.CENTER
            }
            rowColors.forEach { (_, _, hex) ->
                val c = parse(hex)
                fun paint(selected: Boolean) = View(ctx).apply {
                    background = circleDrawable(c, 0,
                        ((if (selected) 4f else 2f) * dp).toInt(), Color.WHITE)
                    layoutParams = LinearLayout.LayoutParams(
                        (44 * dp).toInt(), (44 * dp).toInt()).apply {
                        setMargins((8 * dp).toInt(), (10 * dp).toInt(), (8 * dp).toInt(), (10 * dp).toInt())
                    }
                    setOnClickListener {
                        current = c
                        swatches.forEach { (h, v) ->
                            v.background = circleDrawable(parse(h), 0,
                                ((if (h == hex) 4f else 2f) * dp).toInt(), Color.WHITE)
                        }
                        rSeek.progress = Color.red(c)
                        gSeek.progress = Color.green(c)
                        bSeek.progress = Color.blue(c)
                        onPreview(c)
                    }
                }
                val dot = paint(getHex(ctx) == hex)
                swatches.add(hex to dot)
                row.addView(dot)
            }
            root.addView(row)
        }

        // ── 自定义取色 ──
        val customLabel = TextView(ctx).apply {
            text = if (isZh) "自定义颜色（红 / 绿 / 蓝）" else "Custom color (R / G / B)"
            setTextColor(Color.DKGRAY)
            textSize = 13f
            setPadding(0, (14 * dp).toInt(), 0, 0)
        }
        root.addView(customLabel)

        val preview = View(ctx).apply {
            layoutParams = LinearLayout.LayoutParams(
                ViewGroup.LayoutParams.MATCH_PARENT, (36 * dp).toInt()).apply {
                topMargin = (8 * dp).toInt()
            }
            background = GradientDrawable().apply {
                cornerRadius = 10 * dp
                setColor(current)
            }
        }
        root.addView(preview)

        lateinit var rSeek: SeekBar
        lateinit var gSeek: SeekBar
        lateinit var bSeek: SeekBar
        val sliders = listOf("R", "G", "B")
        sliders.forEachIndexed { i, label ->
            val row = LinearLayout(ctx).apply {
                orientation = LinearLayout.HORIZONTAL
                gravity = Gravity.CENTER_VERTICAL
                setPadding(0, (6 * dp).toInt(), 0, 0)
            }
            row.addView(TextView(ctx).apply {
                text = label
                textSize = 13f
                layoutParams = LinearLayout.LayoutParams((24 * dp).toInt(),
                    ViewGroup.LayoutParams.WRAP_CONTENT)
            })
            val seek = SeekBar(ctx).apply {
                max = 255
                layoutParams = LinearLayout.LayoutParams(0, ViewGroup.LayoutParams.WRAP_CONTENT, 1f)
            }
            when (i) {
                0 -> { rSeek = seek; seek.progress = Color.red(current) }
                1 -> { gSeek = seek; seek.progress = Color.green(current) }
                else -> { bSeek = seek; seek.progress = Color.blue(current) }
            }
            seek.setOnSeekBarChangeListener(object : SeekBar.OnSeekBarChangeListener {
                override fun onProgressChanged(sb: SeekBar?, p: Int, fromUser: Boolean) {
                    current = Color.rgb(rSeek.progress, gSeek.progress, bSeek.progress)
                    (preview.background as GradientDrawable).setColor(current)
                    onPreview(current)
                }
                override fun onStartTrackingTouch(sb: SeekBar?) {}
                override fun onStopTrackingTouch(sb: SeekBar?) {}
            })
            row.addView(seek)
            root.addView(row)
        }

        AlertDialog.Builder(ctx)
            .setTitle(if (isZh) "主题色" else "Theme color")
            .setView(root)
            .setPositiveButton(if (isZh) "确定" else "OK") { _, _ ->
                setHex(ctx, toHex(current))
                onPicked(toHex(current))
            }
            .setNegativeButton(if (isZh) "取消" else "Cancel", null)
            .show()
    }
}
