import Foundation

enum RoomPlanExporter {
  static func encoded(_ plan: PortableRoomPlan) throws -> Data {
    let encoder = JSONEncoder()
    encoder.outputFormatting = [.prettyPrinted, .sortedKeys, .withoutEscapingSlashes]
    return try encoder.encode(plan)
  }

  static func write(_ plan: PortableRoomPlan, fileManager: FileManager = .default) throws -> URL {
    try write(plan, recordings: [], fileManager: fileManager)[0]
  }

  static func write(
    _ plan: PortableRoomPlan,
    recordings: [CapturedSessionRoom],
    fileManager: FileManager = .default
  ) throws -> [URL] {
    let directory = try exportDirectory(fileManager: fileManager)
    let planURL = directory.appendingPathComponent(AppConfig.exportFileName)
    try encoded(plan).write(to: planURL, options: .atomic)

    var urls = [planURL]
    var usedNames = [AppConfig.exportFileName]
    for room in recordings {
      guard let recording = room.lidarRecording else { continue }
      let fileName = AppConfig.archiveFileName(for: room.label, used: usedNames)
      let archiveURL = directory.appendingPathComponent(fileName)
      try Record3DArchiveWriter.write(recording, to: archiveURL, fileManager: fileManager)
      urls.append(archiveURL)
      usedNames.append(fileName)
    }
    return urls
  }

  private static func exportDirectory(fileManager: FileManager) throws -> URL {
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
    return directory
  }
}
