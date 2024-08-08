import Flutter
import UIKit
import GCDWebServer

public class SwiftLocalServerPlugin: NSObject, FlutterPlugin {
  var webServer: GCDWebServer?

  public static func register(with registrar: FlutterPluginRegistrar) {
    let channel = FlutterMethodChannel(name: "com.IsabelleXiong.sportspectra3/localswiftserver", binaryMessenger: registrar.messenger())
    let instance = SwiftLocalServerPlugin()
    registrar.addMethodCallDelegate(instance, channel: channel)
  }

  public func handle(_ call: FlutterMethodCall, result: @escaping FlutterResult) {
    if call.method == "startLocalServer" {
      startLocalServer(result: result)
    } else if call.method == "stopLocalServer" {
      stopLocalServer(result: result)
    } else {
      result(FlutterMethodNotImplemented)
    }
  }

  private func startLocalServer(result: FlutterResult) {
    webServer = GCDWebServer()
    webServer?.addGETHandler(forBasePath: "/", directoryPath: NSTemporaryDirectory(), indexFilename: nil, cacheAge: 3600, allowRangeRequests: true)

    do {
      try webServer?.start(options: [
        GCDWebServerOption_BindToLocalhost: true,
        GCDWebServerOption_Port: 8080
      ])
      result(nil)
    } catch {
      result(FlutterError(code: "SERVER_ERROR", message: "Error starting local server", details: error.localizedDescription))
    }
  }

  private func stopLocalServer(result: FlutterResult) {
    webServer?.stop()
    result(nil)
  }
}