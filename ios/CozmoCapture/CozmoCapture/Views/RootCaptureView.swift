import SwiftUI

struct RootCaptureView: View {
  @State private var mode = CaptureMode.lidar

  var body: some View {
    ZStack(alignment: .top) {
      Group {
        switch mode {
        case .lidar:
          CaptureView()
        case .photos:
          PhotoCaptureView()
        case .video:
          VideoCaptureView()
        }
      }

      Picker("Capture tier", selection: $mode) {
        ForEach(CaptureMode.allCases) { option in
          Text(option.title).tag(option)
        }
      }
      .pickerStyle(.segmented)
      .padding(.horizontal)
      .padding(.top, 8)
    }
  }
}
