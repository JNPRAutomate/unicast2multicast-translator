import 'package:flutter/material.dart';
import 'package:video_player/video_player.dart';
import 'package:chewie/chewie.dart';
import 'package:path_provider/path_provider.dart';
import 'package:flutter/services.dart';
import 'dart:io';
import 'package:shelf/shelf_io.dart' as io;
import 'package:shelf_static/shelf_static.dart';
import '../../local_server.dart';

class VideoScreen extends StatefulWidget {
  final String streamId;

  const VideoScreen({Key? key, required this.streamId}) : super(key: key);

  @override
  _VideoScreenState createState() => _VideoScreenState();
}

class _VideoScreenState extends State<VideoScreen> {
  late VideoPlayerController _videoPlayerController;
  ChewieController? _chewieController;
  HttpServer? _server;
  String _serverUrl = '';
  String _localIp = '10.0.0.54';
  //brandywine
  // String _localIp = '192.168.2.110';

   @override
  void initState() {
    super.initState();
    print('Navigated to VideoScreen with stream ID: ${widget.streamId}');
    LocalServer.start();  // Start the local server
    _startLocalServer();  // This method can be renamed if needed
  }

  @override
  void dispose() {
    LocalServer.stop();  // Stop the local server
    _videoPlayerController.dispose();
    _chewieController?.dispose();
    _server?.close();
    super.dispose();
  }

  Future<void> _startLocalServer() async {
    final Directory tempDir = await getTemporaryDirectory();
    final String tempPath = tempDir.path;

    // Create a simple text file for testing
    final File testFile = File('$tempPath/test.txt');
    await testFile.writeAsString('This is a test file.');

    // Copy the .m3u8 and .ts files to the temporary directory
    await _copyAssetsToTemp(tempPath);

    // Create a handler to serve static files from the temporary directory
    var handler = createStaticHandler(tempPath, defaultDocument: 'index${widget.streamId}.m3u8');

    // Start the HTTP server on any available network interface
    _server = await io.serve(handler, InternetAddress.anyIPv4, 0);
    if (_server != null) {
      _serverUrl = 'http://${_localIp}:${_server!.port}/index${widget.streamId}.m3u8';
      print('Local server started at $_serverUrl');
      _initializePlayer();
    } else {
      print('Error starting local server');
    }
  }

  Future<void> _copyAssetsToTemp(String tempPath) async {
    final String streamId = widget.streamId;
    final String m3u8AssetPath = 'assets/media/index$streamId.m3u8';
    
    print('Attempting to load video segments from URL: $m3u8AssetPath');

    try {
      // Load the .m3u8 file as a string
      final String m3u8Content = await rootBundle.loadString(m3u8AssetPath);
      print('Loaded m3u8 content: $m3u8Content');

      // Write the .m3u8 file to the temporary directory
      final File m3u8File = File('$tempPath/index$streamId.m3u8');
      String updatedM3u8Content = m3u8Content;

      // Copy .ts files to the temporary directory and update m3u8 paths
      for (String line in m3u8Content.split('\n')) {
        if (line.endsWith('.ts')) {
          final String tsAssetPath = 'assets/media/$line';
          print('Loading ts file from: $tsAssetPath');
          try {
            final ByteData data = await rootBundle.load(tsAssetPath);
            final List<int> bytes = data.buffer.asUint8List();
            final File tsFile = File('$tempPath/$line');
            await tsFile.writeAsBytes(bytes);
            updatedM3u8Content = updatedM3u8Content.replaceAll(line, line);
            print('Copied ts file to temporary directory: ${tsFile.path}');
          } catch (e) {
            print('Error loading ts file: $tsAssetPath. Error: $e');
          }
        }
      }

      await m3u8File.writeAsString(updatedM3u8Content);
    } catch (e) {
      print('Error loading or copying video files: $e');
    }
  }

  Future<void> _initializePlayer() async {
    try {
      print('Initializing video player with URL: $_serverUrl');
      _videoPlayerController = VideoPlayerController.networkUrl(Uri.parse(_serverUrl));
      await _videoPlayerController.initialize();
      _createChewieController();
    } catch (e) {
      print('Error initializing video player: $e');
    }
  }

  void _createChewieController() {
    _chewieController = ChewieController(
      videoPlayerController: _videoPlayerController,
      autoPlay: true,
      looping: true,
    );
    setState(() {});
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: Text('Video Player'),
      ),
      body: Center(
        child: _chewieController != null &&
                _chewieController!.videoPlayerController.value.isInitialized
            ? Chewie(
                controller: _chewieController!,
              )
            : Column(
                mainAxisAlignment: MainAxisAlignment.center,
                children: const [
                  CircularProgressIndicator(),
                  SizedBox(height: 20),
                  Text('Loading...'),
                ],
              ),
      ),
    );
  }
}