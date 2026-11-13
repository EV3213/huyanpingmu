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

    // ---------- 1.2：场景识别 ----------

    /** 识别前台应用：学习软件不打断、娱乐内容缩短到 entertainmentMin */
    var smartScene: Boolean
        get() = sp.getBoolean("smart_scene", true)
        set(v) = sp.edit().putBoolean("smart_scene", v).apply()

    var entertainmentMin: Int
        get() = sp.getInt("entertainment_min", 25)
        set(v) = sp.edit().putInt("entertainment_min", v.coerceIn(5, 120)).apply()

    /** 学习软件一直开着时的兜底：超过这么多分钟也要歇一次，0 = 不限 */
    var studyMaxWaitMin: Int
        get() = sp.getInt("study_max_wait_min", 60)
        set(v) = sp.edit().putInt("study_max_wait_min", v.coerceIn(0, 240)).apply()

    // ---------- 1.2：家长密码 ----------

    val pinHash: String get() = sp.getString("pin_hash", "") ?: ""
    val pinSalt: String get() = sp.getString("pin_salt", "") ?: ""
    val hasPin: Boolean get() = pinHash.isNotEmpty()

    fun setPin(pin: String) {
        val salt = Pin.makeSalt()
        sp.edit()
            .putString("pin_salt", salt)
            .putString("pin_hash", Pin.hash(pin, salt))
            .apply()
    }

    fun clearPin() {
        sp.edit().remove("pin_salt").remove("pin_hash").apply()
    }

    fun checkPin(pin: String): Boolean = hasPin && Pin.hash(pin, pinSalt) == pinHash

    fun isZh(): Boolean = lang != "en"

    fun tr(zh: String, en: String): String = if (isZh()) zh else en
}
