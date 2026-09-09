import ARKit
import Foundation

@MainActor
final class ARKitLiDARRecorder {
  var onFrameCountChange: ((Int) -> Void)?

  private var timer: Timer?
  private weak var arSession: ARSession?
  private var frames: [EncodedLiDARFrame] = []
  private var originTimestamp: TimeInterval?
  private var colorSize: (Int, Int)?
  private var depthSize: (Int, Int)?

  func start(session: ARSession) {
    stopSampling()
    frames = []
    originTimestamp = nil
    colorSize = nil
    depthSize = nil
    onFrameCountChange?(0)
    arSession = session
    let timer = Timer(timeInterval: AppConfig.lidarSampleInterval, repeats: true) { [weak self] _ in
      Task { @MainActor in
        self?.sample()
      }
    }
    RunLoop.main.add(timer, forMode: .common)
    self.timer = timer
    sample()
  }

  func finish() -> RawLiDARRecording? {
    stopSampling()
    guard let colorSize, let depthSize, !frames.isEmpty else { return nil }
    return RawLiDARRecording(
      colorWidthPx: colorSize.0,
      colorHeightPx: colorSize.1,
      depthWidthPx: depthSize.0,
      depthHeightPx: depthSize.1,
      fps: 1.0 / AppConfig.lidarSampleInterval,
      frames: frames
    )
  }

  private func stopSampling() {
    timer?.invalidate()
    timer = nil
    arSession = nil
  }

  private func sample() {
    guard frames.count < AppConfig.lidarMaxFramesPerRoom else { return }
    guard let frame = arSession?.currentFrame else { return }
    guard let encoded = encode(frame) else { return }
    if colorSize == nil {
      colorSize = (
        CVPixelBufferGetWidth(frame.capturedImage),
        CVPixelBufferGetHeight(frame.capturedImage)
      )
    }
    frames.append(encoded)
    onFrameCountChange?(frames.count)
  }

  private func encode(_ frame: ARFrame) -> EncodedLiDARFrame? {
    let depthData = frame.sceneDepth ?? frame.smoothedSceneDepth
    guard let depthData, let confidenceMap = depthData.confidenceMap else { return nil }

    do {
      let depth = try ARKitFrameEncoder.packedFloat32(from: depthData.depthMap)
      let confidence = try ARKitFrameEncoder.packedUInt8(from: confidenceMap)
      guard depth.width == confidence.width, depth.height == confidence.height else { return nil }
      if let depthSize, depthSize != (depth.width, depth.height) {
        return nil
      }
      depthSize = (depth.width, depth.height)

      let origin = originTimestamp ?? frame.timestamp
      originTimestamp = origin
      return EncodedLiDARFrame(
        timestampS: frame.timestamp - origin,
        pose: ARKitFrameEncoder.poseXYZW(transform: frame.camera.transform),
        intrinsics: ARKitFrameEncoder.intrinsicCoeffs(frame.camera.intrinsics),
        jpeg: try ARKitFrameEncoder.jpeg(
          from: frame.capturedImage,
          quality: AppConfig.lidarJPEGQuality
        ),
        depthLZFSE: try ARKitFrameEncoder.compressLZFSE(depth.data),
        confidenceLZFSE: try ARKitFrameEncoder.compressLZFSE(confidence.data)
      )
    } catch {
      return nil
    }
  }
}
