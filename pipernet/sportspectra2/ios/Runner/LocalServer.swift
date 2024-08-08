import GCDWebServer

@objc class LocalServer: NSObject {
  var webServer: GCDWebServer?

  func start() {
    webServer = GCDWebServer()

    // Create a simple text file in the temporary directory for testing
    let tempDir = NSTemporaryDirectory()
    let testFilePath = (tempDir as NSString).appendingPathComponent("test.txt")
    let testContent = "Hello, world!"
    do {
      try testContent.write(toFile: testFilePath, atomically: true, encoding: .utf8)
      print("[INFO] Created test file at \(testFilePath)")
    } catch {
      print("[ERROR] Could not create test file: \(error.localizedDescription)")
    }

    // Add a simple handler to serve a text response
    webServer?.addHandler(forMethod: "GET", path: "/test", request: GCDWebServerRequest.self, processBlock: { request in
      return GCDWebServerDataResponse(text: "Hello, world!")
    })

    // Add the existing handler to serve files from the temporary directory
    webServer?.addGETHandler(forBasePath: "/", directoryPath: tempDir, indexFilename: nil, cacheAge: 3600, allowRangeRequests: true)

    do {
      try webServer?.start(options: [
        GCDWebServerOption_BindToLocalhost: false,
        GCDWebServerOption_Port: 8080,
        GCDWebServerOption_BonjourName: "Local Web Server"
      ])
      if let address = getWiFiAddress() {
        print("[INFO] GCDWebServer started on port 8080 and reachable at http://\(address):8080/")
      }
    } catch {
      print("[ERROR] Error starting GCDWebServer: \(error.localizedDescription)")
    }
  }

  func stop() {
    webServer?.stop()
    print("[INFO] GCDWebServer stopped")
  }

  func getWiFiAddress() -> String? {
    var address: String?
    var ifaddr: UnsafeMutablePointer<ifaddrs>?
    if getifaddrs(&ifaddr) == 0 {
      var ptr = ifaddr
      while ptr != nil {
        let interface = ptr!.pointee
        if interface.ifa_addr.pointee.sa_family == UInt8(AF_INET) {
          let name = String(cString: interface.ifa_name)
          if name == "en0" {
            var addr = interface.ifa_addr.pointee
            var hostname = [CChar](repeating: 0, count: Int(NI_MAXHOST))
            getnameinfo(&addr, socklen_t(interface.ifa_addr.pointee.sa_len),
                        &hostname, socklen_t(hostname.count),
                        nil, socklen_t(0), NI_NUMERICHOST)
            address = String(cString: hostname)
          }
        }
        ptr = interface.ifa_next
      }
      freeifaddrs(ifaddr)
    }
    return address
  }
}