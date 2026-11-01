package com.eyeguard.app

import android.content.BroadcastReceiver
import android.content.Context
import android.content.Intent

/**
 * 开机自启：开机后若用户开启过监控，自动拉起前台服务
 */
class BootReceiver : BroadcastReceiver() {
    override fun onReceive(context: Context, intent: Intent) {
        val action = intent.action ?: return
        if (action != Intent.ACTION_BOOT_COMPLETED &&
            action != Intent.ACTION_MY_PACKAGE_REPLACED
        ) return
        val prefs = Prefs(context)
        if (!prefs.enabled) return
        try {
            MonitorService.start(context)
        } catch (_: Exception) {
        }
    }
}
