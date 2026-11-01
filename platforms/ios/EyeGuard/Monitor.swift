import Foundation
import UIKit
import AVFoundation
import Vision
import UserNotifications
import SwiftUI

/// 全局配置（对应桌面版的 config.json）
struct Settings {
    static let intervalKey = "interval_min"
    static let breakKey = "break_sec"
    static let cameraKey = "use_camera"
    static let langKey = "lang"

    static var intervalMin: Int {
        get { max(1, UserDefaults.standard.object(forKey: intervalKey) as? Int ?? 30) }
        set { UserDefaults.standard.set(newValue, forKey: intervalKey) }
    }
    static var breakSec: Int {
        get { max(5, UserDefaults.standard.object(forKey: breakKey) as? Int ?? 20) }
        set { UserDefaults.standard.set(newValue, forKey: breakKey) }
    }
    static var useCamera: Bool {
        get { UserDefaults.standard.object(forKey: cameraKey) as? Bool ?? true }
        set { UserDefaults.standard.set(newValue, forKey: cameraKey) }
    }
    static var lang: String {
        get { UserDefaults.standard.string(forKey: langKey) ?? "zh" }
        set { UserDefaults.standard.set(newValue, forKey: langKey) }
    }
    static var isZh: Bool { lang != "en" }
}

/// 文案（中文 / English）
struct L {
    static var zh: Bool { Settings.isZh }
    static let app = (zh: "护眼管家", en: "EyeGuard")
    static let subtitle = (zh: "看屏幕久了，强制休息一下", en: "Take a break before your eyes complain")
    static let interval = (zh: "注视 %d 分钟后休息", en: "Break after %d min of viewing")
    static let breakLen = (zh: "每次休息 %d 秒", en: "Each break lasts %d s")
    static let camera = (zh: "摄像头检测（本机处理，不上传）", en: "Camera detection (on-device, never uploaded)")
    static let start = (zh: "开始监控", en: "Start monitoring")
    static let stop = (zh: "停止监控", en: "Stop monitoring")
    static let restNow = (zh: "立即休息一次", en: "Take a break now")
    static let language = (zh: "语言：中文", en: "Language: English")
    static let runningCamera = (zh: "运行中 · 摄像头监测", en: "Running · camera monitoring")
    static let runningTimer = (zh: "运行中 · 纯计时模式", en: "Running · timer only")
    static let stopped = (zh: "已停止", en: "Stopped")
    static let privacy = (zh: "摄像头画面只在本机处理，不联网、不保存、不上传。", en: "Camera frames are processed on-device only — no network, no saving, no uploads.")
    static let breakTitle = (zh: "休息一下", en: "Take a Break")
    static let breakTip = (zh: "请离开屏幕，望向 6 米以外的远处\n多眨眼 · 伸展肩颈 · 喝口水",
                           en: "Look away from the screen at something 6 meters away\nBlink more · Stretch · Take a sip of water")
    static let breakCount = (zh: "休息倒计时 ", en: "Break ends in ")
    static let breakSeconds = (zh: " 秒", en: " s")
    static let breakDone = (zh: "✨ 休息完成，马上回到工作", en: "✨ Break finished — back to work")
    static let speakRest = (zh: "休息一下，离开屏幕，看看远处，让眼睛放松一下吧",
                            en: "Time for a break. Please look away from the screen and relax your eyes.")
    static let speakMid = (zh: "再坚持一下，记得多眨眨眼", en: "Hang in there a little longer. Remember to blink.")
    static let speakDone = (zh: "休息完成，欢迎回来", en: "Break finished. Welcome back.")
    static let notifTitle = (zh: "该让眼睛休息了", en: "Time for an eye break")
    static let notifBody = (zh: "离开屏幕 20 秒，看看远处的绿植。", en: "Look away from the screen for 20 seconds.")
    static let cameraDenied = (zh: "未获得摄像头权限，已切换为纯计时模式", en: "No camera permission — using timer only")

    static func t(_ pair: (zh: String, en: String)) -> String { zh ? pair.zh : pair.en }
    static func f(_ pair: (zh: String, en: String), _ n: Int) -> String {
        String(format: t(pair), n)
    }
}

/// 监控引擎：计时 + 摄像头人脸检测 + 触发休息
@MainActor
final class Monitor: ObservableObject {
    @Published var isRunning = false
    @Published var showBreak = false
    @Published var cameraOK = false
    @Published var watched = 0

    private var timer: Timer?
    private let camera = CameraWatcher()
    private var lastFaceAt = Date()
    private var breakActive = false

    init() {
        requestNotificationPermission()
    }

    func toggle() { isRunning ? stop() : start() }

