import Foundation
import UIKit
import XCTest
import simd

@testable import CozmoCapture

final class Record3DArchiveTests: XCTestCase {
  func testPoseAndIntrinsicsMatchRecord3DLayout() {
    var transform = matrix_identity_float4x4
    transform.columns.3 = SIMD4(1.25, 2.5, 3.75, 1)
    XCTAssertEqual(
      ARKitFrameEncoder.poseXYZW(transform: transform),
      [0, 0, 0, 1, 1.25, 2.5, 3.75],
      accuracy: 0.0001
    )

    let intrinsics = simd_float3x3(
      columns: (
        SIMD3(600, 0, 0),
        SIMD3(0, 601, 0),
        SIMD3(320, 240, 1)
      ))
    XCTAssertEqual(ARKitFrameEncoder.intrinsicCoeffs(intrinsics), [600, 601, 320, 240])
  }

  func testArchiveFileNamesAreStableAndUnique() {
    XCTAssertEqual(AppConfig.archiveFileName(for: "My Room", used: []), "my-room.r3d")
    XCTAssertEqual(
      AppConfig.archiveFileName(for: "My Room", used: ["my-room.r3d"]),
      "my-room-2.r3d"
    )
  }

  func testArchiveMatchesRecord3DContract() throws {
    let jpeg = try tinyJPEG()
    let depth = float32Buffer(values: [1.0, 1.5, 2.0, 2.5])
    let confidence = Data([2, 1, 1, 0])
    let frame = EncodedLiDARFrame(
      timestampS: 0.5,
      pose: [0, 0, 0, 1, 0.1, 1.4, 0.2],
      intrinsics: [600, 601, 320, 240],
      jpeg: jpeg,
      depthLZFSE: try ARKitFrameEncoder.compressLZFSE(depth),
      confidenceLZFSE: try ARKitFrameEncoder.compressLZFSE(confidence)
    )
    let recording = RawLiDARRecording(
      colorWidthPx: 2,
      colorHeightPx: 2,
      depthWidthPx: 2,
      depthHeightPx: 2,
      fps: 2,
      frames: [frame]
    )

    let archive = try Record3DArchiveWriter.encoded(recording)
    let entries = try zipEntries(archive)
    XCTAssertEqual(Set(entries.keys), ["metadata", "rgbd/0.jpg", "rgbd/0.depth", "rgbd/0.conf"])

    let metadata = try XCTUnwrap(
      JSONSerialization.jsonObject(with: XCTUnwrap(entries["metadata"])) as? [String: Any]
    )
    XCTAssertEqual(metadata["w"] as? Int, 2)
    XCTAssertEqual(metadata["h"] as? Int, 2)
    XCTAssertEqual(metadata["dw"] as? Int, 2)
    XCTAssertEqual(metadata["dh"] as? Int, 2)
    XCTAssertEqual(double(metadata["fps"]), 2)
    XCTAssertEqual(metadata["source"] as? String, "cozmo-capture-arkit")
    XCTAssertEqual(try numberRow(metadata["frameTimestamps"]), [0.5])
    XCTAssertEqual(try numberMatrix(metadata["poses"]), [[0, 0, 0, 1, 0.1, 1.4, 0.2]])
    XCTAssertEqual(
      try numberMatrix(metadata["perFrameIntrinsicCoeffs"]),
      [[600, 601, 320, 240]]
    )

    let decodedDepth = try decompressLZFSE(XCTUnwrap(entries["rgbd/0.depth"]), expected: 16)
    let decodedConfidence = try decompressLZFSE(XCTUnwrap(entries["rgbd/0.conf"]), expected: 4)
    XCTAssertEqual(decodedDepth, depth)
    XCTAssertEqual(decodedConfidence, confidence)
    XCTAssertEqual(entries["rgbd/0.jpg"], jpeg)
  }

  private func tinyJPEG() throws -> Data {
    let size = CGSize(width: 2, height: 2)
    UIGraphicsBeginImageContext(size)
    UIColor.red.setFill()
    UIRectFill(CGRect(origin: .zero, size: size))
    let image = UIGraphicsGetImageFromCurrentImageContext()
    UIGraphicsEndImageContext()
    return try XCTUnwrap(image?.jpegData(compressionQuality: 0.8))
  }

  private func float32Buffer(values: [Float]) -> Data {
    var copy = values
    return copy.withUnsafeMutableBytes { Data($0) }
  }

  private func decompressLZFSE(_ data: Data, expected: Int) throws -> Data {
    let decoded = try (data as NSData).decompressed(using: .lzfse) as Data
    XCTAssertEqual(decoded.count, expected)
    return decoded
  }

  private func zipEntries(_ data: Data) throws -> [String: Data] {
    var entries: [String: Data] = [:]
    var offset = 0
    while offset + 30 <= data.count {
      let signature = data.subdata(in: offset..<(offset + 4))
      if signature != Data([0x50, 0x4B, 0x03, 0x04]) {
        break
      }
      let nameLength = Int(readUInt16(data, offset + 26))
      let extraLength = Int(readUInt16(data, offset + 28))
      let size = Int(readUInt32(data, offset + 18))
      let nameStart = offset + 30
      let name = String(
        data: data.subdata(in: nameStart..<(nameStart + nameLength)),
        encoding: .utf8
      )
      let payloadStart = nameStart + nameLength + extraLength
      entries[try XCTUnwrap(name)] = data.subdata(in: payloadStart..<(payloadStart + size))
      offset = payloadStart + size
    }
    XCTAssertFalse(entries.isEmpty)
    return entries
  }

  private func readUInt16(_ data: Data, _ offset: Int) -> UInt16 {
    UInt16(data[offset]) | UInt16(data[offset + 1]) << 8
  }

  private func double(_ value: Any?) -> Double {
    (value as? NSNumber)?.doubleValue ?? -1
  }

  private func numberRow(_ value: Any?) throws -> [Double] {
    try XCTUnwrap(value as? [Any]).map { ($0 as! NSNumber).doubleValue }
  }

  private func numberMatrix(_ value: Any?) throws -> [[Double]] {
    try XCTUnwrap(value as? [Any]).map { row in
      (row as! [Any]).map { ($0 as! NSNumber).doubleValue }
    }
  }

  private func readUInt32(_ data: Data, _ offset: Int) -> UInt32 {
    UInt32(data[offset])
      | UInt32(data[offset + 1]) << 8
      | UInt32(data[offset + 2]) << 16
      | UInt32(data[offset + 3]) << 24
  }
}

private func XCTAssertEqual(
  _ expression: [Double],
  _ expected: [Double],
  accuracy: Double,
  file: StaticString = #filePath,
  line: UInt = #line
) {
  XCTAssertEqual(expression.count, expected.count, file: file, line: line)
  for (value, target) in zip(expression, expected) {
    XCTAssertEqual(value, target, accuracy: accuracy, file: file, line: line)
  }
}
