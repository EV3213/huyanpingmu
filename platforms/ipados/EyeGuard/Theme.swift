import SwiftUI
import UIKit

/// 主题色：10 个预设色板 + 自定义取色（与 Android / 桌面端同一套色板）。
/// 颜色以 hex 存在 UserDefaults，所有界面从这里取色。
enum ThemeColor {
    static let key = "theme_color"
    static let defaultHex = "#12644A"

    /// 预设色板：名称（中文 / English）+ hex
    static let presets: [(zh: String, en: String, hex: String)] = [
        ("森林绿", "Forest",   "#12644A"),
        ("青竹",   "Bamboo",  "#2E7D5B"),
        ("松石青", "Teal",     "#0E6B6B"),
        ("远山蓝", "Azure",    "#2A5CAA"),
        ("靛蓝",   "Indigo",   "#4B3FA8"),
        ("葡萄紫", "Grape",    "#7A3E9D"),
        ("玫瑰红", "Rose",     "#A63B63"),
        ("暖橙",   "Amber",    "#B85C1E"),
        ("琥珀黄", "Ochre",    "#A8791B"),
        ("石墨灰", "Graphite", "#3C4744"),
    ]

    // MARK: - 存取

    static var hex: String {
        get { UserDefaults.standard.string(forKey: key) ?? defaultHex }
        set { UserDefaults.standard.set(newValue, forKey: key) }
    }

    // MARK: - 颜色运算

    static func parse(_ hex: String) -> UIColor {
        var h = hex.trimmingCharacters(in: .whitespaces)
        if h.hasPrefix("#") { h.removeFirst() }
        guard h.count == 6, let v = UInt32(h, radix: 16) else {
            return parse(defaultHex)
        }
        return UIColor(red: CGFloat((v >> 16) & 0xFF) / 255,
                       green: CGFloat((v >> 8) & 0xFF) / 255,
                       blue: CGFloat(v & 0xFF) / 255, alpha: 1)
    }

    static func toHex(_ color: UIColor) -> String {
        var r: CGFloat = 0, g: CGFloat = 0, b: CGFloat = 0, a: CGFloat = 0
        color.getRed(&r, green: &g, blue: &b, alpha: &a)
        return String(format: "#%02X%02X%02X",
                      Int(r * 255), Int(g * 255), Int(b * 255))
    }

    /// 变暗 / 变亮：factor<1 变暗，>1 变亮
    static func shade(_ color: UIColor, _ factor: CGFloat) -> UIColor {
        var r: CGFloat = 0, g: CGFloat = 0, b: CGFloat = 0, a: CGFloat = 0
        color.getRed(&r, green: &g, blue: &b, alpha: &a)
        let f = min(max(factor, 0), 2)
        return UIColor(red: min(max(r * f, 0), 1),
                       green: min(max(g * f, 0), 1),
                       blue: min(max(b * f, 0), 1), alpha: a)
    }

    /// 与白色混合：keep 为保留原色比例（0..1）
    static func mix(_ color: UIColor, _ other: UIColor, _ keep: CGFloat) -> UIColor {
        var r1: CGFloat = 0, g1: CGFloat = 0, b1: CGFloat = 0, a1: CGFloat = 0
        var r2: CGFloat = 0, g2: CGFloat = 0, b2: CGFloat = 0, a2: CGFloat = 0
        color.getRed(&r1, green: &g1, blue: &b1, alpha: &a1)
        other.getRed(&r2, green: &g2, blue: &b2, alpha: &a2)
        return UIColor(red: r1 * keep + r2 * (1 - keep),
                       green: g1 * keep + g2 * (1 - keep),
                       blue: b1 * keep + b2 * (1 - keep), alpha: a1)
    }

    // MARK: - 语义色

    static var primary: UIColor { parse(hex) }
    static var color: Color { Color(primary) }
    /// 深一档（标题、强调文字）
    static var deep: Color { Color(shade(primary, 0.78)) }
    /// 容器色（次级按钮底色）
    static var container: Color { Color(mix(primary, .white, 0.88)) }
    /// 表面色（三级按钮底色）
    static var surface: Color { Color(mix(primary, .white, 0.94)) }
    /// 页面背景
    static var background: Color { Color(mix(primary, .white, 0.95)) }
}

extension Color {
    init(hex: String) {
        self.init(uiColor: ThemeColor.parse(hex))
    }
}
