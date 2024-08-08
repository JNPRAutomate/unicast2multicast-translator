import 'dart:math';
import 'package:flutter/foundation.dart';
import 'package:flutter/material.dart';
import 'package:dio/dio.dart';
import '../services/network_service.dart';

class VideoUrlScreen extends StatefulWidget {
  @override
  _VideoUrlScreenState createState() => _VideoUrlScreenState();
}

class _VideoUrlScreenState extends State<VideoUrlScreen> {
  final TextEditingController _urlController = TextEditingController();
  final TextEditingController _thumbnailController =
      TextEditingController(); // Thumbnail URL controller
  final TextEditingController _titleController = TextEditingController();
  final TextEditingController _organizationController = TextEditingController();
  final TextEditingController _descriptionController = TextEditingController();
  String? _selectedCategory;
  bool _isUploading = false;
  final NetworkService _networkService = NetworkService();
  String _sourceIp = '';
  String _udpPort = '';

  @override
  void initState() {
    super.initState();
    _fetchPublicIpAddress();
  }

  Future<void> _fetchPublicIpAddress() async {
    String ip = await _networkService.getPublicIPAddress();
    setState(() {
      _sourceIp = ip;
    });
    print('Public IP: $_sourceIp');
  }

  static String _generateMulticastGroupIp() {
    return '232.255.${_randomNumber(0, 255)}.${_randomNumber(1, 255)}';
  }

  static int _generateUdpPort() {
    return _randomNumber(1024, 65535);
  }

  static int _randomNumber(int min, int max) {
    final random = Random();
    return min + random.nextInt(max - min);
  }

  Future<void> _streamVideoUrl() async {
    _sourceIp = '162.250.138.12';
    _udpPort = '9001';

    if (_urlController.text.isEmpty || _thumbnailController.text.isEmpty) {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text('Please enter a video URL and thumbnail URL')),
      );
      setState(() {
        _isUploading = false;
      });
      return;
    }

    print('Starting stream...');
    setState(() {
      _isUploading = true;
    });

    try {
      if (kIsWeb) {
        await _startStreamingOnServer(_urlController.text, _sourceIp, _udpPort);
      } else {
        await _startStreamingOnServer(_urlController.text, _sourceIp, _udpPort);
      }

      print('Stream started successfully');
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text('Stream started successfully')),
      );

      // Navigate back to the Add Stream screen
      Navigator.pop(context);
    } catch (e) {
      print('Stream error: $e');
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text('An error occurred during streaming')),
      );
    } finally {
      setState(() {
        _isUploading = false;
      });
    }
  }

  Future<void> _startStreamingOnServer(
      String videoUrl, String ip, String port) async {
    try {
      Dio dio = Dio();
      final response = await dio.post(
        'http://10.0.0.54:8000/stream_video_url/',
        data: {
          'video_url': videoUrl,
          'source_ip': ip,
          'udp_port': port,
        },
        options: Options(
          headers: {
            "Content-Type": "application/x-www-form-urlencoded",
          },
        ),
      );

      if (response.statusCode == 200) {
        print('Streaming command executed successfully on the server');
      } else {
        print(
            'Failed to start streaming on the server: ${response.statusCode}');
      }
    } catch (e) {
      print('Exception caught while starting streaming on the server: $e');
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: Text('Stream Video URL'),
      ),
      body: Padding(
        padding: const EdgeInsets.all(16.0),
        child: SingleChildScrollView(
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.stretch,
            children: [
              Text(
                'Enter the video URL and thumbnail URL you wish to stream.',
                style: TextStyle(fontSize: 18),
              ),
              SizedBox(height: 20),
              TextFormField(
                controller: _urlController,
                decoration: InputDecoration(
                  border: OutlineInputBorder(),
                  hintText: 'Enter Video URL',
                ),
              ),
              SizedBox(height: 20),
              TextFormField(
                controller: _thumbnailController,
                decoration: InputDecoration(
                  border: OutlineInputBorder(),
                  hintText: 'Enter Thumbnail URL',
                ),
              ),
              SizedBox(height: 20),
              TextFormField(
                controller: _titleController,
                decoration: InputDecoration(
                  border: OutlineInputBorder(),
                  hintText: 'Enter Title',
                ),
              ),
              SizedBox(height: 20),
              TextFormField(
                controller: _organizationController,
                decoration: InputDecoration(
                  border: OutlineInputBorder(),
                  hintText: 'Enter Organization',
                ),
              ),
              SizedBox(height: 20),
              TextFormField(
                controller: _descriptionController,
                maxLines: 3,
                decoration: InputDecoration(
                  border: OutlineInputBorder(),
                  hintText: 'Enter Description',
                ),
              ),
              SizedBox(height: 20),
              DropdownButton<String>(
                value: _selectedCategory,
                onChanged: (String? newValue) {
                  setState(() {
                    _selectedCategory = newValue;
                  });
                },
                items: <String>['Educational', 'Nature', 'Technology', 'Music']
                    .map<DropdownMenuItem<String>>((String value) {
                  return DropdownMenuItem<String>(
                    value: value,
                    child: Text(value),
                  );
                }).toList(),
              ),
              SizedBox(height: 20),
              ElevatedButton(
                onPressed: _isUploading || _sourceIp.isEmpty
                    ? null
                    : () {
                        print('Submit button pressed');
                        _streamVideoUrl();
                      },
                child: Text(_isUploading ? 'Streaming...' : 'Submit'),
              ),
            ],
          ),
        ),
      ),
    );
  }
}

