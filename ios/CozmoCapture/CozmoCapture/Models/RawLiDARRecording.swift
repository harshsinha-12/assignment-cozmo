import Foundation

struct EncodedLiDARFrame {
  let timestampS: Double
  let pose: [Double]
  let intrinsics: [Double]
  let jpeg: Data
  let depthLZFSE: Data
  let confidenceLZFSE: Data
}

struct RawLiDARRecording {
  let colorWidthPx: Int
  let colorHeightPx: Int
  let depthWidthPx: Int
  let depthHeightPx: Int
  let fps: Double
  let frames: [EncodedLiDARFrame]
}
