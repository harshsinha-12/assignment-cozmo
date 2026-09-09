import Foundation

enum RoomAssociation {
  static func annotate(_ rooms: [PortableRoom]) -> [PortableRoom] {
    let wallRooms = occupancy(
      rooms.flatMap { room in
        room.walls.map { ($0.identifier, room.identifier) }
      })
    let openingRooms = occupancy(
      rooms.flatMap { room in
        (room.doors + room.windows + room.openings).map { ($0.identifier, room.identifier) }
      })

    return rooms.map { room in
      PortableRoom(
        identifier: room.identifier,
        label: room.label,
        walls: room.walls.map { wall in
          let ids = wallRooms[wall.identifier] ?? [room.identifier]
          return wall.annotated(roomIds: ids.count >= 2 ? ids : nil)
        },
        doors: room.doors.map { opening in
          annotateOpening(
            opening, roomId: room.identifier, wallRooms: wallRooms, openingRooms: openingRooms)
        },
        windows: room.windows.map { opening in
          annotateOpening(
            opening, roomId: room.identifier, wallRooms: wallRooms, openingRooms: openingRooms)
        },
        openings: room.openings.map { opening in
          annotateOpening(
            opening, roomId: room.identifier, wallRooms: wallRooms, openingRooms: openingRooms)
        }
      )
    }
  }

  private static func annotateOpening(
    _ opening: PortableSurface,
    roomId: String,
    wallRooms: [String: [String]],
    openingRooms: [String: [String]]
  ) -> PortableSurface {
    var connected: [String] = []
    if let wallId = opening.wallIdentifier {
      connected.append(contentsOf: wallRooms[wallId] ?? [])
    }
    connected.append(contentsOf: openingRooms[opening.identifier] ?? [roomId])
    let unique = uniqued(connected)
    return opening.annotated(connectsRoomIds: unique.count >= 2 ? unique : nil)
  }

  private static func occupancy(_ pairs: [(String, String)]) -> [String: [String]] {
    var roomsBySurface: [String: [String]] = [:]
    for (surfaceId, roomId) in pairs {
      roomsBySurface[surfaceId, default: []].append(roomId)
    }
    return roomsBySurface.mapValues(uniqued)
  }

  private static func uniqued(_ values: [String]) -> [String] {
    var seen = Set<String>()
    return values.filter { seen.insert($0).inserted }
  }
}
