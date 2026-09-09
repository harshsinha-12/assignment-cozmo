import SwiftUI

struct VideoCaptureView: View {
  @StateObject private var store = VideoCaptureStore()

  var body: some View {
    ZStack(alignment: .bottom) {
      CameraPreview(session: store.session)
        .ignoresSafeArea()
      controls
        .padding()
    }
    .onAppear(perform: store.startSession)
    .onDisappear(perform: store.stopSession)
  }

  private var controls: some View {
    VStack(spacing: 12) {
      Text("Video")
        .font(.headline)
      Text(guidance)
        .font(.footnote)
        .multilineTextAlignment(.center)
        .foregroundStyle(.secondary)

      if !store.clips.isEmpty {
        VStack(alignment: .leading, spacing: 4) {
          ForEach(store.clips) { clip in
            Text(clip.label)
              .font(.footnote)
          }
        }
        .frame(maxWidth: .infinity, alignment: .leading)
      }

      if store.state.allowsNaming && !store.isRecording {
        TextField("Room name", text: $store.draftLabel)
          .textFieldStyle(.roundedBorder)
          .textInputAutocapitalization(.words)
      }

      Button(
        store.isRecording ? "Stop recording" : "Record \(displayLabel)",
        systemImage: store.isRecording ? "stop.fill" : "record.circle",
        action: store.toggleRecording
      )
      .buttonStyle(.borderedProminent)
      .controlSize(.large)

      Button("Export video job", action: store.exportJob)
        .buttonStyle(.bordered)
        .disabled(store.clips.isEmpty || store.isRecording)

      if !store.exportURLs.isEmpty {
        ShareLink(items: store.exportURLs) {
          Label("Share video job ZIP", systemImage: "square.and.arrow.up")
        }
      }

      if !store.clips.isEmpty && !store.isRecording {
        Button("Start over", systemImage: "trash", action: store.reset)
          .buttonStyle(.bordered)
      }
    }
    .padding()
    .frame(maxWidth: .infinity)
    .background(.regularMaterial, in: RoundedRectangle(cornerRadius: 20))
  }

  private var displayLabel: String {
    let trimmed = store.draftLabel.trimmingCharacters(in: .whitespacesAndNewlines)
    return trimmed.isEmpty ? AppConfig.defaultLabel(forIndex: store.clips.count) : trimmed
  }

  private var guidance: String {
    if case .failed(let message) = store.state {
      return message
    }
    if store.isRecording {
      return "Walk the perimeter slowly. Pause at corners and keep recording through doorways."
    }
    if store.state == .exported {
      return "Share the video ZIP; metric centimetres still need a calibrated pose sidecar."
    }
    return "One continuous walkthrough per named room. Rear camera, chest height."
  }
}
