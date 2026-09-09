import RoomPlan

enum StructureMerger {
  static func alignedRooms(
    from sessionRooms: [CapturedSessionRoom]
  ) async throws -> [(capturedRoom: CapturedRoom, label: String)] {
    let captured = sessionRooms.map(\.capturedRoom)
    let labels = sessionRooms.map(\.label)
    guard captured.count >= 2 else {
      return Array(zip(captured, labels))
    }

    let merged = try await StructureBuilder(options: []).capturedStructure(from: captured).rooms
    let labelsByIdentifier = Dictionary(
      uniqueKeysWithValues: zip(captured.map(\.identifier), labels)
    )
    return merged.enumerated().map { index, room in
      let fallback = index < labels.count ? labels[index] : AppConfig.defaultLabel(forIndex: index)
      return (room, labelsByIdentifier[room.identifier] ?? fallback)
    }
  }
}
