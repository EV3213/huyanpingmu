import SwiftUI

@main
struct EyeGuardApp: App {
    @StateObject private var monitor = Monitor()

    var body: some Scene {
        WindowGroup {
            ContentView()
                .environmentObject(monitor)
        }
    }
}
