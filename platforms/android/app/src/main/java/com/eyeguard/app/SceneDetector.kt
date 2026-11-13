package com.eyeguard.app

import android.app.usage.UsageEvents
import android.app.usage.UsageStatsManager
import android.content.Context
import android.content.pm.PackageManager

/**
 * 场景识别（对应桌面版的 classify_scene）：
 * 看当前前台应用是什么——学习类、娱乐类，还是普通应用。
 *
 * 手机上没有「全屏窗口」这个概念可用，改成读系统的使用情况统计（UsageStats）。
 * 需要用户在系统设置里授权「使用情况访问权限」，没授权就自动退回普通计时。
 */
class SceneDetector(private val ctx: Context) {

    companion object {
        const val STUDY = "study"
        const val ENT = "ent"
        const val NORMAL = "normal"

        /** 包名直接命中（比 label 可靠） */
        private val STUDY_PKG = listOf(
            "cn.xuexi.android",             // 学习强国
            "com.tencent.weread",           // 微信读书
            "com.chaoxing.mobile",          // 学习通
            "com.baidu.homework",           // 作业帮
            "com.zuoyebang.airclass",       // 作业帮直播课
            "com.yuanfudao.android",        // 猿辅导
            "com.jiongji.andriod.card",     // 百词斩
            "com.shanghaiyue.power",        // 知到
            "com.zhihuishu.app",            // 智慧树
            "com.netease.edu.ucmooc",       // 中国大学 MOOC
            "com.duolingo",                 // Duolingo
            "com.ankidroid"                 // AnkiDroid
        )

        private val ENT_PKG = listOf(
            "tv.danmaku.bili",              // 哔哩哔哩
            "com.ss.android.ugc.aweme",     // 抖音
            "com.ss.android.ugc.aweme.lite",
            "com.smile.gifmaker",           // 快手
            "com.qiyi.video",               // 爱奇艺
            "com.tencent.qqlive",           // 腾讯视频
            "com.youku.phone",              // 优酷
            "com.hunantv.imgo.activity",    // 芒果 TV
            "com.google.android.youtube",
            "com.netflix.mediaclient",
            "com.ss.android.article.video", // 西瓜视频
            "com.xingin.xhs",               // 小红书
            "com.tencent.weishi",           // 微视
            "com.kuaishou.nebula"
        )

        private val STUDY_KW = listOf(
            "学习", "课堂", "网课", "作业", "题库", "单词", "词典", "读书", "公开课",
            "慕课", "mooc", "知到", "智慧树", "背单词", "学而思", "洋葱", "猿辅导",
            "study", "learn", "course", "class", "school", "homework", "exam", "tutor"
        )

        private val ENT_KW = listOf(
            "哔哩", "bilibili", "抖音", "快手", "视频", "影视", "电影", "综艺", "直播",
            "游戏", "爱奇艺", "优酷", "芒果", "netflix", "youtube",
            "video", "movie", "game", "stream"
        )
    }

    private val usm = ctx.getSystemService(Context.USAGE_STATS_SERVICE) as UsageStatsManager

    /** 系统里是否拿到了使用情况访问权限 */
    fun hasPermission(): Boolean = try {
        val now = System.currentTimeMillis()
        !usm.queryUsageStats(UsageStatsManager.INTERVAL_DAILY, now - 60_000, now).isNullOrEmpty()
    } catch (e: Exception) {
        false
    }

    /** 最近一个切到前台的应用包名 */
    fun foreground(): String? {
        val now = System.currentTimeMillis()
        return try {
            val events = usm.queryEvents(now - 20_000, now) ?: return null
            val e = UsageEvents.Event()
            var last: String? = null
            var lastTs = 0L
            while (events.hasNextEvent()) {
                events.getNextEvent(e)
                if (e.eventType == UsageEvents.Event.MOVE_TO_FOREGROUND && e.timeStamp >= lastTs) {
                    lastTs = e.timeStamp
                    last = e.packageName
                }
            }
            last
        } catch (ex: Exception) {
            null
        }
    }

    fun classify(pkg: String?): String {
        if (pkg.isNullOrBlank() || pkg == ctx.packageName) return NORMAL
        if (STUDY_PKG.any { it.equals(pkg, true) }) return STUDY
        if (ENT_PKG.any { it.equals(pkg, true) }) return ENT
        val hay = (pkg + " " + labelOf(pkg)).lowercase()
        if (STUDY_KW.any { hay.contains(it) }) return STUDY
        if (ENT_KW.any { hay.contains(it) }) return ENT
        return NORMAL
    }

    private fun labelOf(pkg: String): String = try {
        val pm = ctx.packageManager
        pm.getApplicationLabel(pm.getApplicationInfo(pkg, 0)).toString()
    } catch (e: PackageManager.NameNotFoundException) {
        ""
    } catch (e: Exception) {
        ""
    }
}
