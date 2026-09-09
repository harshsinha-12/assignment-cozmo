enum CaptureState: Equatable {
  case unsupported
  case ready
  case capturing
  case processing
  case exported
  case failed(String)

  var title: String {
    switch self {
    case .unsupported: "RoomPlan unavailable"
    case .ready: "Ready"
    case .capturing: "Scanning"
    case .processing: "Building room"
    case .exported: "Export ready"
    case .failed: "Capture failed"
    }
  }

  var message: String {
    switch self {
    case .unsupported:
      "Use a LiDAR-equipped Pro iPhone for this capture route."
    case .ready:
      "Start at the doorway, then slowly show every wall and opening."
    case .capturing:
      "Move slowly and keep the phone pointed at walls from chest height."
    case .processing:
      "RoomPlan is converting the scan into metric surfaces."
    case .exported:
      "Share roomplan.json into the job's lidar folder."
    case .failed(let message):
      message
    }
  }
}
