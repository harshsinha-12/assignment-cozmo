import Foundation
import UIKit

struct CaptureJobPackage: Equatable {
  let jobId: String
  let jobDirectory: URL
  let zipURL: URL
}

enum JobPackageBuilder {
  static var currentDeviceName: String {
    UIDevice.current.model
  }

  static func makeJobId(date: Date) -> String {
    let formatter = DateFormatter()
    formatter.calendar = Calendar(identifier: .gregorian)
    formatter.locale = Locale(identifier: "en_US_POSIX")
    formatter.timeZone = TimeZone(secondsFromGMT: 0)
    formatter.dateFormat = "yyyyMMdd-HHmmss"
    return "\(AppConfig.jobIdPrefix)-\(formatter.string(from: date))"
  }

  static func writeToDocuments(
    plan: PortableRoomPlan,
    recordings: [(label: String, recording: RawLiDARRecording?)],
    fileManager: FileManager = .default
  ) throws -> CaptureJobPackage {
    let documents = try fileManager.url(
      for: .documentDirectory,
      in: .userDomainMask,
      appropriateFor: nil,
      create: true
    )
    let parent = documents.appendingPathComponent(
      AppConfig.exportDirectoryName,
      isDirectory: true
    )
    try fileManager.createDirectory(at: parent, withIntermediateDirectories: true)
    return try write(
      plan: plan,
      recordings: recordings,
      device: currentDeviceName,
      into: parent,
      fileManager: fileManager
    )
  }

  static func write(
    plan: PortableRoomPlan,
    recordings: [(label: String, recording: RawLiDARRecording?)],
    jobId: String? = nil,
    device: String,
    createdAt: Date = Date(),
    into parentDirectory: URL,
    fileManager: FileManager = .default
  ) throws -> CaptureJobPackage {
    guard !plan.rooms.isEmpty else {
      throw PackageError.emptyPlan
    }

    try fileManager.createDirectory(at: parentDirectory, withIntermediateDirectories: true)
    let resolvedId = uniquedJobId(
      jobId ?? makeJobId(date: createdAt),
      in: parentDirectory,
      fileManager: fileManager
    )
    let jobDirectory = parentDirectory.appendingPathComponent(resolvedId, isDirectory: true)
    if fileManager.fileExists(atPath: jobDirectory.path) {
      try fileManager.removeItem(at: jobDirectory)
    }
    let lidarDirectory = jobDirectory.appendingPathComponent(
      AppConfig.lidarDirectoryName,
      isDirectory: true
    )
    try fileManager.createDirectory(at: lidarDirectory, withIntermediateDirectories: true)

    let planData = try RoomPlanExporter.encoded(plan)
    let planRelative = "\(AppConfig.lidarDirectoryName)/\(AppConfig.exportFileName)"
    try planData.write(
      to: lidarDirectory.appendingPathComponent(AppConfig.exportFileName),
      options: .atomic
    )

    var zip = ZipStoreWriter()
    zip.add(name: "\(resolvedId)/\(planRelative)", data: planData)

    var lidarFiles = [planRelative]
    var usedNames = [AppConfig.exportFileName]
    for (label, recording) in recordings {
      guard let recording, !recording.frames.isEmpty else { continue }
      let fileName = AppConfig.archiveFileName(for: label, used: usedNames)
      let archiveData = try Record3DArchiveWriter.encoded(recording)
      let relative = "\(AppConfig.lidarDirectoryName)/\(fileName)"
      try archiveData.write(
        to: lidarDirectory.appendingPathComponent(fileName),
        options: .atomic
      )
      zip.add(name: "\(resolvedId)/\(relative)", data: archiveData)
      lidarFiles.append(relative)
      usedNames.append(fileName)
    }

    let manifestData = Data(
      CaptureJobManifest.yaml(
        jobId: resolvedId,
        tier: "lidar",
        device: device,
        captureFormat: AppConfig.captureFormat,
        rooms: plan.rooms.map(\.label),
        filesKey: "lidar_files",
        files: lidarFiles,
        notes: AppConfig.jobNotes
      ).utf8
    )
    try manifestData.write(
      to: jobDirectory.appendingPathComponent(AppConfig.manifestFileName),
      options: .atomic
    )
    zip.add(name: "\(resolvedId)/\(AppConfig.manifestFileName)", data: manifestData)

    let zipURL = parentDirectory.appendingPathComponent("\(resolvedId).zip")
    try zip.encoded().write(to: zipURL, options: .atomic)
    return CaptureJobPackage(jobId: resolvedId, jobDirectory: jobDirectory, zipURL: zipURL)
  }

