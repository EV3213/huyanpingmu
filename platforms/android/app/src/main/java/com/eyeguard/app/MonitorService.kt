package com.eyeguard.app

import android.app.Notification
import android.app.NotificationChannel
import android.app.NotificationManager
import android.app.PendingIntent
import android.content.Context
import android.content.Intent
import android.content.pm.PackageManager
import android.content.pm.ServiceInfo
import android.os.Build
import android.util.Log
import androidx.camera.core.CameraSelector
import androidx.camera.core.ImageAnalysis
import androidx.camera.core.ImageProxy
import androidx.camera.lifecycle.ProcessCameraProvider
import androidx.core.app.NotificationCompat
import androidx.core.content.ContextCompat
import androidx.lifecycle.LifecycleService
import androidx.lifecycle.lifecycleScope
import com.google.mlkit.vision.common.InputImage
import com.google.mlkit.vision.face.FaceDetection
import com.google.mlkit.vision.face.FaceDetectorOptions
import kotlinx.coroutines.Job
import kotlinx.coroutines.delay
import kotlinx.coroutines.isActive
import kotlinx.coroutines.launch
import java.util.concurrent.Executors
import java.util.concurrent.atomic.AtomicBoolean
import kotlin.math.max

/**
 * 常驻前台服务：摄像头人脸检测 + 计时，达到阈值弹出全屏休息页。
 * 摄像头不可用时自动降级为纯计时模式。
 */
class MonitorService : LifecycleService() {

    companion object {
        private const val TAG = "EyeGuard"
        private const val CHANNEL_ID = "eyeguard"
        private const val NOTIF_ID = 1001
        const val ACTION_START = "com.eyeguard.action.START"
        const val ACTION_STOP = "com.eyeguard.action.STOP"
        const val ACTION_REST_NOW = "com.eyeguard.action.REST_NOW"

        fun start(context: Context) {
            val i = Intent(context, MonitorService::class.java).setAction(ACTION_START)
            ContextCompat.startForegroundService(context, i)
        }

        fun stop(context: Context) {
            val i = Intent(context, MonitorService::class.java).setAction(ACTION_STOP)
            context.startService(i)
        }

        fun restNow(context: Context) {
            val i = Intent(context, MonitorService::class.java).setAction(ACTION_REST_NOW)
            context.startService(i)
        }
    }

    private lateinit var prefs: Prefs
    private val cameraOk = AtomicBoolean(false)
    private val faceSeen = AtomicBoolean(false)
    private var lastFaceAt = 0L
    private var watched = 0
    private var breaking = false
    private var timerJob: Job? = null
    private var cameraProvider: ProcessCameraProvider? = null
    private val executor = Executors.newSingleThreadExecutor()

    private val detector = FaceDetection.getClient(
        FaceDetectorOptions.Builder()
            .setPerformanceMode(FaceDetectorOptions.PERFORMANCE_MODE_FAST)
            .setMinFaceSize(0.15f)
            .build()
    )

    override fun onCreate() {
        super.onCreate()
        prefs = Prefs(this)
        createChannel()
        startForegroundCompat()
        startCameraIfPossible()
        startTimer()
    }

    override fun onStartCommand(intent: Intent?, flags: Int, startId: Int): Int {
        super.onStartCommand(intent, flags, startId)
        when (intent?.action) {
            ACTION_STOP -> {
                prefs.enabled = false
                stopCamera()
                stopSelf()
                return START_NOT_STICKY
            }
            ACTION_REST_NOW -> {
                watched = 0
                showBreak()
            }
        }
        prefs.enabled = true
        return START_STICKY
    }

