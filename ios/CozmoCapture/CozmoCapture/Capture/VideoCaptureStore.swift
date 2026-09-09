import AVFoundation
import Foundation

struct CapturedVideoClip: Identifiable {
  let id = UUID()
  let label: String
  let data: Data
}

final class VideoCaptureStore: NSObject, ObservableObject {
  @Published var state: CaptureState = .ready
  @Published var clips: [CapturedVideoClip] = []
  @Published var exportURLs: [URL] = []
  @Published var draftLabel: String = AppConfig.defaultLabel(forIndex: 0)
  @Published var isRecording = false

  let session = AVCaptureSession()
  private let movieOutput = AVCaptureMovieFileOutput()
  private let sessionQueue = DispatchQueue(label: "cozmo.video.session")

  func startSession() {
    sessionQueue.async { [weak self] in
      self?.configureIfNeeded()
      self?.session.startRunning()
    }
  }

  func stopSession() {
    sessionQueue.async { [weak self] in
      guard let self else { return }
      if self.movieOutput.isRecording {
        self.movieOutput.stopRecording()
      }
      self.session.stopRunning()
    }
  }

  func toggleRecording() {
    if isRecording {
      movieOutput.stopRecording()
      return
    }
    guard state == .ready || state == .exported || isFailed else { return }
    let url = FileManager.default.temporaryDirectory
      .appendingPathComponent("cozmo-video-\(UUID().uuidString).mp4")
    isRecording = true
    state = .capturing
    movieOutput.startRecording(to: url, recordingDelegate: self)
  }

  func exportJob() {
    guard !isRecording else {
      state = .failed("Stop recording before exporting.")
      return
    }
    guard !clips.isEmpty else {
      state = .failed("Record at least one room walkthrough before exporting.")
      return
    }
    do {
      let package = try JobPackageBuilder.writeVideosToDocuments(
        clips: clips.map { ($0.label, $0.data) }
      )
      exportURLs = [package.zipURL]
      state = .exported
    } catch {
      state = .failed("Could not write the video job: \(error.localizedDescription)")
    }
  }

  func reset() {
    clips = []
    exportURLs = []
    draftLabel = AppConfig.defaultLabel(forIndex: 0)
    isRecording = false
    state = .ready
  }

  private var isFailed: Bool {
    if case .failed = state { return true }
    return false
  }

  private func configureIfNeeded() {
    guard session.inputs.isEmpty else { return }
    session.beginConfiguration()
    session.sessionPreset = .hd1920x1080
    guard let camera = AVCaptureDevice.default(.builtInWideAngleCamera, for: .video, position: .back),
      let videoInput = try? AVCaptureDeviceInput(device: camera),
      session.canAddInput(videoInput)
    else {
      session.commitConfiguration()
      DispatchQueue.main.async {
        self.state = .failed("Rear camera is unavailable on this device.")
      }
      return
    }
    session.addInput(videoInput)
    if let microphone = AVCaptureDevice.default(for: .audio),
      let audioInput = try? AVCaptureDeviceInput(device: microphone),
      session.canAddInput(audioInput)
    {
      session.addInput(audioInput)
    }
    guard session.canAddOutput(movieOutput) else {
      session.commitConfiguration()
      DispatchQueue.main.async {
        self.state = .failed("Video recording is unavailable on this device.")
      }
      return
    }
    session.addOutput(movieOutput)
    session.commitConfiguration()
  }
}

extension VideoCaptureStore: AVCaptureFileOutputRecordingDelegate {
  func fileOutput(
    _ output: AVCaptureFileOutput,
    didFinishRecordingTo outputFileURL: URL,
    from connections: [AVCaptureConnection],
    error: Error?
  ) {
    DispatchQueue.main.async {
      self.isRecording = false
      if let error {
        self.state = .failed(error.localizedDescription)
        return
      }
      do {
        let data = try Data(contentsOf: outputFileURL)
        let label = AppConfig.uniquedLabel(self.draftLabel, existing: self.clips.map(\.label))
        self.clips.append(CapturedVideoClip(label: label, data: data))
        self.draftLabel = AppConfig.defaultLabel(forIndex: self.clips.count)
        self.exportURLs = []
        self.state = .ready
      } catch {
        self.state = .failed("Could not read the recorded clip: \(error.localizedDescription)")
      }
      try? FileManager.default.removeItem(at: outputFileURL)
    }
  }
}
