import 'dart:io';
import 'dart:typed_data';
import 'package:file_picker/file_picker.dart';
import 'package:flutter/foundation.dart';
import 'package:flutter/material.dart';

// The SnackBar widget: message briefly appears at the bottom of the screen to provide users with feedback on action
void showSnackBar(BuildContext context, String content) {
  // locates the nearest Scaffold widget in the widget tree and shows the SnackBar within it.
  ScaffoldMessenger.of(context).showSnackBar(
    SnackBar(content: Text(content)),
  );
}

// cannot use io package for web, so must use uint8list
// Uint8List: This is a type provided by the Dart SDK. It represents an immutable list of 8-bit unsigned integers. It's commonly used to represent binary data, such as images, in memory.
Future<Uint8List?> pickImage() async {
  FilePickerResult? pickedImage =
      await FilePicker.platform.pickFiles(type: FileType.image);

  if (pickedImage != null) {
    // image for web version
    if (kIsWeb) {
      return pickedImage.files.single.bytes;
    }
    // image for ios version
    return await File(pickedImage.files.single.path!).readAsBytes();
  }
  return null;
}