  static func writePhotosToDocuments(
    rooms: [(label: String, jpegs: [Data])],
    fileManager: FileManager = .default
  ) throws -> CaptureJobPackage {
    try writePhotos(
      rooms: rooms,
      device: currentDeviceName,
      into: try documentsExportDirectory(fileManager: fileManager),
      fileManager: fileManager
    )
  }

  static func writePhotos(
    rooms: [(label: String, jpegs: [Data])],
    jobId: String? = nil,
    device: String,
    createdAt: Date = Date(),
    into parentDirectory: URL,
    fileManager: FileManager = .default
  ) throws -> CaptureJobPackage {
    guard !rooms.isEmpty else {
      throw PackageError.emptyPlan
    }
    for (_, jpegs) in rooms {
      guard (AppConfig.minPhotosPerRoom...AppConfig.maxPhotosPerRoom).contains(jpegs.count) else {
        throw PackageError.invalidPhotoCount
      }
    }

    let prepared = try prepareJob(
      jobId: jobId,
      createdAt: createdAt,
      into: parentDirectory,
      fileManager: fileManager
    )
    var zip = ZipStoreWriter()
    var files: [String] = []
    var usedFolders: [String] = []
    for (label, jpegs) in rooms {
      let folder = AppConfig.folderName(for: label, used: usedFolders)
      usedFolders.append(folder)
      let directory = prepared.jobDirectory
        .appendingPathComponent(AppConfig.photosDirectoryName, isDirectory: true)
        .appendingPathComponent(folder, isDirectory: true)
      try fileManager.createDirectory(at: directory, withIntermediateDirectories: true)
      for (index, jpeg) in jpegs.enumerated() {
        let name = String(format: "%02d.jpg", index + 1)
        let relative = "\(AppConfig.photosDirectoryName)/\(folder)/\(name)"
        try jpeg.write(to: directory.appendingPathComponent(name), options: .atomic)
        zip.add(name: "\(prepared.jobId)/\(relative)", data: jpeg)
        files.append(relative)
      }
    }
    return try finishPackage(
      prepared,
      zip: zip,
      tier: "photos",
      device: device,
      captureFormat: AppConfig.photoCaptureFormat,
      rooms: rooms.map(\.label),
      filesKey: "photo_files",
      files: files,
      notes: AppConfig.photoJobNotes
    )
  }

  static func writeVideosToDocuments(
    clips: [(label: String, data: Data)],
    fileManager: FileManager = .default
  ) throws -> CaptureJobPackage {
    try writeVideos(
      clips: clips,
      device: currentDeviceName,
      into: try documentsExportDirectory(fileManager: fileManager),
      fileManager: fileManager
    )
  }

