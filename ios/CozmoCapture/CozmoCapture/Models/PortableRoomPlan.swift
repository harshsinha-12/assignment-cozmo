import Foundation

struct PortableRoomPlan: Codable, Equatable {
  let format: String
  let coordinateSystem: CoordinateSystem
  let rooms: [PortableRoom]

  init(rooms: [PortableRoom]) {
    format = AppConfig.portableFormat
    coordinateSystem = CoordinateSystem()
    self.rooms = rooms
  }
}

struct CoordinateSystem: Codable, Equatable {
  let units: String
  let upAxis: String
  let floorAxes: [String]
  let transformLayout: String

  init(
    units: String = "m",
    upAxis: String = "y",
    floorAxes: [String] = ["x", "z"],
    transformLayout: String = "column-major"
  ) {
    self.units = units
    self.upAxis = upAxis
    self.floorAxes = floorAxes
    self.transformLayout = transformLayout
  }
}

struct PortableRoom: Codable, Equatable {
  let identifier: String
  let label: String
  let walls: [PortableSurface]
  let doors: [PortableSurface]
  let windows: [PortableSurface]
  let openings: [PortableSurface]
}

struct PortableSurface: Codable, Equatable {
  let identifier: String
  let dimensions: [Float]
  let transform: [Float]
  let confidence: String
  let wallIdentifier: String?

  init(
    identifier: String,
    dimensions: [Float],
    transform: [Float],
    confidence: String,
    wallIdentifier: String? = nil
  ) {
    self.identifier = identifier
    self.dimensions = dimensions
    self.transform = transform
    self.confidence = confidence
    self.wallIdentifier = wallIdentifier
  }
}
