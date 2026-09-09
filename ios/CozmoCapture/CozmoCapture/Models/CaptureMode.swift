enum CaptureMode: String, CaseIterable, Identifiable {
  case lidar
  case photos
  case video

  var id: String { rawValue }

  var title: String {
    switch self {
    case .lidar: "LiDAR"
    case .photos: "Photos"
    case .video: "Video"
    }
  }
}
