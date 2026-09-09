import Foundation
import XCTest

@testable import CozmoCapture

final class PortableRoomPlanTests: XCTestCase {
  private let identity: [Float] = [
    1, 0, 0, 0,
    0, 1, 0, 0,
    0, 0, 1, 0,
    0, 0, 0, 1,
  ]

  func testExportMatchesPortableContract() throws {
    let wall = surface("wall-1", dimensions: [4.2, 2.5, 0.1])
    let room = PortableRoom(
      identifier: "room-1",
      label: "Captured room",
      walls: [wall, wall, wall],
      doors: [],
      windows: [],
      openings: []
    )

    let object = try jsonObject(from: PortableRoomPlan(rooms: [room]))
    let coordinateSystem = try XCTUnwrap(object["coordinateSystem"] as? [String: Any])
    let rooms = try XCTUnwrap(object["rooms"] as? [[String: Any]])
    let walls = try XCTUnwrap(rooms.first?["walls"] as? [[String: Any]])

    XCTAssertEqual(object["format"] as? String, "roomplan-json-v1")
    XCTAssertEqual(coordinateSystem["units"] as? String, "m")
    XCTAssertEqual(coordinateSystem["transformLayout"] as? String, "column-major")
    XCTAssertEqual(walls.first?["dimensions"] as? [Double], [4.2, 2.5, 0.1])
    XCTAssertEqual(walls.first?["transform"] as? [Int], identity.map(Int.init))
    XCTAssertNil(walls.first?["wallIdentifier"])
    XCTAssertNil(walls.first?["roomIds"])
  }

  func testMultiRoomExportPreservesLabelsAndRoomsArray() throws {
    let plan = PortableRoomPlan(rooms: [
      room("room_a", label: "Kitchen", walls: ["a_south", "a_east", "a_north"]),
      room("room_b", label: "Hall", walls: ["b_south", "b_east", "b_north"]),
    ])

    let object = try jsonObject(from: plan)
    let rooms = try XCTUnwrap(object["rooms"] as? [[String: Any]])
    XCTAssertEqual(rooms.map { $0["identifier"] as? String }, ["room_a", "room_b"])
    XCTAssertEqual(rooms.map { $0["label"] as? String }, ["Kitchen", "Hall"])
  }

  func testAssociationAnnotatesSharedWallsAndConnectingDoors() throws {
    let sharedWall = surface("shared_wall", roomIds: nil)
    let exclusiveA = surface("a_south")
    let exclusiveB = surface("b_south")
    let door = surface(
      "door_ab",
      dimensions: [0.8, 2.1, 0.1],
      wallIdentifier: "shared_wall"
    )

    let annotated = RoomAssociation.annotate([
      PortableRoom(
        identifier: "room_a",
        label: "Kitchen",
        walls: [exclusiveA, sharedWall, surface("a_north")],
        doors: [door],
        windows: [],
        openings: []
      ),
      PortableRoom(
        identifier: "room_b",
        label: "Hall",
        walls: [exclusiveB, sharedWall, surface("b_north")],
        doors: [door],
        windows: [],
        openings: []
      ),
    ])

    let kitchenWalls = Dictionary(
      uniqueKeysWithValues: annotated[0].walls.map { ($0.identifier, $0) })
    let hallWalls = Dictionary(uniqueKeysWithValues: annotated[1].walls.map { ($0.identifier, $0) })
    XCTAssertNil(kitchenWalls["a_south"]?.roomIds)
    XCTAssertEqual(kitchenWalls["shared_wall"]?.roomIds, ["room_a", "room_b"])
    XCTAssertEqual(hallWalls["shared_wall"]?.roomIds, ["room_a", "room_b"])
    XCTAssertEqual(annotated[0].doors.first?.connectsRoomIds, ["room_a", "room_b"])
    XCTAssertEqual(annotated[0].doors.first?.wallIdentifier, "shared_wall")

    let encoded = try jsonObject(from: PortableRoomPlan(rooms: annotated))
    let rooms = try XCTUnwrap(encoded["rooms"] as? [[String: Any]])
    let walls = try XCTUnwrap(rooms.first?["walls"] as? [[String: Any]])
    let shared = try XCTUnwrap(walls.first { $0["identifier"] as? String == "shared_wall" })
    XCTAssertEqual(shared["roomIds"] as? [String], ["room_a", "room_b"])
    let doors = try XCTUnwrap(rooms.first?["doors"] as? [[String: Any]])
    XCTAssertEqual(doors.first?["connectsRoomIds"] as? [String], ["room_a", "room_b"])
    XCTAssertEqual(doors.first?["wallIdentifier"] as? String, "shared_wall")
  }

  func testUniquedLabelsKeepOperatorNamesDistinct() {
    XCTAssertEqual(AppConfig.uniquedLabel(" Kitchen ", existing: []), "Kitchen")
    XCTAssertEqual(AppConfig.uniquedLabel("Kitchen", existing: ["Kitchen"]), "Kitchen 2")
    XCTAssertEqual(
      AppConfig.uniquedLabel("Kitchen", existing: ["Kitchen", "Kitchen 2"]),
      "Kitchen 3"
    )
    XCTAssertEqual(AppConfig.uniquedLabel("   ", existing: ["Room 1"]), "Room 2")
  }

  private func room(_ identifier: String, label: String, walls: [String]) -> PortableRoom {
    PortableRoom(
      identifier: identifier,
      label: label,
      walls: walls.map { surface($0) },
      doors: [],
      windows: [],
      openings: []
    )
  }

  private func surface(
    _ identifier: String,
    dimensions: [Float] = [4.2, 2.5, 0.1],
    wallIdentifier: String? = nil,
    roomIds: [String]? = nil
  ) -> PortableSurface {
    PortableSurface(
      identifier: identifier,
      dimensions: dimensions,
      transform: identity,
      confidence: "high",
      wallIdentifier: wallIdentifier,
      roomIds: roomIds
    )
  }

  private func jsonObject(from plan: PortableRoomPlan) throws -> [String: Any] {
    let data = try RoomPlanExporter.encoded(plan)
    return try XCTUnwrap(JSONSerialization.jsonObject(with: data) as? [String: Any])
  }
}