    func start() {
        guard !isRunning else { return }
        isRunning = true
        watched = 0
        if Settings.useCamera {
            camera.start(
                onReady: { [weak self] ok in
                    Task { @MainActor in
                        guard let self else { return }
                        self.cameraOK = ok
                        if ok { self.lastFaceAt = Date() }
                    }
                },
                onFace: { [weak self] seen in
                    guard seen else { return }
                    Task { @MainActor in self?.lastFaceAt = Date() }
                }
            )
        }
        timer?.invalidate()
        timer = Timer.scheduledTimer(withTimeInterval: 1, repeats: true) { [weak self] _ in
            Task { @MainActor in self?.tick() }
        }
    }

    func stop() {
        isRunning = false
        timer?.invalidate()
        timer = nil
        camera.stop()
        cameraOK = false
    }

    private func tick() {
        guard isRunning, !breakActive else { return }
        let interval = Settings.intervalMin * 60
        var watching = true
        if cameraOK {
            watching = Date().timeIntervalSince(lastFaceAt) <= 10
        }
        if watching {
            watched += 1
            if watched >= interval {
                watched = 0
                triggerBreak()
            }
        } else {
            watched = 0
        }
    }

    func triggerBreak() {
        guard !breakActive else { return }
        breakActive = true
        showBreak = true
        let seconds = Settings.breakSec
        if UIApplication.shared.applicationState != .active {
            pushNotification()
        }
        DispatchQueue.main.asyncAfter(deadline: .now() + .seconds(seconds + 3)) {
            self.breakActive = false
        }
    }

    // MARK: - 通知（App 不在前台时提醒）
    private func requestNotificationPermission() {
        UNUserNotificationCenter.current()
            .requestAuthorization(options: [.alert, .sound]) { _, _ in }
    }

    private func pushNotification() {
        let content = UNMutableNotificationContent()
        content.title = L.t(L.notifTitle)
        content.body = L.t(L.notifBody)
        content.sound = .default
        let req = UNNotificationRequest(identifier: UUID().uuidString,
                                        content: content,
                                        trigger: nil)
        UNUserNotificationCenter.current().add(req)
    }
}

/// 前置摄像头 + Vision 人脸检测（全部本地）
final class CameraWatcher: NSObject {
    private let session = AVCaptureSession()
    private let queue = DispatchQueue(label: "eyeguard.camera")
    private var running = false
    private var onReady: ((Bool) -> Void)?
    private var onFace: ((Bool) -> Void)?
    private var lastAnalyzed = Date.distantPast

    func start(onReady: @escaping (Bool) -> Void,
               onFace: @escaping (Bool) -> Void) {
        self.onReady = onReady
        self.onFace = onFace
        AVCaptureDevice.requestAccess(for: .video) { [weak self] granted in
            guard let self, granted else {
                onReady(false)
                return
            }
            self.queue.async { self.configureAndRun() }
        }
    }

    private func configureAndRun() {
        guard !running else { return }
        session.beginConfiguration()
        session.sessionPreset = .low
        guard let device = AVCaptureDevice.default(.builtInWideAngleCamera,
                                                   for: .video,
                                                   position: .front),
              let input = try? AVCaptureDeviceInput(device: device),
              session.canAddInput(input) else {
            session.commitConfiguration()
            DispatchQueue.main.async { self.onReady?(false) }
            return
        }
        session.addInput(input)

        let output = AVCaptureVideoDataOutput()
        output.alwaysDiscardsLateVideoFrames = true
        output.setSampleBufferDelegate(self, queue: queue)
        if session.canAddOutput(output) { session.addOutput(output) }
        session.commitConfiguration()
        session.startRunning()
        running = true
        DispatchQueue.main.async { self.onReady?(true) }
    }

    func stop() {
        queue.async {
            if self.running {
                self.session.stopRunning()
                self.running = false
            }
        }
    }
}

extension CameraWatcher: AVCaptureVideoDataOutputSampleBufferDelegate {
    func captureOutput(_ output: AVCaptureOutput,
                       didOutput sampleBuffer: CMSampleBuffer,
                       from connection: AVCaptureConnection) {
        // 限制到每秒 1 帧，省电
        let now = Date()
        guard now.timeIntervalSince(lastAnalyzed) >= 1.0 else { return }
        lastAnalyzed = now

        guard let buffer = CMSampleBufferGetImageBuffer(sampleBuffer) else { return }
        let request = VNDetectFaceRectanglesRequest { [weak self] req, _ in
            guard let self else { return }
            let faces = req.results as? [VNFaceObservation] ?? []
            DispatchQueue.main.async { self.onFace?(!faces.isEmpty) }
        }
        try? VNImageRequestHandler(cvPixelBuffer: buffer, options: [:]).perform([request])
    }
}
