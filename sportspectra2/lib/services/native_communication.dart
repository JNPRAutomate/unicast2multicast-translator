import 'package:flutter/services.dart';

class NativeCommunication {
  static const MethodChannel _channel = MethodChannel('com.example.live_stream');

  static Future<void> startCamera() async {
    try {
      await _channel.invokeMethod('startCamera');
    } on PlatformException catch (e) {
      print("Failed to start camera: '${e.message}'.");
    }
  }

  static Future<void> stopCamera() async {
    try {
      await _channel.invokeMethod('stopCamera');
    } on PlatformException catch (e) {
      print("Failed to stop camera: '${e.message}'.");
    }
  }
}