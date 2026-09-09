import Foundation

enum AppConfig {
  static let exportDirectoryName = "CozmoCapture"
  static let exportFileName = "roomplan.json"
  static let manifestFileName = "manifest.yaml"
  static let lidarDirectoryName = "lidar"
  static let photosDirectoryName = "photos"
  static let videoDirectoryName = "video"
  static let jobIdPrefix = "cozmo-capture"
  static let marketingVersion = "0.1.0"
  static let captureToolName = "Cozmo Capture"
  static let portableFormat = "roomplan-json-v1"
  static let captureFormat = "roomplan-json-v1+record3d-r3d"
  static let photoCaptureFormat = "jpeg-stills-v1"
  static let videoCaptureFormat = "mp4-walkthrough-v1"
  static let jobNotes =
    "Route 1 Cozmo Capture export. RoomPlan JSON is the wall source; .r3d files are raw ARKit RGB-D."
  static let photoJobNotes =
    "Route 1 Cozmo Capture photo export. Exactly 2–8 JPEGs per named room folder."
  static let videoJobNotes =
    "Route 1 Cozmo Capture video export. One MP4 walkthrough per named room. Metric output still needs a calibrated pose sidecar."
  static let lidarSampleInterval: TimeInterval = 0.5
  static let lidarMaxFramesPerRoom = 90
  static let lidarJPEGQuality: CGFloat = 0.8
  static let photoJPEGQuality: CGFloat = 0.85
  static let minPhotosPerRoom = 2
  static let maxPhotosPerRoom = 8
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

  static func slug(for label: String) -> String {
    let slug = label.lowercased()
      .split(whereSeparator: { !$0.isLetter && !$0.isNumber })
      .joined(separator: "-")
    return slug.isEmpty ? "room" : slug
  }

  static func uniquedName(base: String, ext: String, used: [String]) -> String {
    var name = "\(base).\(ext)"
    var suffix = 2
    while used.contains(name) {
      name = "\(base)-\(suffix).\(ext)"
      suffix += 1
    }
    return name
  }

  static func archiveFileName(for label: String, used: [String]) -> String {
    uniquedName(base: slug(for: label), ext: "r3d", used: used)
  }

  static func folderName(for label: String, used: [String]) -> String {
    var name = slug(for: label)
    var suffix = 2
    while used.contains(name) {
      name = "\(slug(for: label))-\(suffix)"
      suffix += 1
    }
    return name
  }
}
