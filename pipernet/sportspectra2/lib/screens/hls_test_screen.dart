import 'package:flutter/material.dart';
import 'package:video_player/video_player.dart';
import 'package:chewie/chewie.dart';

void main() {
  runApp(MyApp());
}

class MyApp extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      home: HlsTestScreen(),
    );
  }
}

class HlsTestScreen extends StatefulWidget {
  @override
  _HlsTestScreenState createState() => _HlsTestScreenState();
}

class _HlsTestScreenState extends State<HlsTestScreen> {
  VideoPlayerController? _videoPlayerController;
  ChewieController? _chewieController;
  bool _isLoading = false;
  bool _isInitialized = false;

  @override
  void dispose() {
    _videoPlayerController?.dispose();
    _chewieController?.dispose();
    super.dispose();
  }

  Future<void> _initializePlayer(String url) async {
    setState(() {
      _isLoading = true;
    });

    print("Initializing player with URL: $url");

    _videoPlayerController = VideoPlayerController.network(url);
    try {
      await _videoPlayerController!.initialize();
      _chewieController = ChewieController(
        videoPlayerController: _videoPlayerController!,
        aspectRatio: 16 / 9,
        autoPlay: true,
        looping: false,
      );

      setState(() {
        _isLoading = false;
        _isInitialized = true;
      });
    } catch (e) {
      print("Error initializing video player: $e");
      setState(() {
        _isLoading = false;
        _isInitialized = false;
      });
    }
  }

  @override
  void initState() {
    super.initState();
    _initializePlayer(
        'https://bitdash-a.akamaihd.net/content/sintel/hls/playlist.m3u8');
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: Text('HLS Test Screen'),
      ),
      body: Padding(
        padding: const EdgeInsets.all(16.0),
        child: Column(
          children: [
            _isLoading
                ? CircularProgressIndicator()
                : _isInitialized
                    ? Expanded(
                        child: Chewie(
                          controller: _chewieController!,
                        ),
                      )
                    : Container(),
          ],
        ),
      ),
    );
  }
}