    // ---------- 通知 / 前台 ----------
    private fun createChannel() {
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) {
            val nm = getSystemService(NotificationManager::class.java)
            val ch = NotificationChannel(
                CHANNEL_ID,
                prefs.tr("护眼管家", "EyeGuard"),
                NotificationManager.IMPORTANCE_LOW
            ).apply { description = prefs.tr("后台护眼监控", "Background eye-care monitoring") }
            nm.createNotificationChannel(ch)
        }
    }

    private fun buildNotification(): Notification {
        val open = PendingIntent.getActivity(
            this, 0, Intent(this, MainActivity::class.java),
            PendingIntent.FLAG_IMMUTABLE or PendingIntent.FLAG_UPDATE_CURRENT
        )
        val text = if (cameraOk.get())
            prefs.tr("正在监测屏幕使用时长", "Monitoring screen time")
        else
            prefs.tr("纯计时模式（摄像头不可用）", "Timer only (camera unavailable)")
        return NotificationCompat.Builder(this, CHANNEL_ID)
            .setSmallIcon(android.R.drawable.ic_menu_view)
            .setContentTitle(prefs.tr("护眼管家", "EyeGuard"))
            .setContentText(text)
            .setOngoing(true)
            .setContentIntent(open)
            .setPriority(NotificationCompat.PRIORITY_LOW)
            .build()
    }

    private fun startForegroundCompat() {
        val n = buildNotification()
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.Q) {
            startForeground(NOTIF_ID, n, ServiceInfo.FOREGROUND_SERVICE_TYPE_CAMERA)
        } else {
            startForeground(NOTIF_ID, n)
        }
    }

    // ---------- 摄像头 ----------
    private fun startCameraIfPossible() {
        if (!prefs.useCamera) return
        val granted = ContextCompat.checkSelfPermission(this, android.Manifest.permission.CAMERA) ==
                PackageManager.PERMISSION_GRANTED
        if (!granted) {
            Log.i(TAG, "camera permission not granted, timer only")
            return
        }
        val future = ProcessCameraProvider.getInstance(this)
        future.addListener({
            try {
                val provider = future.get()
                cameraProvider = provider
                val analysis = ImageAnalysis.Builder()
                    .setBackpressureStrategy(ImageAnalysis.STRATEGY_KEEP_ONLY_LATEST)
                    .build()
                analysis.setAnalyzer(executor) { proxy -> analyze(proxy) }
                val selector = CameraSelector.Builder()
                    .requireLensFacing(CameraSelector.LENS_FACING_FRONT)
                    .build()
                provider.unbindAll()
                provider.bindToLifecycle(this, selector, analysis)
                cameraOk.set(true)
                Log.i(TAG, "camera bound")
            } catch (e: Exception) {
                cameraOk.set(false)
                Log.w(TAG, "camera failed: ${e.message}")
            }
        }, ContextCompat.getMainExecutor(this))
    }

    private fun analyze(proxy: ImageProxy) {
        val media = proxy.image
        if (media == null) {
            proxy.close()
            return
        }
        val image = InputImage.fromMediaImage(media, proxy.imageInfo.rotationDegrees)
        detector.process(image)
            .addOnSuccessListener { faces ->
                if (faces.isNotEmpty()) {
                    faceSeen.set(true)
                    lastFaceAt = System.currentTimeMillis()
                } else {
                    faceSeen.set(false)
                }
            }
            .addOnCompleteListener { proxy.close() }
    }

    private fun stopCamera() {
        try {
            cameraProvider?.unbindAll()
        } catch (_: Exception) {
        }
        cameraOk.set(false)
    }

    // ---------- 计时 ----------
    private fun startTimer() {
        timerJob?.cancel()
        timerJob = lifecycleScope.launch {
            while (isActive) {
                delay(1000)
                if (breaking) continue
                val intervalSec = max(1, prefs.intervalMin) * 60
                val watching = if (cameraOk.get()) {
                    val away = !faceSeen.get() &&
                            System.currentTimeMillis() - lastFaceAt > 10_000
                    !away
                } else true
                if (watching) {
                    watched++
                    if (watched >= intervalSec) {
                        watched = 0
                        showBreak()
                    }
                } else {
                    watched = 0
                }
            }
        }
    }

    private fun showBreak() {
        if (breaking) return
        breaking = true
        Log.i(TAG, "break triggered")
        val i = Intent(this, BreakActivity::class.java)
            .putExtra(BreakActivity.EXTRA_LANG, prefs.lang)
            .putExtra(BreakActivity.EXTRA_SECONDS, prefs.breakSec)
            .addFlags(Intent.FLAG_ACTIVITY_NEW_TASK or Intent.FLAG_ACTIVITY_CLEAR_TOP)
        startActivity(i)
        lifecycleScope.launch {
            delay((prefs.breakSec + 3) * 1000L)
            breaking = false
            Log.i(TAG, "break finished")
        }
    }

    override fun onDestroy() {
        timerJob?.cancel()
        stopCamera()
        executor.shutdown()
        super.onDestroy()
    }
}
