import 'package:camera/camera.dart';
import 'package:flutter/foundation.dart';
import 'package:flutter/material.dart';
import 'package:flutter_ffmpeg/flutter_ffmpeg.dart';
import 'package:provider/provider.dart';
import 'package:sportspectra2/providers/stream_provider.dart' as my_provider;
import 'package:http/http.dart' as http;

class BroadcastScreen extends StatefulWidget {
  final bool isBroadcaster;
  final String channelId;

  const BroadcastScreen({
    Key? key,
    required this.isBroadcaster,
    required this.channelId,
  }) : super(key: key);

  @override
  _BroadcastScreenState createState() => _BroadcastScreenState();
}

class _BroadcastScreenState extends State<BroadcastScreen> {
  final FlutterFFmpeg _flutterFFmpeg = FlutterFFmpeg();
  bool _isMuted = false;
  bool _isStreaming = false;
  CameraController? _cameraController;
  List<CameraDescription>? cameras;

  @override
  void initState() {
    super.initState();
    if (kIsWeb) {
      _initializeCamera(); // Only initialize the camera for web
    }
    if (widget.isBroadcaster) {
      _startStream();
    }
  }

  Future<void> _initializeCamera() async {
    try {
      cameras = await availableCameras();
      _cameraController = CameraController(
        cameras![0],
        ResolutionPreset.high,
      );
      await _cameraController?.initialize();
      if (mounted) {
        setState(() {});
      }
    } catch (e) {
      print('Error initializing camera: $e');
    }
  }

  void _startStream() {
    if (kIsWeb) {
      _startWebStream();
    } else {
      _startFFmpegStream(); 
    }
  }

  Future<void> _startWebStream() async {
    try {
      final response = await http.post(
        Uri.parse('http://10.0.0.54:8000/start_web_stream/'),
        body: {
          'source_ip': '162.250.138.12', // Actual source IP
          'udp_port': '9001',            // Actual UDP port
          'is_web': 'true',
        },
      );
      if (response.statusCode == 200) {
        print('Streaming started successfully');
        setState(() {
          _isStreaming = true;
        });
      } else {
        print('Failed to start streaming: ${response.statusCode}');
        print('Response body: ${response.body}');
      }
    } catch (e) {
      print('Exception caught: $e');
    }
  }

  Future<void> _startFFmpegStream() async {
    final String streamUrl = "udp://162.250.138.12:9001?pkt_size=1316";
    final String command = 
        '-f avfoundation -framerate 30 -video_size 1280x720 -i "0:0" -f mpegts $streamUrl -loglevel debug';
    print("Starting FFmpeg stream with command: $command");

    setState(() {
      _isStreaming = true;
    });

    final int result = await _flutterFFmpeg.execute(command);
    print("FFmpeg execute result: $result");
    if (result != 0) {
      print('FFmpeg command failed with exit code: $result');
      setState(() {
        _isStreaming = false;
      });
    }
  }

  void _toggleMute() {
    setState(() {
      _isMuted = !_isMuted;
      print("Microphone toggled. Muted: $_isMuted");
    });
  }

  void _endStream(BuildContext context) {
    showDialog(
      context: context,
      builder: (context) {
        return AlertDialog(
          title: Text('End Stream'),
          content: Text('Are you sure you want to end this stream?'),
          actions: [
            TextButton(
              onPressed: () {
                Navigator.of(context).pop();
              },
              child: Text('Cancel'),
            ),
            TextButton(
              onPressed: () async {
                print('End Stream button pressed');
                print('Channel ID: ${widget.channelId}');
                final provider = Provider.of<my_provider.StreamProvider>(
                    context,
                    listen: false);
                await provider.deleteStream(channelId: widget.channelId);
                print('Delete stream request sent');

                if (kIsWeb) {
                  _stopWebStream();
                } else {
                  _flutterFFmpeg.cancel();
                }
                setState(() {
                  _isStreaming = false;
                });

                Navigator.of(context).pop(); // Close the dialog
                Navigator.of(context).pop(); // Navigate back to the feed screen
              },
              child: Text('End Stream'),
            ),
          ],
        );
      },
    );
  }

  Future<void> _stopWebStream() async {
    try {
      final response = await http.post(
        Uri.parse('http://10.0.0.54:8000/stop_web_stream/'),
      );
      if (response.statusCode == 200) {
        print('Streaming stopped successfully');
      } else {
        print('Failed to stop streaming: ${response.statusCode}');
        print('Response body: ${response.body}');
      }
    } catch (e) {
      print('Exception caught: $e');
    }
  }

  @override
  void dispose() {
    _cameraController?.dispose();
    if (widget.isBroadcaster) {
      if (!kIsWeb) {
        _flutterFFmpeg.cancel();
      }
      print("Disposed local renderer and stream");
    }
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: Text('Broadcast Screen'),
        actions: widget.isBroadcaster
            ? [
                ElevatedButton(
                  onPressed: () => _endStream(context),
                  child: Text(
                    'End Stream',
                    style: TextStyle(color: Colors.purple),
                  ),
                ),
                IconButton(
                  icon: Icon(_isMuted ? Icons.mic_off : Icons.mic),
                  onPressed: _toggleMute,
                ),
                if (kIsWeb) // Only show the switch camera button for web
                  IconButton(
                    icon: Icon(Icons.switch_camera),
                    onPressed: _switchCamera,
                  ),
              ]
            : null,
      ),
      body: widget.isBroadcaster
          ? Stack(
              children: [
                if (kIsWeb)
                  _cameraController != null && _cameraController!.value.isInitialized
                      ? CameraPreview(_cameraController!)
                      : Center(child: CircularProgressIndicator()),
                Positioned(
                  top: 20,
                  right: 20,
                  child: Column(
                    children: [
                      if (kIsWeb) // Only show the switch camera button for web
                        IconButton(
                          icon: Icon(Icons.switch_camera, color: Colors.white),
                          onPressed: _switchCamera,
                        ),
                      IconButton(
                        icon: Icon(
                          _isMuted ? Icons.mic_off : Icons.mic,
                          color: _isMuted ? Colors.red : Colors.white,
                        ),
                        onPressed: _toggleMute,
                      ),
                    ],
                  ),
                ),
              ],
            )
          : Center(child: Text('Live stream view for viewers')),
    );
  }

  Future<void> _switchCamera() async {
    if (!kIsWeb) return; // Do nothing if not on the web
    print("Switching camera...");
    if (_cameraController == null || !(_cameraController?.value.isInitialized ?? false) || cameras == null) {
      return;
    }
    final currentIndex = cameras!.indexOf(_cameraController!.description);
    final newIndex = (currentIndex + 1) % cameras!.length;
    _cameraController = CameraController(cameras![newIndex], ResolutionPreset.high);
    await _cameraController?.initialize();
    setState(() {});
  }
}