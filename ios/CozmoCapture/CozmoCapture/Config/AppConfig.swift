import Foundation

enum AppConfig {
  static let exportDirectoryName = "CozmoCapture"
  static let exportFileName = "roomplan.json"
  static let portableFormat = "roomplan-json-v1"

  static func defaultLabel(forIndex index: Int) -> String {
    "Room \(index + 1)"
  }

  static func uniquedLabel(_ label: String, existing: [String]) -> String {
    let trimmed = label.trimmingCharacters(in: .whitespacesAndNewlines)
    let base = trimmed.isEmpty ? defaultLabel(forIndex: existing.count) : trimmed
    if !existing.contains(base) {
      return base
    }
    var suffix = 2
    while existing.contains("\(base) \(suffix)") {
      suffix += 1
    }
    return "\(base) \(suffix)"
  }
}
