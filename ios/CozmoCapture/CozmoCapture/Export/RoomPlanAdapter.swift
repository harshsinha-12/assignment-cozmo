import RoomPlan
import simd

enum RoomPlanAdapter {
  static func portablePlan(
    from rooms: [(capturedRoom: CapturedRoom, label: String)]
  ) -> PortableRoomPlan {
    let portableRooms = rooms.map { room, label in
      portableRoom(from: room, identifier: room.identifier.uuidString, label: label)
    }
    return PortableRoomPlan(rooms: RoomAssociation.annotate(portableRooms))
  }

  static func portableRoom(
    from capturedRoom: CapturedRoom,
    identifier: String,
    label: String
  ) -> PortableRoom {
    PortableRoom(
      identifier: identifier,
      label: label,
      walls: capturedRoom.walls.map(portableSurface),
      doors: capturedRoom.doors.map(portableSurface),
      windows: capturedRoom.windows.map(portableSurface),
      openings: capturedRoom.openings.map(portableSurface)
    )
  }

  private static func portableSurface(_ surface: CapturedRoom.Surface) -> PortableSurface {
    PortableSurface(
      identifier: surface.identifier.uuidString,
      dimensions: [surface.dimensions.x, surface.dimensions.y, surface.dimensions.z],
      transform: columnMajorValues(surface.transform),
      confidence: confidenceName(surface.confidence),
      wallIdentifier: surface.parentIdentifier?.uuidString
    )
  }

  private static func columnMajorValues(_ matrix: simd_float4x4) -> [Float] {
    [matrix.columns.0, matrix.columns.1, matrix.columns.2, matrix.columns.3]
      .flatMap { [$0.x, $0.y, $0.z, $0.w] }
  }

  private static func confidenceName(_ confidence: CapturedRoom.Confidence) -> String {
    switch confidence {
    case .high: "high"
    case .medium: "medium"
    case .low: "low"
    @unknown default: "medium"
    }
  }
}
