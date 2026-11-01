import SwiftUI
import AVFoundation
import AVKit

/// 全屏休息页：绿植视频背景（如已加入 Resources）+ 倒计时 + 神经语音
struct BreakView: View {
    @Environment(\.dismiss) private var dismiss
    @State private var left: Int
    @State private var done = false
    @State private var player: AVQueuePlayer?
    @State private var looper: AVPlayerLooper?
    @State private var timer: Timer?
    private let total: Int
    private let speech = AVSpeechSynthesizer()

    init() {
        let seconds = Settings.breakSec
        self.total = seconds
        _left = State(initialValue: seconds)
    }

    var body: some View {
        ZStack {
            background
            Color.black.opacity(player == nil ? 0.28 : 0.34)

            VStack(spacing: 18) {
                Spacer()
                Text(L.t(L.breakTitle))
                    .font(.system(size: 40, weight: .bold))
                    .foregroundStyle(.white)

                Text(L.t(L.breakTip))
                    .multilineTextAlignment(.center)
                    .lineSpacing(6)
                    .foregroundStyle(Color.white.opacity(0.85))

                if done {
                    Text(L.t(L.breakDone))
                        .font(.system(size: 22, weight: .bold))
                        .foregroundStyle(Color(uiColor: ThemeColor.mix(ThemeColor.primary, .white, 0.55)))
                        .padding(.top, 16)
                } else {
                    Text(L.t(L.breakCount) + "\(left)" + L.t(L.breakSeconds))
                        .font(.system(size: 20))
                        .foregroundStyle(Color(uiColor: ThemeColor.mix(ThemeColor.primary, .white, 0.62)))
                        .padding(.top, 16)
                }
                Spacer()
            }
            .padding(32)
        }
        .ignoresSafeArea()
        .statusBarHidden(true)
        .onAppear(perform: begin)
        .onDisappear { timer?.invalidate() }
    }

    @ViewBuilder
    private var background: some View {
        if let player {
            VideoPlayer(player: player)
                .disabled(true)
                .ignoresSafeArea()
        } else {
            LinearGradient(
                colors: [Color(uiColor: ThemeColor.shade(ThemeColor.primary, 0.45)),
                         Color(uiColor: ThemeColor.shade(ThemeColor.primary, 0.85))],
                startPoint: .topLeading, endPoint: .bottomTrailing
            )
            .ignoresSafeArea()
        }
    }

    private func begin() {
        startVideoIfAvailable()
        speak(L.t(L.speakRest))
        timer = Timer.scheduledTimer(withTimeInterval: 1, repeats: true) { t in
            if left > 1 {
                left -= 1
                if left == total / 2 { speak(L.t(L.speakMid)) }
            } else {
                t.invalidate()
                done = true
                speak(L.t(L.speakDone))
                DispatchQueue.main.asyncAfter(deadline: .now() + 2.2) {
                    player?.pause()
                    dismiss()
                }
            }
        }
    }

    private func startVideoIfAvailable() {
        for name in ["rest-aerial", "rest-plant"] {
            guard let url = Bundle.main.url(forResource: name, withExtension: "mp4") else { continue }
            let item = AVPlayerItem(url: url)
            let qp = AVQueuePlayer(playerItem: item)
            qp.isMuted = true
            looper = AVPlayerLooper(player: qp, templateItem: item)
            player = qp
            qp.play()
            return
        }
    }

    private func speak(_ text: String) {
        let u = AVSpeechUtterance(string: text)
        u.voice = AVSpeechSynthesisVoice(language: Settings.isZh ? "zh-CN" : "en-US")
        u.rate = 0.46
        u.pitchMultiplier = 1.02
        speech.speak(u)
    }
}
