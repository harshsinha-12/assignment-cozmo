import SwiftUI

struct PhotoCaptureView: View {
  @StateObject private var store = PhotoCaptureStore()

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
      Text("Photos")
        .font(.headline)
      Text(guidance)
        .font(.footnote)
        .multilineTextAlignment(.center)
        .foregroundStyle(.secondary)

      if !store.rooms.isEmpty || !store.pendingJPEGs.isEmpty {
        VStack(alignment: .leading, spacing: 4) {
          ForEach(store.rooms) { room in
            Text("\(room.label) · \(room.jpegs.count) stills")
              .font(.footnote)
          }
          if !store.pendingJPEGs.isEmpty {
            Text("Current room · \(store.pendingJPEGs.count) / \(AppConfig.maxPhotosPerRoom)")
              .font(.footnote.monospacedDigit())
          }
        }
        .frame(maxWidth: .infinity, alignment: .leading)
      }

      if store.state.allowsNaming {
        TextField("Room name", text: $store.draftLabel)
          .textFieldStyle(.roundedBorder)
          .textInputAutocapitalization(.words)
      }

      Button("Capture still", systemImage: "camera", action: store.capturePhoto)
        .buttonStyle(.borderedProminent)
        .controlSize(.large)
        .disabled(!store.canCapture)

      HStack {
        Button("Finish room", action: store.finishRoom)
          .disabled(store.pendingJPEGs.count < AppConfig.minPhotosPerRoom)
        Button("Export photo job", action: store.exportJob)
          .disabled(store.rooms.isEmpty || !store.pendingJPEGs.isEmpty)
      }
      .buttonStyle(.bordered)

      if !store.exportURLs.isEmpty {
        ShareLink(items: store.exportURLs) {
          Label("Share photo job ZIP", systemImage: "square.and.arrow.up")
        }
      }

      if !store.rooms.isEmpty || !store.pendingJPEGs.isEmpty {
        Button("Start over", systemImage: "trash", action: store.reset)
          .buttonStyle(.bordered)
      }
    }
    .padding()
    .frame(maxWidth: .infinity)
    .background(.regularMaterial, in: RoundedRectangle(cornerRadius: 20))
  }

  private var guidance: String {
    if case .failed(let message) = store.state {
      return message
    }
    if store.state == .exported {
      return "Share the photo ZIP; the CLI expects photos/<room>/01.jpg …"
    }
    return "Shoot 2–8 overlapping stills per room: doorway, each wall, through-door, ceiling."
  }
}