  static func writeVideos(
    clips: [(label: String, data: Data)],
    jobId: String? = nil,
    device: String,
    createdAt: Date = Date(),
    into parentDirectory: URL,
    fileManager: FileManager = .default
  ) throws -> CaptureJobPackage {
    guard !clips.isEmpty else {
      throw PackageError.emptyPlan
    }

    let prepared = try prepareJob(
      jobId: jobId,
      createdAt: createdAt,
      into: parentDirectory,
      fileManager: fileManager
    )
    let videoDirectory = prepared.jobDirectory.appendingPathComponent(
      AppConfig.videoDirectoryName,
      isDirectory: true
    )
    try fileManager.createDirectory(at: videoDirectory, withIntermediateDirectories: true)
    var zip = ZipStoreWriter()
    var files: [String] = []
    var usedNames: [String] = []
    for (label, data) in clips {
      let fileName = AppConfig.uniquedName(base: AppConfig.slug(for: label), ext: "mp4", used: usedNames)
      usedNames.append(fileName)
      let relative = "\(AppConfig.videoDirectoryName)/\(fileName)"
      try data.write(to: videoDirectory.appendingPathComponent(fileName), options: .atomic)
      zip.add(name: "\(prepared.jobId)/\(relative)", data: data)
      files.append(relative)
    }
    return try finishPackage(
      prepared,
      zip: zip,
      tier: "video",
      device: device,
      captureFormat: AppConfig.videoCaptureFormat,
      rooms: clips.map(\.label),
      filesKey: "video_files",
      files: files,
      notes: AppConfig.videoJobNotes
    )
  }

  private static func documentsExportDirectory(fileManager: FileManager) throws -> URL {
    let documents = try fileManager.url(
      for: .documentDirectory,
      in: .userDomainMask,
      appropriateFor: nil,
      create: true
    )
    let parent = documents.appendingPathComponent(
      AppConfig.exportDirectoryName,
      isDirectory: true
    )
    try fileManager.createDirectory(at: parent, withIntermediateDirectories: true)
    return parent
  }

  private static func prepareJob(
    jobId: String?,
    createdAt: Date,
    into parentDirectory: URL,
    fileManager: FileManager
  ) throws -> CaptureJobPackage {
    try fileManager.createDirectory(at: parentDirectory, withIntermediateDirectories: true)
    let resolvedId = uniquedJobId(
      jobId ?? makeJobId(date: createdAt),
      in: parentDirectory,
      fileManager: fileManager
    )
    let jobDirectory = parentDirectory.appendingPathComponent(resolvedId, isDirectory: true)
    if fileManager.fileExists(atPath: jobDirectory.path) {
      try fileManager.removeItem(at: jobDirectory)
    }
    try fileManager.createDirectory(at: jobDirectory, withIntermediateDirectories: true)
    return CaptureJobPackage(
      jobId: resolvedId,
      jobDirectory: jobDirectory,
      zipURL: parentDirectory.appendingPathComponent("\(resolvedId).zip")
    )
  }

  private static func finishPackage(
    _ prepared: CaptureJobPackage,
    zip: ZipStoreWriter,
    tier: String,
    device: String,
    captureFormat: String,
    rooms: [String],
    filesKey: String,
    files: [String],
    notes: String
  ) throws -> CaptureJobPackage {
    var zip = zip
    let manifestData = Data(
      CaptureJobManifest.yaml(
        jobId: prepared.jobId,
        tier: tier,
        device: device,
        captureFormat: captureFormat,
        rooms: rooms,
        filesKey: filesKey,
        files: files,
        notes: notes
      ).utf8
    )
    try manifestData.write(
      to: prepared.jobDirectory.appendingPathComponent(AppConfig.manifestFileName),
      options: .atomic
    )
    zip.add(name: "\(prepared.jobId)/\(AppConfig.manifestFileName)", data: manifestData)
    try zip.encoded().write(to: prepared.zipURL, options: .atomic)
    return prepared
  }

  private static func uniquedJobId(
    _ base: String,
    in parent: URL,
    fileManager: FileManager
  ) -> String {
    var jobId = base
    var suffix = 2
    while fileManager.fileExists(atPath: parent.appendingPathComponent(jobId).path)
      || fileManager.fileExists(atPath: parent.appendingPathComponent("\(jobId).zip").path)
    {
      jobId = "\(base)-\(suffix)"
      suffix += 1
    }
    return jobId
  }

  enum PackageError: LocalizedError, Equatable {
    case emptyPlan
    case invalidPhotoCount

    var errorDescription: String? {
      switch self {
      case .emptyPlan:
        "Scan at least one room before exporting a capture job."
      case .invalidPhotoCount:
        "Each photo room needs 2 to 8 stills before export."
      }
    }
  }
}
