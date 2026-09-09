import Foundation
import RoomPlan

@MainActor
final class RoomCaptureStore: ObservableObject {
  @Published private(set) var state: CaptureState = .ready
  @Published private(set) var exportURL: URL?

  private var session: RoomCaptureSession?
  private var roomIdentifier = UUID().uuidString

  init() {
    if !RoomCaptureSession.isSupported {
      state = .unsupported
    }
  }

  func attach(session: RoomCaptureSession) {
    self.session = session
  }

  func start() {
    guard RoomCaptureSession.isSupported else {
      state = .unsupported
      return
    }
    roomIdentifier = UUID().uuidString
    exportURL = nil
    state = .capturing
    session?.run(configuration: RoomCaptureSession.Configuration())
  }

  func stop() {
    guard state == .capturing else { return }
    state = .processing
    session?.stop()
  }

  func didFinish(room: CapturedRoom?, error: Error?) {
    if let error {
      state = .failed(error.localizedDescription)
      return
    }
    guard let room else {
      state = .failed("RoomPlan did not return a processed room.")
      return
    }

    do {
      let portableRoom = RoomPlanAdapter.portableRoom(
        from: room,
        identifier: roomIdentifier,
        label: AppConfig.defaultRoomLabel
      )
      exportURL = try RoomPlanExporter.write(PortableRoomPlan(rooms: [portableRoom]))
      state = .exported
    } catch {
      state = .failed("Could not write the RoomPlan export: \(error.localizedDescription)")
    }
  }
}
