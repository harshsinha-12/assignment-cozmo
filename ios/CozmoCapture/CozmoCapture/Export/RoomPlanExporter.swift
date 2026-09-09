import Foundation

enum RoomPlanExporter {
  static func encoded(_ plan: PortableRoomPlan) throws -> Data {
    let encoder = JSONEncoder()
    encoder.outputFormatting = [.prettyPrinted, .sortedKeys, .withoutEscapingSlashes]
    return try encoder.encode(plan)
  }

  static func write(_ plan: PortableRoomPlan, fileManager: FileManager = .default) throws -> URL {
    let documents = try fileManager.url(
      for: .documentDirectory,
      in: .userDomainMask,
      appropriateFor: nil,
      create: true
    )
    let directory = documents.appendingPathComponent(
      AppConfig.exportDirectoryName,
      isDirectory: true
    )
    try fileManager.createDirectory(at: directory, withIntermediateDirectories: true)
    let destination = directory.appendingPathComponent(AppConfig.exportFileName)
    try encoded(plan).write(to: destination, options: .atomic)
    return destination
  }
}
