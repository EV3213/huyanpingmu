import SwiftUI
import UIKit

struct ContentView: View {
    @EnvironmentObject var monitor: Monitor
    @AppStorage(Settings.intervalKey) private var intervalMin: Int = 30
    @AppStorage(Settings.breakKey) private var breakSec: Int = 20
    @AppStorage(Settings.cameraKey) private var useCamera: Bool = true
    @AppStorage(Settings.langKey) private var lang: String = "zh"
    @AppStorage(ThemeColor.key) private var themeHex: String = ThemeColor.defaultHex

    private var zh: Bool { lang != "en" }

    /// 自定义取色：与预设色板共用一个 hex 存储
    private var customColor: Binding<Color> {
        Binding(
            get: { Color(hex: themeHex) },
            set: { themeHex = ThemeColor.toHex(UIColor($0)) }
        )
    }

    var body: some View {
        ScrollView {
            VStack(alignment: .leading, spacing: 18) {
                header
                settingsCard
                themeCard
                statusRow
                actionButtons
                Text(L.t(L.privacy))
                    .font(.footnote)
                    .foregroundStyle(.secondary)
                    .padding(.top, 4)
            }
            .padding(24)
            .frame(maxWidth: 620, alignment: .leading)
            .frame(maxWidth: .infinity)
        }
        .background(ThemeColor.background.ignoresSafeArea())
        .fullScreenCover(isPresented: $monitor.showBreak) {
            BreakView()
        }
    }

    private var header: some View {
        VStack(alignment: .leading, spacing: 6) {
            Text(L.t(L.app))
                .font(.system(size: 30, weight: .bold))
                .foregroundStyle(ThemeColor.deep)
            Text(L.t(L.subtitle))
                .font(.subheadline)
                .foregroundStyle(.secondary)
        }
    }

    private var settingsCard: some View {
        VStack(alignment: .leading, spacing: 20) {
            VStack(alignment: .leading, spacing: 6) {
                Text(zh ? "注视 \(intervalMin) 分钟后休息"
                        : "Break after \(intervalMin) min of viewing")
                    .font(.headline)
                Slider(value: Binding(
                    get: { Double(intervalMin) },
                    set: { intervalMin = max(1, Int($0.rounded())) }
                ), in: 1...60, step: 1)
                .tint(ThemeColor.color)
            }

            VStack(alignment: .leading, spacing: 6) {
                Text(zh ? "每次休息 \(breakSec) 秒" : "Each break lasts \(breakSec) s")
                    .font(.headline)
                Slider(value: Binding(
                    get: { Double(breakSec) },
                    set: { breakSec = max(5, Int($0.rounded())) }
                ), in: 5...60, step: 1)
                .tint(ThemeColor.color)
            }

            Toggle(isOn: $useCamera) {
                Text(L.t(L.camera)).font(.headline)
            }
            .tint(ThemeColor.color)
        }
        .padding(20)
        .background(Color.white, in: RoundedRectangle(cornerRadius: 18, style: .continuous))
        .shadow(color: .black.opacity(0.05), radius: 10, y: 4)
    }

    // MARK: - 主题色（预设色板 + 自定义取色）

    private var themeCard: some View {
        VStack(alignment: .leading, spacing: 14) {
            HStack {
                Text(zh ? "主题色" : "Theme color")
                    .font(.headline)
                Spacer()
                Text(themeHex.uppercased())
                    .font(.caption.monospaced())
                    .foregroundStyle(.secondary)
            }

            ScrollView(.horizontal, showsIndicators: false) {
                HStack(spacing: 12) {
                    ForEach(ThemeColor.presets, id: \.hex) { p in
                        Button {
                            themeHex = p.hex
                        } label: {
                            Circle()
                                .fill(Color(hex: p.hex))
                                .frame(width: 34, height: 34)
                                .overlay(
                                    Circle().strokeBorder(
                                        Color.white,
                                        lineWidth: themeHex.caseInsensitiveCompare(p.hex) == .orderedSame ? 3 : 0)
                                )
                                .overlay(
                                    Circle().strokeBorder(
                                        Color.black.opacity(0.08), lineWidth: 1)
                                )
                                .shadow(color: .black.opacity(0.08), radius: 3, y: 1)
                        }
                        .buttonStyle(.plain)
                        .accessibilityLabel(zh ? p.zh : p.en)
                    }
                }
                .padding(.vertical, 4)
            }

            HStack(spacing: 10) {
                ColorPicker(zh ? "自定义颜色" : "Custom color",
                            selection: customColor, supportsOpacity: false)
                    .font(.subheadline)
                Spacer()
                RoundedRectangle(cornerRadius: 8, style: .continuous)
                    .fill(ThemeColor.color)
                    .frame(width: 44, height: 26)
            }
        }
        .padding(20)
        .background(Color.white, in: RoundedRectangle(cornerRadius: 18, style: .continuous))
        .shadow(color: .black.opacity(0.05), radius: 10, y: 4)
    }

    private var statusRow: some View {
        HStack(spacing: 8) {
            Circle()
                .fill(monitor.isRunning ? ThemeColor.color : Color.gray.opacity(0.4))
                .frame(width: 10, height: 10)
            Text(statusText)
                .font(.subheadline)
                .foregroundStyle(.secondary)
        }
    }

    private var statusText: String {
        if !monitor.isRunning { return L.t(L.stopped) }
        return monitor.cameraOK ? L.t(L.runningCamera) : L.t(L.runningTimer)
    }

    private var actionButtons: some View {
        VStack(spacing: 12) {
            Button {
                monitor.toggle()
            } label: {
                Text(monitor.isRunning ? L.t(L.stop) : L.t(L.start))
                    .font(.headline)
                    .frame(maxWidth: .infinity)
                    .padding(.vertical, 16)
            }
            .buttonStyle(.plain)
            .background(ThemeColor.color)
            .foregroundStyle(.white)
            .clipShape(RoundedRectangle(cornerRadius: 14, style: .continuous))

            Button {
                monitor.triggerBreak()
            } label: {
                Text(L.t(L.restNow))
                    .font(.headline)
                    .frame(maxWidth: .infinity)
                    .padding(.vertical, 14)
            }
            .buttonStyle(.plain)
            .background(ThemeColor.container)
            .foregroundStyle(ThemeColor.deep)
            .clipShape(RoundedRectangle(cornerRadius: 14, style: .continuous))

            Button {
                lang = zh ? "en" : "zh"
            } label: {
                Text(L.t(L.language))
                    .font(.subheadline)
                    .frame(maxWidth: .infinity)
                    .padding(.vertical, 12)
            }
            .buttonStyle(.plain)
            .background(ThemeColor.surface)
            .foregroundStyle(ThemeColor.deep)
            .clipShape(RoundedRectangle(cornerRadius: 14, style: .continuous))
        }
    }
}

#Preview {
    ContentView().environmentObject(Monitor())
}
