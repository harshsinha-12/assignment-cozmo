import Foundation
import RoomPlan

@MainActor
final class RoomCaptureStore: ObservableObject {
  @Published private(set) var state: CaptureState = .ready
  @Published private(set) var sessionRooms: [CapturedSessionRoom] = []
  @Published private(set) var exportURLs: [URL] = []
  @Published private(set) var lidarFrameCount = 0
  @Published var draftLabel: String = AppConfig.defaultLabel(forIndex: 0)

  private var session: RoomCaptureSession?
  private let lidarRecorder = ARKitLiDARRecorder()
  private var pendingRecording: RawLiDARRecording?

  var exportURL: URL? { exportURLs.first }

  init() {
    lidarRecorder.onFrameCountChange = { [weak self] count in
      self?.lidarFrameCount = count
    }
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
    exportURLs = []
    pendingRecording = nil
    lidarFrameCount = 0
    state = .capturing
    session?.run(configuration: RoomCaptureSession.Configuration())
    if let arSession = session?.arSession {
      lidarRecorder.start(session: arSession)
    }
  }

  func stop() {
    guard state == .capturing else { return }
    pendingRecording = lidarRecorder.finish()
    lidarFrameCount = pendingRecording?.frames.count ?? 0
    state = .processing
    session?.stop()
  }

  func reset() {
    guard canStart else { return }
    _ = lidarRecorder.finish()
    sessionRooms = []
    exportURLs = []
    pendingRecording = nil
    lidarFrameCount = 0
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
    sessionRooms.append(
      CapturedSessionRoom(
        label: label,
        capturedRoom: room,
        lidarRecording: pendingRecording
      )
    )
    pendingRecording = nil
    draftLabel = AppConfig.defaultLabel(forIndex: sessionRooms.count)
    exportURLs = []
    lidarFrameCount = 0
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
      let package = try JobPackageBuilder.writeToDocuments(
        plan: plan,
        recordings: sessionRooms.map { ($0.label, $0.lidarRecording) }
      )
      exportURLs = [package.zipURL]
      state = .exported
    } catch {
      state = .failed("Could not write the capture job: \(error.localizedDescription)")
    }
  }
}
