import Foundation
import XCTest

@testable import CozmoCapture

final class PortableRoomPlanTests: XCTestCase {
  func testExportMatchesPortableContract() throws {
    let identity: [Float] = [
      1, 0, 0, 0,
      0, 1, 0, 0,
      0, 0, 1, 0,
      0, 0, 0, 1,
    ]
    let wall = PortableSurface(
      identifier: "wall-1",
      dimensions: [4.2, 2.5, 0.1],
      transform: identity,
      confidence: "high"
    )
    let room = PortableRoom(
      identifier: "room-1",
      label: "Captured room",
      walls: [wall, wall, wall],
      doors: [],
      windows: [],
      openings: []
    )

    let data = try RoomPlanExporter.encoded(PortableRoomPlan(rooms: [room]))
    let object = try XCTUnwrap(JSONSerialization.jsonObject(with: data) as? [String: Any])
    let coordinateSystem = try XCTUnwrap(object["coordinateSystem"] as? [String: Any])
    let rooms = try XCTUnwrap(object["rooms"] as? [[String: Any]])
    let walls = try XCTUnwrap(rooms.first?["walls"] as? [[String: Any]])

    XCTAssertEqual(object["format"] as? String, "roomplan-json-v1")
    XCTAssertEqual(coordinateSystem["units"] as? String, "m")
    XCTAssertEqual(coordinateSystem["transformLayout"] as? String, "column-major")
    XCTAssertEqual(walls.first?["dimensions"] as? [Double], [4.2, 2.5, 0.1])
    XCTAssertEqual(walls.first?["transform"] as? [Int], identity.map(Int.init))
  }
}
