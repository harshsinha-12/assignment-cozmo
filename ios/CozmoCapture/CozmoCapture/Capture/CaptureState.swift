enum CaptureState: Equatable {
  case unsupported
  case ready
  case capturing
  case processing
  case merging
  case exported
  case failed(String)

  var title: String {
    switch self {
    case .unsupported: "RoomPlan unavailable"
    case .ready: "Ready"
    case .capturing: "Scanning"
    case .processing: "Building room"
    case .merging: "Merging rooms"
    case .exported: "Export ready"
    case .failed: "Capture failed"
    }
  }

  var message: String {
    switch self {
    case .unsupported:
      "Use a LiDAR-equipped Pro iPhone for this capture route."
    case .ready:
      "Name the next room, scan it, then export one job ZIP for the CLI."
    case .capturing:
      "Move slowly and keep the phone pointed at walls. Raw LiDAR frames are logged in the background."
    case .processing:
      "RoomPlan is converting the scan into metric surfaces."
    case .merging:
      "StructureBuilder is aligning rooms into one metric frame."
    case .exported:
      "Share the job ZIP, unzip it, and run the CLI on that folder."
    case .failed(let message):
      message
    }
  }

  var allowsNaming: Bool {
    switch self {
    case .ready, .exported, .failed: true
    default: false
    }
  }
}
