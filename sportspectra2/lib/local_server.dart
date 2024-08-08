import 'package:flutter/services.dart';

class LocalServer {
  static const MethodChannel _channel = MethodChannel('com.IsabelleXiong.sportspectra3/localswiftserver');

  static Future<void> start() async {
    try {
      print("[DEBUG] Starting local server...");
      await _channel.invokeMethod('startLocalServer');
      print("[INFO] Local server started");
    } on PlatformException catch (e) {
      print("[ERROR] Failed to start local server: ${e.message}");
    }
  }

  static Future<void> stop() async {
    try {
      print("[DEBUG] Stopping local server...");
      await _channel.invokeMethod('stopLocalServer');
      print("[INFO] Local server stopped");
    } on PlatformException catch (e) {
      print("[ERROR] Failed to stop local server: ${e.message}");
    }
  }
}