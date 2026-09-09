import Foundation

enum CaptureJobManifest {
  static func yaml(
    jobId: String,
    device: String,
    rooms: [String],
    lidarFiles: [String]
  ) -> String {
    var lines = [
      "job_id: \(quote(jobId))",
      "tier: lidar",
      "device: \(quote(device))",
      "capture_tool: \(quote("\(AppConfig.captureToolName) \(AppConfig.marketingVersion)"))",
      "capture_format: \(quote(AppConfig.captureFormat))",
      "rooms:",
    ]
    for room in rooms {
      lines.append("  - \(quote(room))")
    }
    lines.append("lidar_files:")
    for file in lidarFiles {
      lines.append("  - \(quote(file))")
    }
    lines.append("notes: \(quote(AppConfig.jobNotes))")
    return lines.joined(separator: "\n") + "\n"
  }

  static func quote(_ value: String) -> String {
    let escaped = value
      .replacingOccurrences(of: "\\", with: "\\\\")
      .replacingOccurrences(of: "\"", with: "\\\"")
    return "\"\(escaped)\""
  }
}
