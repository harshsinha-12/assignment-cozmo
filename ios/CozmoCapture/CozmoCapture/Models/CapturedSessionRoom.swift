import Foundation
import RoomPlan

struct CapturedSessionRoom: Identifiable {
  let id: String
  let label: String
  let capturedRoom: CapturedRoom
  let lidarRecording: RawLiDARRecording?

  init(label: String, capturedRoom: CapturedRoom, lidarRecording: RawLiDARRecording? = nil) {
    id = capturedRoom.identifier.uuidString
    self.label = label
    self.capturedRoom = capturedRoom
    self.lidarRecording = lidarRecording
  }
}
