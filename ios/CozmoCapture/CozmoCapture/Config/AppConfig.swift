import Foundation

enum AppConfig {
  static let exportDirectoryName = "CozmoCapture"
  static let exportFileName = "roomplan.json"
  static let manifestFileName = "manifest.yaml"
  static let lidarDirectoryName = "lidar"
  static let jobIdPrefix = "cozmo-capture"
  static let marketingVersion = "0.1.0"
  static let captureToolName = "Cozmo Capture"
  static let portableFormat = "roomplan-json-v1"
  static let captureFormat = "roomplan-json-v1+record3d-r3d"
  static let jobNotes =
    "Route 1 Cozmo Capture export. RoomPlan JSON is the wall source; .r3d files are raw ARKit RGB-D."
  static let lidarSampleInterval: TimeInterval = 0.5
  static let lidarMaxFramesPerRoom = 90
  static let lidarJPEGQuality: CGFloat = 0.8
  static let record3DSource = "cozmo-capture-arkit"

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

  static func archiveFileName(for label: String, used: [String]) -> String {
    let slug = label.lowercased()
      .split(whereSeparator: { !$0.isLetter && !$0.isNumber })
      .joined(separator: "-")
    let base = slug.isEmpty ? "room" : slug
    var name = "\(base).r3d"
    var suffix = 2
    while used.contains(name) {
      name = "\(base)-\(suffix).r3d"
      suffix += 1
    }
    return name
  }
}
