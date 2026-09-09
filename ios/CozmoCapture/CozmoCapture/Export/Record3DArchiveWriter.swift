import Foundation
import zlib

enum Record3DArchiveWriter {
  static func encoded(_ recording: RawLiDARRecording) throws -> Data {
    guard !recording.frames.isEmpty else {
      throw ArchiveError.emptyRecording
    }

    var zip = ZipStoreWriter()
    zip.add(name: "metadata", data: try metadataJSON(recording))
    for (index, frame) in recording.frames.enumerated() {
      zip.add(name: "rgbd/\(index).jpg", data: frame.jpeg)
      zip.add(name: "rgbd/\(index).depth", data: frame.depthLZFSE)
      zip.add(name: "rgbd/\(index).conf", data: frame.confidenceLZFSE)
    }
    return zip.encoded()
  }

  static func write(
    _ recording: RawLiDARRecording,
    to url: URL,
    fileManager: FileManager = .default
  ) throws {
    try encoded(recording).write(to: url, options: .atomic)
  }

  private static func metadataJSON(_ recording: RawLiDARRecording) throws -> Data {
    let document: [String: Any] = [
      "w": recording.colorWidthPx,
      "h": recording.colorHeightPx,
      "dw": recording.depthWidthPx,
      "dh": recording.depthHeightPx,
      "fps": recording.fps,
      "frameTimestamps": recording.frames.map(\.timestampS),
      "poses": recording.frames.map(\.pose),
      "perFrameIntrinsicCoeffs": recording.frames.map(\.intrinsics),
      "source": AppConfig.record3DSource,
    ]
    return try JSONSerialization.data(withJSONObject: document, options: [.sortedKeys])
  }

  enum ArchiveError: LocalizedError {
    case emptyRecording
    var errorDescription: String? { "LiDAR recording has no frames." }
  }
}

struct ZipStoreWriter {
  private var entries: [(name: String, data: Data)] = []

  mutating func add(name: String, data: Data) {
    entries.append((name, data))
  }

  func encoded() -> Data {
    var local = Data()
    var central = Data()
    var offset: UInt32 = 0

    for entry in entries {
      let nameData = Data(entry.name.utf8)
      let crc = crc32Checksum(entry.data)
      let size = UInt32(entry.data.count)
      var localHeader = Data()
      localHeader.append(contentsOf: [0x50, 0x4B, 0x03, 0x04])
      localHeader.append(contentsOf: UInt16(20).littleEndianBytes)
      localHeader.append(contentsOf: UInt16(0).littleEndianBytes)
      localHeader.append(contentsOf: UInt16(0).littleEndianBytes)
      localHeader.append(contentsOf: UInt16(0).littleEndianBytes)
      localHeader.append(contentsOf: UInt16(0).littleEndianBytes)
      localHeader.append(contentsOf: crc.littleEndianBytes)
      localHeader.append(contentsOf: size.littleEndianBytes)
      localHeader.append(contentsOf: size.littleEndianBytes)
      localHeader.append(contentsOf: UInt16(nameData.count).littleEndianBytes)
      localHeader.append(contentsOf: UInt16(0).littleEndianBytes)
      localHeader.append(nameData)
      localHeader.append(entry.data)

      var centralHeader = Data()
      centralHeader.append(contentsOf: [0x50, 0x4B, 0x01, 0x02])
      centralHeader.append(contentsOf: UInt16(20).littleEndianBytes)
      centralHeader.append(contentsOf: UInt16(20).littleEndianBytes)
      centralHeader.append(contentsOf: UInt16(0).littleEndianBytes)
      centralHeader.append(contentsOf: UInt16(0).littleEndianBytes)
      centralHeader.append(contentsOf: UInt16(0).littleEndianBytes)
      centralHeader.append(contentsOf: UInt16(0).littleEndianBytes)
      centralHeader.append(contentsOf: crc.littleEndianBytes)
      centralHeader.append(contentsOf: size.littleEndianBytes)
      centralHeader.append(contentsOf: size.littleEndianBytes)
      centralHeader.append(contentsOf: UInt16(nameData.count).littleEndianBytes)
      centralHeader.append(contentsOf: UInt16(0).littleEndianBytes)
      centralHeader.append(contentsOf: UInt16(0).littleEndianBytes)
      centralHeader.append(contentsOf: UInt16(0).littleEndianBytes)
      centralHeader.append(contentsOf: UInt16(0).littleEndianBytes)
      centralHeader.append(contentsOf: UInt32(0).littleEndianBytes)
      centralHeader.append(contentsOf: offset.littleEndianBytes)
      centralHeader.append(nameData)

      local.append(localHeader)
      central.append(centralHeader)
      offset += UInt32(localHeader.count)
    }

    var end = Data()
    end.append(contentsOf: [0x50, 0x4B, 0x05, 0x06])
    end.append(contentsOf: UInt16(0).littleEndianBytes)
    end.append(contentsOf: UInt16(0).littleEndianBytes)
    end.append(contentsOf: UInt16(entries.count).littleEndianBytes)
    end.append(contentsOf: UInt16(entries.count).littleEndianBytes)
    end.append(contentsOf: UInt32(central.count).littleEndianBytes)
    end.append(contentsOf: UInt32(local.count).littleEndianBytes)
    end.append(contentsOf: UInt16(0).littleEndianBytes)
    return local + central + end
  }
}

private func crc32Checksum(_ data: Data) -> UInt32 {
  data.withUnsafeBytes { buffer in
    let pointer = buffer.bindMemory(to: UInt8.self)
    return UInt32(zlib.crc32(0, pointer.baseAddress, uInt(pointer.count)))
  }
}

extension FixedWidthInteger {
  fileprivate var littleEndianBytes: [UInt8] {
    withUnsafeBytes(of: littleEndian, Array.init)
  }
}
