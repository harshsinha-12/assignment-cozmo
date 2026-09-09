import CoreImage
import CoreVideo
import Foundation
import UIKit
import simd

enum ARKitFrameEncoder {
  enum EncoderError: LocalizedError {
    case missingPixelData
    case jpegFailed
    case compressionFailed

    var errorDescription: String? {
      switch self {
      case .missingPixelData: "LiDAR frame is missing pixel data."
      case .jpegFailed: "Could not encode the RGB JPEG."
      case .compressionFailed: "Could not LZFSE-compress the LiDAR buffers."
      }
    }
  }

  static func poseXYZW(transform: simd_float4x4) -> [Double] {
    let rotation = simd_float3x3(
      SIMD3(transform.columns.0.x, transform.columns.0.y, transform.columns.0.z),
      SIMD3(transform.columns.1.x, transform.columns.1.y, transform.columns.1.z),
      SIMD3(transform.columns.2.x, transform.columns.2.y, transform.columns.2.z)
    )
    let quaternion = simd_quatf(rotation).normalized
    return [
      Double(quaternion.vector.x),
      Double(quaternion.vector.y),
      Double(quaternion.vector.z),
      Double(quaternion.vector.w),
      Double(transform.columns.3.x),
      Double(transform.columns.3.y),
      Double(transform.columns.3.z),
    ]
  }

  static func intrinsicCoeffs(_ matrix: simd_float3x3) -> [Double] {
    [
      Double(matrix.columns.0.x),
      Double(matrix.columns.1.y),
      Double(matrix.columns.2.x),
      Double(matrix.columns.2.y),
    ]
  }

  static func compressLZFSE(_ data: Data) throws -> Data {
    do {
      return try (data as NSData).compressed(using: .lzfse) as Data
    } catch {
      throw EncoderError.compressionFailed
    }
  }

  static func jpeg(from pixelBuffer: CVPixelBuffer, quality: CGFloat) throws -> Data {
    let image = CIImage(cvPixelBuffer: pixelBuffer)
    let context = CIContext(options: nil)
    guard let cgImage = context.createCGImage(image, from: image.extent) else {
      throw EncoderError.jpegFailed
    }
    guard let data = UIImage(cgImage: cgImage).jpegData(compressionQuality: quality) else {
      throw EncoderError.jpegFailed
    }
    return data
  }

  static func packedFloat32(from buffer: CVPixelBuffer) throws -> (
    width: Int, height: Int, data: Data
  ) {
    try packedBytes(from: buffer, bytesPerPixel: 4)
  }

  static func packedUInt8(from buffer: CVPixelBuffer) throws -> (
    width: Int, height: Int, data: Data
  ) {
    try packedBytes(from: buffer, bytesPerPixel: 1)
  }

  private static func packedBytes(
    from buffer: CVPixelBuffer,
    bytesPerPixel: Int
  ) throws -> (width: Int, height: Int, data: Data) {
    CVPixelBufferLockBaseAddress(buffer, .readOnly)
    defer { CVPixelBufferUnlockBaseAddress(buffer, .readOnly) }
    let width = CVPixelBufferGetWidth(buffer)
    let height = CVPixelBufferGetHeight(buffer)
    let bytesPerRow = CVPixelBufferGetBytesPerRow(buffer)
    let rowBytes = width * bytesPerPixel
    guard let base = CVPixelBufferGetBaseAddress(buffer), width > 0, height > 0 else {
      throw EncoderError.missingPixelData
    }

    var packed = Data(count: rowBytes * height)
    packed.withUnsafeMutableBytes { destination in
      guard let dest = destination.baseAddress else { return }
      for row in 0..<height {
        memcpy(
          dest.advanced(by: row * rowBytes),
          base.advanced(by: row * bytesPerRow),
          rowBytes
        )
      }
    }
    return (width, height, packed)
  }
}
