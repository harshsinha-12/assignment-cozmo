import Foundation

enum CaptureJobManifest {
  static func yaml(
    jobId: String,
    tier: String,
    device: String,
    captureFormat: String,
    rooms: [String],
    filesKey: String,
    files: [String],
    notes: String
  ) -> String {
    var lines = [
      "job_id: \(quote(jobId))",
      "tier: \(tier)",
      "device: \(quote(device))",
      "capture_tool: \(quote("\(AppConfig.captureToolName) \(AppConfig.marketingVersion)"))",
      "capture_format: \(quote(captureFormat))",
      "rooms:",
    ]
    for room in rooms {
      lines.append("  - \(quote(room))")
    }
    lines.append("\(filesKey):")
    for file in files {
      lines.append("  - \(quote(file))")
    }
    lines.append("notes: \(quote(notes))")
    return lines.joined(separator: "\n") + "\n"
  }

  static func quote(_ value: String) -> String {
    let escaped = value
      .replacingOccurrences(of: "\\", with: "\\\\")
      .replacingOccurrences(of: "\"", with: "\\\"")
    return "\"\(escaped)\""
  }
}
