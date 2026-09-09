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

      action
        .buttonStyle(.borderedProminent)
        .controlSize(.large)
    }
    .padding()
    .frame(maxWidth: .infinity)
    .background(.regularMaterial, in: RoundedRectangle(cornerRadius: 20))
  }

  @ViewBuilder
  private var action: some View {
    switch store.state {
    case .capturing:
      Button("Finish scan", systemImage: "stop.fill", action: store.stop)
    case .processing:
      ProgressView()
    case .exported:
      if let exportURL = store.exportURL {
        VStack(spacing: 8) {
          ShareLink(item: exportURL) {
            Label("Share roomplan.json", systemImage: "square.and.arrow.up")
          }
          Button("Scan again", systemImage: "arrow.clockwise", action: store.start)
            .buttonStyle(.bordered)
        }
      }
    case .ready, .failed:
      Button("Start scan", systemImage: "viewfinder", action: store.start)
    case .unsupported:
      EmptyView()
    }
  }
}
