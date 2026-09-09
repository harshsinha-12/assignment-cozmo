import AVFoundation
import Foundation

struct CapturedPhotoRoom: Identifiable {
  let id = UUID()
  let label: String
  let jpegs: [Data]
}

final class PhotoCaptureStore: NSObject, ObservableObject {
  @Published var state: CaptureState = .ready
  @Published var rooms: [CapturedPhotoRoom] = []
  @Published var pendingJPEGs: [Data] = []
  @Published var exportURLs: [URL] = []
  @Published var draftLabel: String = AppConfig.defaultLabel(forIndex: 0)

  let session = AVCaptureSession()
  private let output = AVCapturePhotoOutput()
  private let sessionQueue = DispatchQueue(label: "cozmo.photo.session")

  var canCapture: Bool {
    state == .ready && pendingJPEGs.count < AppConfig.maxPhotosPerRoom
  }

  func startSession() {
    sessionQueue.async { [weak self] in
      self?.configureIfNeeded()
      self?.session.startRunning()
    }
  }

  func stopSession() {
    sessionQueue.async { [weak self] in
      self?.session.stopRunning()
    }
  }

  func capturePhoto() {
    guard canCapture else { return }
    output.capturePhoto(with: AVCapturePhotoSettings(), delegate: self)
  }

  func finishRoom() {
    guard pendingJPEGs.count >= AppConfig.minPhotosPerRoom else {
      state = .failed("Need at least \(AppConfig.minPhotosPerRoom) photos in this room.")
      return
    }
    let label = AppConfig.uniquedLabel(draftLabel, existing: rooms.map(\.label))
    rooms.append(CapturedPhotoRoom(label: label, jpegs: pendingJPEGs))
    pendingJPEGs = []
    draftLabel = AppConfig.defaultLabel(forIndex: rooms.count)
    exportURLs = []
    state = .ready
  }

  func exportJob() {
    guard pendingJPEGs.isEmpty else {
      state = .failed("Finish or discard the current room before exporting.")
      return
    }
    guard !rooms.isEmpty else {
      state = .failed("Capture at least one room of stills before exporting.")
      return
    }
    do {
      let package = try JobPackageBuilder.writePhotosToDocuments(
        rooms: rooms.map { ($0.label, $0.jpegs) }
      )
      exportURLs = [package.zipURL]
      state = .exported
    } catch {
      state = .failed("Could not write the photo job: \(error.localizedDescription)")
    }
  }

  func reset() {
    rooms = []
    pendingJPEGs = []
    exportURLs = []
    draftLabel = AppConfig.defaultLabel(forIndex: 0)
    state = .ready
  }

  private func configureIfNeeded() {
    guard session.inputs.isEmpty else { return }
    session.beginConfiguration()
    session.sessionPreset = .photo
    guard let device = AVCaptureDevice.default(.builtInWideAngleCamera, for: .video, position: .back),
      let input = try? AVCaptureDeviceInput(device: device),
      session.canAddInput(input),
      session.canAddOutput(output)
    else {
      session.commitConfiguration()
      DispatchQueue.main.async {
        self.state = .failed("Rear camera is unavailable on this device.")
      }
      return
    }
    session.addInput(input)
    session.addOutput(output)
    session.commitConfiguration()
  }
}

extension PhotoCaptureStore: AVCapturePhotoCaptureDelegate {
  func photoOutput(
    _ output: AVCapturePhotoOutput,
    didFinishProcessingPhoto photo: AVCapturePhoto,
    error: Error?
  ) {
    DispatchQueue.main.async {
      if let error {
        self.state = .failed(error.localizedDescription)
        return
      }
      guard let data = photo.fileDataRepresentation() else {
        self.state = .failed("The camera did not return a JPEG still.")
        return
      }
      self.pendingJPEGs.append(data)
      self.state = .ready
    }
  }
}
