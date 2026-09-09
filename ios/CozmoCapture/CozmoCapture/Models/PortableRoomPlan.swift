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

struct PortableSurface: Equatable {
  let identifier: String
  let dimensions: [Float]
  let transform: [Float]
  let confidence: String
  let wallIdentifier: String?
  let roomIds: [String]?
  let connectsRoomIds: [String]?

  init(
    identifier: String,
    dimensions: [Float],
    transform: [Float],
    confidence: String,
    wallIdentifier: String? = nil,
    roomIds: [String]? = nil,
    connectsRoomIds: [String]? = nil
  ) {
    self.identifier = identifier
    self.dimensions = dimensions
    self.transform = transform
    self.confidence = confidence
    self.wallIdentifier = Self.nonEmpty(wallIdentifier)
    self.roomIds = Self.nonEmpty(roomIds)
    self.connectsRoomIds = Self.nonEmpty(connectsRoomIds)
  }

  func annotated(
    wallIdentifier: String? = nil,
    roomIds: [String]? = nil,
    connectsRoomIds: [String]? = nil
  ) -> PortableSurface {
    PortableSurface(
      identifier: identifier,
      dimensions: dimensions,
      transform: transform,
      confidence: confidence,
      wallIdentifier: wallIdentifier ?? self.wallIdentifier,
      roomIds: roomIds ?? self.roomIds,
      connectsRoomIds: connectsRoomIds ?? self.connectsRoomIds
    )
  }

  private static func nonEmpty(_ value: String?) -> String? {
    guard let value, !value.isEmpty else { return nil }
    return value
  }

  private static func nonEmpty(_ values: [String]?) -> [String]? {
    guard let values, !values.isEmpty else { return nil }
    return values
  }
}

extension PortableSurface: Codable {
  enum CodingKeys: String, CodingKey {
    case identifier
    case dimensions
    case transform
    case confidence
    case wallIdentifier
    case roomIds
    case connectsRoomIds
  }

  func encode(to encoder: Encoder) throws {
    var container = encoder.container(keyedBy: CodingKeys.self)
    try container.encode(identifier, forKey: .identifier)
    try container.encode(dimensions, forKey: .dimensions)
    try container.encode(transform, forKey: .transform)
    try container.encode(confidence, forKey: .confidence)
    try container.encodeIfPresent(wallIdentifier, forKey: .wallIdentifier)
    try container.encodeIfPresent(roomIds, forKey: .roomIds)
    try container.encodeIfPresent(connectsRoomIds, forKey: .connectsRoomIds)
  }

  init(from decoder: Decoder) throws {
    let container = try decoder.container(keyedBy: CodingKeys.self)
    identifier = try container.decode(String.self, forKey: .identifier)
    dimensions = try container.decode([Float].self, forKey: .dimensions)
    transform = try container.decode([Float].self, forKey: .transform)
    confidence = try container.decode(String.self, forKey: .confidence)
    wallIdentifier = try container.decodeIfPresent(String.self, forKey: .wallIdentifier)
    roomIds = try container.decodeIfPresent([String].self, forKey: .roomIds)
    connectsRoomIds = try container.decodeIfPresent([String].self, forKey: .connectsRoomIds)
  }
}
