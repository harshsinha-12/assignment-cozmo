import Foundation
import RoomPlan

struct CapturedSessionRoom: Identifiable {
  let id: String
  let label: String
  let capturedRoom: CapturedRoom

  init(label: String, capturedRoom: CapturedRoom) {
    id = capturedRoom.identifier.uuidString
    self.label = label
    self.capturedRoom = capturedRoom
  }
}
