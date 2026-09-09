import Foundation
import UIKit
import XCTest

@testable import CozmoCapture

final class JobPackageTests: XCTestCase {
  private var scratch: URL!

  override func setUpWithError() throws {
    scratch = FileManager.default.temporaryDirectory
      .appendingPathComponent("JobPackageTests-\(UUID().uuidString)", isDirectory: true)
    try FileManager.default.createDirectory(at: scratch, withIntermediateDirectories: true)
  }

  override func tearDownWithError() throws {
    if let scratch {
      try? FileManager.default.removeItem(at: scratch)
    }
  }

  func testManifestQuotesRequiredJobFields() {
    let yaml = CaptureJobManifest.yaml(
      jobId: "cozmo-capture-test",
      device: "iPhone 17 Pro",
      rooms: ["Kitchen", "Hall"],
      lidarFiles: ["lidar/roomplan.json", "lidar/kitchen.r3d"]
    )

    XCTAssertTrue(yaml.contains("job_id: \"cozmo-capture-test\""))
    XCTAssertTrue(yaml.contains("tier: lidar"))
    XCTAssertTrue(yaml.contains("device: \"iPhone 17 Pro\""))
    XCTAssertTrue(yaml.contains("capture_tool: \"Cozmo Capture 0.1.0\""))
    XCTAssertTrue(yaml.contains("capture_format: \"roomplan-json-v1+record3d-r3d\""))
    XCTAssertTrue(yaml.contains("  - \"Kitchen\""))
    XCTAssertTrue(yaml.contains("  - \"Hall\""))
    XCTAssertTrue(yaml.contains("  - \"lidar/roomplan.json\""))
    XCTAssertTrue(yaml.contains("  - \"lidar/kitchen.r3d\""))
  }

  func testJobIdUsesStableUTCTimestamp() {
    XCTAssertEqual(
      JobPackageBuilder.makeJobId(date: Date(timeIntervalSince1970: 1_788_978_640)),
      "cozmo-capture-20260909-183040"
    )
  }

  func testPackageWritesFolderAndZipMatchingCLILayout() throws {
    let recording = try sampleRecording()
    let package = try JobPackageBuilder.write(
      plan: samplePlan(),
      recordings: [("Kitchen", recording), ("Hall", nil)],
      jobId: "cozmo-capture-test",
      device: "iPhone 17 Pro",
      into: scratch
    )

    XCTAssertEqual(package.jobId, "cozmo-capture-test")
    XCTAssertEqual(package.zipURL.lastPathComponent, "cozmo-capture-test.zip")

    let manifest = try String(
      contentsOf: package.jobDirectory.appendingPathComponent("manifest.yaml"),
      encoding: .utf8
    )
    XCTAssertTrue(manifest.contains("tier: lidar"))
    XCTAssertTrue(
      FileManager.default.fileExists(
        atPath: package.jobDirectory.appendingPathComponent("lidar/roomplan.json").path
      )
    )
    XCTAssertTrue(
      FileManager.default.fileExists(
        atPath: package.jobDirectory.appendingPathComponent("lidar/kitchen.r3d").path
      )
    )
    XCTAssertFalse(
      FileManager.default.fileExists(
        atPath: package.jobDirectory.appendingPathComponent("lidar/hall.r3d").path
      )
    )

    let planObject = try jsonObject(
      from: Data(contentsOf: package.jobDirectory.appendingPathComponent("lidar/roomplan.json"))
    )
    let rooms = try XCTUnwrap(planObject["rooms"] as? [[String: Any]])
    XCTAssertEqual(rooms.map { $0["label"] as? String }, ["Kitchen", "Hall"])

    let entries = try zipEntries(Data(contentsOf: package.zipURL))
    XCTAssertEqual(
      Set(entries.keys),
      [
        "cozmo-capture-test/manifest.yaml",
        "cozmo-capture-test/lidar/roomplan.json",
        "cozmo-capture-test/lidar/kitchen.r3d",
      ]
    )
    XCTAssertEqual(
      entries["cozmo-capture-test/manifest.yaml"],
      try Data(contentsOf: package.jobDirectory.appendingPathComponent("manifest.yaml"))
    )
  }

  func testDuplicateJobIdsAreUniqued() throws {
    _ = try JobPackageBuilder.write(
      plan: samplePlan(),
      recordings: [],
      jobId: "cozmo-capture-test",
      device: "iPhone 17 Pro",
      into: scratch
    )
    let second = try JobPackageBuilder.write(
      plan: samplePlan(),
      recordings: [],
      jobId: "cozmo-capture-test",
      device: "iPhone 17 Pro",
      into: scratch
    )
    XCTAssertEqual(second.jobId, "cozmo-capture-test-2")
    XCTAssertEqual(second.zipURL.lastPathComponent, "cozmo-capture-test-2.zip")
  }

  func testEmptyPlanIsRejected() {
    XCTAssertThrowsError(
      try JobPackageBuilder.write(
        plan: PortableRoomPlan(rooms: []),
        recordings: [],
        jobId: "cozmo-capture-empty",
        device: "iPhone 17 Pro",
        into: scratch
      )
    ) { error in
      XCTAssertEqual(
        (error as? JobPackageBuilder.PackageError),
        JobPackageBuilder.PackageError.emptyPlan
      )
    }
  }

  private func samplePlan() -> PortableRoomPlan {
    let identity: [Float] = [
      1, 0, 0, 0,
      0, 1, 0, 0,
      0, 0, 1, 0,
      0, 0, 0, 1,
    ]
    let wall = PortableSurface(
      identifier: "wall-1",
      dimensions: [4.2, 2.5, 0.1],
      transform: identity,
      confidence: "high"
    )
    return PortableRoomPlan(rooms: [
      PortableRoom(
        identifier: "room_a",
        label: "Kitchen",
        walls: [wall, wall, wall],
        doors: [],
        windows: [],
        openings: []
      ),
      PortableRoom(
        identifier: "room_b",
        label: "Hall",
        walls: [wall, wall, wall],
        doors: [],
        windows: [],
        openings: []
      ),
    ])
  }

  private func sampleRecording() throws -> RawLiDARRecording {
    EncodedLiDARFrame(
      timestampS: 0.5,
      pose: [0, 0, 0, 1, 0.1, 1.4, 0.2],
      intrinsics: [600, 601, 320, 240],
      jpeg: try tinyJPEG(),
      depthLZFSE: try ARKitFrameEncoder.compressLZFSE(float32Buffer(values: [1, 1.5, 2, 2.5])),
      confidenceLZFSE: try ARKitFrameEncoder.compressLZFSE(Data([2, 1, 1, 0]))
    ).recording
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

  private func jsonObject(from data: Data) throws -> [String: Any] {
    try XCTUnwrap(JSONSerialization.jsonObject(with: data) as? [String: Any])
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

  private func readUInt32(_ data: Data, _ offset: Int) -> UInt32 {
    UInt32(data[offset])
      | UInt32(data[offset + 1]) << 8
      | UInt32(data[offset + 2]) << 16
      | UInt32(data[offset + 3]) << 24
  }
}

extension EncodedLiDARFrame {
  fileprivate var recording: RawLiDARRecording {
    RawLiDARRecording(
      colorWidthPx: 2,
      colorHeightPx: 2,
      depthWidthPx: 2,
      depthHeightPx: 2,
      fps: 2,
      frames: [self]
    )
  }
}
