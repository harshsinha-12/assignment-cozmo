import Foundation
import RoomPlan

@MainActor
final class RoomCaptureStore: ObservableObject {
  @Published private(set) var state: CaptureState = .ready
  @Published private(set) var sessionRooms: [CapturedSessionRoom] = []
  @Published private(set) var exportURL: URL?
  @Published var draftLabel: String = AppConfig.defaultLabel(forIndex: 0)

  private var session: RoomCaptureSession?

  init() {
    if !RoomCaptureSession.isSupported {
      state = .unsupported
    }
  }

  var canStart: Bool {
    switch state {
    case .ready, .exported, .failed: true
    default: false
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
    guard canStart else { return }
    exportURL = nil
    state = .capturing
    session?.run(configuration: RoomCaptureSession.Configuration())
  }

  func stop() {
    guard state == .capturing else { return }
    state = .processing
    session?.stop()
  }

  func reset() {
    guard canStart else { return }
    sessionRooms = []
    exportURL = nil
    draftLabel = AppConfig.defaultLabel(forIndex: 0)
    state = RoomCaptureSession.isSupported ? .ready : .unsupported
  }

  func exportMerged() {
    exportPlan(merge: sessionRooms.count >= 2)
  }

  func exportUnmerged() {
    exportPlan(merge: false)
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

    let label = AppConfig.uniquedLabel(draftLabel, existing: sessionRooms.map(\.label))
    sessionRooms.append(CapturedSessionRoom(label: label, capturedRoom: room))
    draftLabel = AppConfig.defaultLabel(forIndex: sessionRooms.count)
    exportURL = nil
    state = .ready
  }

  private func exportPlan(merge: Bool) {
    guard !sessionRooms.isEmpty else {
      state = .failed("Scan at least one room before exporting.")
      return
    }
    guard canStart else { return }

    if merge, sessionRooms.count >= 2 {
      state = .merging
      Task { await exportAlignedRooms() }
      return
    }

    write(RoomPlanAdapter.portablePlan(from: sessionRooms.map { ($0.capturedRoom, $0.label) }))
  }

  private func exportAlignedRooms() async {
    do {
      let aligned = try await StructureMerger.alignedRooms(from: sessionRooms)
      write(RoomPlanAdapter.portablePlan(from: aligned))
    } catch {
      state = .failed(
        "Could not merge rooms: \(error.localizedDescription). Export without merging, or scan the connecting doorway again."
      )
    }
  }

  private func write(_ plan: PortableRoomPlan) {
    do {
      exportURL = try RoomPlanExporter.write(plan)
      state = .exported
    } catch {
      state = .failed("Could not write the RoomPlan export: \(error.localizedDescription)")
    }
  }
}
