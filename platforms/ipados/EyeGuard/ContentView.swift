import SwiftUI

struct ContentView: View {
    @EnvironmentObject var monitor: Monitor
    @AppStorage(Settings.intervalKey) private var intervalMin: Int = 30
    @AppStorage(Settings.breakKey) private var breakSec: Int = 20
    @AppStorage(Settings.cameraKey) private var useCamera: Bool = true
    @AppStorage(Settings.langKey) private var lang: String = "zh"

    private var zh: Bool { lang != "en" }

    var body: some View {
        ScrollView {
            VStack(alignment: .leading, spacing: 18) {
                header
                settingsCard
                statusRow
                actionButtons
                Text(L.t(L.privacy))
                    .font(.footnote)
                    .foregroundStyle(.secondary)
                    .padding(.top, 4)
            }
            .padding(40)
            .frame(maxWidth: 820, alignment: .leading)
            .frame(maxWidth: .infinity)
        }
        .background(Color(red: 0.96, green: 0.98, blue: 0.97).ignoresSafeArea())
        .fullScreenCover(isPresented: $monitor.showBreak) {
            BreakView()
        }
        .onChange(of: lang) { _, _ in
            // 语言切换后刷新界面文案（AppStorage 驱动）
        }
    }

    private var header: some View {
        VStack(alignment: .leading, spacing: 6) {
            Text(L.t(L.app))
                .font(.system(size: 38, weight: .bold))
                .foregroundStyle(Color(red: 0.07, green: 0.39, blue: 0.29))
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
            }

            VStack(alignment: .leading, spacing: 6) {
                Text(zh ? "每次休息 \(breakSec) 秒" : "Each break lasts \(breakSec) s")
                    .font(.headline)
                Slider(value: Binding(
                    get: { Double(breakSec) },
                    set: { breakSec = max(5, Int($0.rounded())) }
                ), in: 5...60, step: 1)
            }

            Toggle(isOn: $useCamera) {
                Text(L.t(L.camera)).font(.headline)
            }
        }
        .padding(20)
        .background(Color.white, in: RoundedRectangle(cornerRadius: 18, style: .continuous))
        .shadow(color: .black.opacity(0.05), radius: 10, y: 4)
    }

    private var statusRow: some View {
        HStack(spacing: 8) {
            Circle()
                .fill(monitor.isRunning ? Color(red: 0.07, green: 0.55, blue: 0.38)
                                        : Color.gray.opacity(0.4))
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
            .background(Color(red: 0.07, green: 0.39, blue: 0.29))
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
            .background(Color(red: 0.86, green: 0.94, blue: 0.90))
            .foregroundStyle(Color(red: 0.07, green: 0.39, blue: 0.29))
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
            .background(Color(red: 0.93, green: 0.96, blue: 0.95))
            .foregroundStyle(Color(red: 0.07, green: 0.39, blue: 0.29))
            .clipShape(RoundedRectangle(cornerRadius: 14, style: .continuous))
        }
    }
}

#Preview {
    ContentView().environmentObject(Monitor())
}
