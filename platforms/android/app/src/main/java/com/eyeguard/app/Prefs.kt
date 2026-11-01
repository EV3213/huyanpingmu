package com.eyeguard.app

import android.content.Context
import android.content.SharedPreferences

/**
 * 配置存取（对应桌面版的 config.json）
 */
class Prefs(context: Context) {

    private val sp: SharedPreferences =
        context.getSharedPreferences("eyeguard", Context.MODE_PRIVATE)

    var intervalMin: Int
        get() = sp.getInt("interval_min", 30)
        set(v) = sp.edit().putInt("interval_min", v.coerceIn(1, 180)).apply()

    var breakSec: Int
        get() = sp.getInt("break_sec", 20)
        set(v) = sp.edit().putInt("break_sec", v.coerceIn(5, 300)).apply()

    var useCamera: Boolean
        get() = sp.getBoolean("use_camera", true)
        set(v) = sp.edit().putBoolean("use_camera", v).apply()

    var lang: String
        get() = sp.getString("lang", "zh") ?: "zh"
        set(v) = sp.edit().putString("lang", v).apply()

    var enabled: Boolean
        get() = sp.getBoolean("enabled", false)
        set(v) = sp.edit().putBoolean("enabled", v).apply()

    fun isZh(): Boolean = lang != "en"

    fun tr(zh: String, en: String): String = if (isZh()) zh else en
}
