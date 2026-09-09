import SwiftUI

struct CaptureView: View {
  @StateObject private var store = RoomCaptureStore()

  var body: some View {
    ZStack(alignment: .bottom) {
      RoomCaptureContainer(store: store)
        .ignoresSafeArea()

      controls
        .padding()
    }
  }

  private var controls: some View {
    VStack(spacing: 12) {
      VStack(spacing: 4) {
        Text(store.state.title)
          .font(.headline)
        Text(store.state.message)
          .font(.footnote)
          .multilineTextAlignment(.center)
          .foregroundStyle(.secondary)
      }

      if store.state == .capturing {
        Text("LiDAR frames: \(store.lidarFrameCount)")
          .font(.footnote.monospacedDigit())
      }

      if !store.sessionRooms.isEmpty {
        roomList
      }

      if store.state.allowsNaming {
        TextField("Room name", text: $store.draftLabel)
          .textFieldStyle(.roundedBorder)
          .textInputAutocapitalization(.words)
      }

      action
        .buttonStyle(.borderedProminent)
        .controlSize(.large)
    }
    .padding()
    .frame(maxWidth: .infinity)
    .background(.regularMaterial, in: RoundedRectangle(cornerRadius: 20))
  }

  private var roomList: some View {
    VStack(alignment: .leading, spacing: 4) {
      Text(
        store.sessionRooms.count == 1
          ? "1 room scanned" : "\(store.sessionRooms.count) rooms scanned"
      )
      .font(.subheadline.weight(.semibold))
      ForEach(store.sessionRooms) { room in
        let frames = room.lidarRecording?.frames.count ?? 0
        Text(frames == 0 ? room.label : "\(room.label) · \(frames) LiDAR frames")
          .font(.footnote)
      }
    }
    .frame(maxWidth: .infinity, alignment: .leading)
  }

  @ViewBuilder
  private var action: some View {
    switch store.state {
    case .capturing:
      Button("Finish scan", systemImage: "stop.fill", action: store.stop)
    case .processing, .merging:
      ProgressView()
    case .exported:
      exportedActions
    case .ready:
      readyActions
    case .failed:
      failedActions
    case .unsupported:
      EmptyView()
    }
  }

  private var readyActions: some View {
    VStack(spacing: 8) {
      Button("Scan \(displayLabel)", systemImage: "viewfinder", action: store.start)
      if !store.sessionRooms.isEmpty {
        Button(
          "Export capture job", systemImage: "square.and.arrow.down", action: store.exportMerged
        )
        .buttonStyle(.bordered)
        Button("Start over", systemImage: "trash", action: store.reset)
          .buttonStyle(.bordered)
      }
    }
  }

  private var exportedActions: some View {
    VStack(spacing: 8) {
      if !store.exportURLs.isEmpty {
        ShareLink(items: store.exportURLs) {
          Label("Share capture job ZIP", systemImage: "square.and.arrow.up")
        }
      }
      Button("Scan \(displayLabel)", systemImage: "viewfinder", action: store.start)
        .buttonStyle(.bordered)
      Button("Start over", systemImage: "trash", action: store.reset)
        .buttonStyle(.bordered)
    }
  }

  private var failedActions: some View {
    VStack(spacing: 8) {
      Button("Scan \(displayLabel)", systemImage: "viewfinder", action: store.start)
      if store.sessionRooms.count >= 2 {
        Button(
          "Retry merge", systemImage: "arrow.triangle.2.circlepath", action: store.exportMerged
        )
        .buttonStyle(.bordered)
        Button(
          "Export without merging", systemImage: "square.and.arrow.down",
          action: store.exportUnmerged
        )
        .buttonStyle(.bordered)
      } else if !store.sessionRooms.isEmpty {
        Button(
          "Export capture job", systemImage: "square.and.arrow.down", action: store.exportMerged
        )
        .buttonStyle(.bordered)
      }
      if !store.sessionRooms.isEmpty {
        Button("Start over", systemImage: "trash", action: store.reset)
          .buttonStyle(.bordered)
      }
    }
  }

  private var displayLabel: String {
    let trimmed = store.draftLabel.trimmingCharacters(in: .whitespacesAndNewlines)
    return trimmed.isEmpty ? AppConfig.defaultLabel(forIndex: store.sessionRooms.count) : trimmed
  }
}
