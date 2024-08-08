import 'dart:io';
import 'dart:math';
import 'package:flutter/foundation.dart';
import 'package:flutter/material.dart';
import 'package:file_picker/file_picker.dart';
import 'package:image_picker/image_picker.dart';
import '../models/stream.dart';
import '../providers/stream_provider.dart' as my_provider;
import '../services/network_service.dart';
import 'package:process_run/process_run.dart';
import 'package:flutter_ffmpeg/flutter_ffmpeg.dart';
import 'package:http/http.dart' as http;
import 'dart:convert';

class AnUploadedFileScreen extends StatefulWidget {
  final TextEditingController thumbnailController;

  const AnUploadedFileScreen({Key? key, required this.thumbnailController})
      : super(key: key);

  @override
  _AnUploadedFileScreenState createState() => _AnUploadedFileScreenState();
}

class _AnUploadedFileScreenState extends State<AnUploadedFileScreen> {
  String? _selectedCategory;
  final TextEditingController _organizationController = TextEditingController();
  final TextEditingController _descriptionController = TextEditingController();
  final TextEditingController _titleController = TextEditingController();
  dynamic _videoFile;
  String? _videoFileName;
  bool _isUploading = false;
  final NetworkService _networkService = NetworkService();
  bool _isWeb = false;

  String _sourceIp = '';
  String _groupIp = '';
  String _udpPort = '';
  final String _amtRelay = 'amt-relay.m2icast.net';

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

    Future<void> _pickVideoFile() async {
    if (kIsWeb) {
      // Use ImagePicker for web
      final ImagePicker _picker = ImagePicker();
      final XFile? pickedFile = await _picker.pickVideo(
        source: ImageSource.gallery,
      );

      if (pickedFile != null) {
        setState(() {
          _videoFile = File(pickedFile.path);
          _videoFileName = pickedFile.name;
          _isWeb = true; // Set the flag to indicate web upload
        });
      } else {
        print('No video file selected.');
      }
    } else {
      // Use FilePicker for mobile
      FilePickerResult? result = await FilePicker.platform.pickFiles(
        type: FileType.video,
      );

      if (result != null) {
        setState(() {
          _videoFile = File(result.files.single.path!);
          _videoFileName = result.files.single.name;
          _isWeb = false; // Set the flag to indicate mobile upload
        });
      } else {
        print('No video file selected.');
      }
    }
  }

  Future<void> _uploadFiles() async {
  _groupIp = _generateMulticastGroupIp();
  _udpPort = _generateUdpPort().toString();

  print('Generated Group IP: $_groupIp');
  print('Generated UDP Port: $_udpPort');
  print('AMT Relay: $_amtRelay');

  if (_videoFile == null || widget.thumbnailController.text.isEmpty) {
    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(
          content: Text('Please choose a video file and enter a thumbnail URL')),
    );
    setState(() {
      _isUploading = false;
    });
    return;
  }

  print('Starting upload...');
  print('Uploading with the following details:');
  print('Title: ${_titleController.text}');
  print('Organization: ${_organizationController.text}');
  print('Description: ${_descriptionController.text}');
  print('Category: ${_selectedCategory ?? 'Other'}');
  print('Thumbnail URL: ${widget.thumbnailController.text}');
  print('Video File Path: ${_videoFile?.path}');
  print('Source IP: $_sourceIp');
  print('Group IP: $_groupIp');
  print('UDP Port: $_udpPort');
  print('AMT Relay: $_amtRelay');

  setState(() {
    _isUploading = true;
  });

  try {
    // Upload stream metadata immediately
    final response = await _networkService.addStream(
      title: _titleController.text,
      organization: _organizationController.text,
      description: _descriptionController.text,
      category: _selectedCategory ?? 'Other',
      image: widget.thumbnailController.text,
      videoFilePath: null, // Set to null to skip upload
      sourceIp: _sourceIp,
      groupIp: _groupIp,
      udpPort: _udpPort,
      amtRelay: 'amt-relay.m2icast.net',
      status: 'New',
      isWeb: _isWeb,
      
    );
      // Handle the rest of the response
    var newStream = StreamModel(
      id: response['id'],
      channelId: response['channel_id'],
      title: _titleController.text,
      description: _descriptionController.text,
      category: _selectedCategory ?? 'Other',
      status: 'New',
      image: widget.thumbnailController.text,
      viewers: 0,
      organization: _organizationController.text,
      sourceIp: _sourceIp,
      groupIp: _groupIp,
      udpPort: _udpPort,
      amtRelay: 'amt-relay.m2icast.net',
    );

    print('New Stream Channel ID: ${newStream.channelId}');

    print('Stream metadata uploaded successfully.');
    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(content: Text('Stream metadata uploaded successfully')),
    );

    Navigator.pop(context); // Immediately pop back to the previous screen

     if (!_isWeb) {
        // Only run FFmpeg command if not on web
        Future.delayed(Duration.zero, () async {
          print('Running FFmpeg command');
          await _runFFmpegCommand(_videoFile!.path, '162.250.138.12', '9001');
          print('FFmpeg command completed');
        });
      }
    } catch (e) {
      print('Upload error: $e');
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text('An error occurred during upload')),
      );
    } finally {
      setState(() {
        _isUploading = false;
      });
    }
}

  Future<void> _runFFmpegCommand(String videoFilePath, String ip, String port) async {
  final FlutterFFmpeg _flutterFFmpeg = FlutterFFmpeg();
  final cmd = '-stream_loop -1 -re -i $videoFilePath -c:v copy -c:a copy -f mpegts "udp://$ip:$port?pkt_size=1316" -loglevel debug';
  
  final int result = await _flutterFFmpeg.execute(cmd);
  if (result != 0) {
    throw Exception('FFmpeg command failed with exit code: $result');
  }
}

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: Text('Upload File'),
      ),
      body: Padding(
        padding: const EdgeInsets.all(16.0),
        child: SingleChildScrollView(
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.stretch,
            children: [
              Text(
                'Upload the video file you wish to stream.',
                style: TextStyle(fontSize: 18),
              ),
              SizedBox(height: 20),
              Text(
                'Title:',
                style: TextStyle(fontSize: 16),
              ),
              SizedBox(height: 8),
              TextFormField(
                controller: _titleController,
                decoration: InputDecoration(
                  border: OutlineInputBorder(),
                  hintText: 'Enter Title',
                ),
              ),
              SizedBox(height: 20),
              Text(
                'Name of originating organization:',
                style: TextStyle(fontSize: 16),
              ),
              SizedBox(height: 8),
              TextFormField(
                controller: _organizationController,
                decoration: InputDecoration(
                  border: OutlineInputBorder(),
                  hintText: 'Enter name',
                ),
              ),
              SizedBox(height: 20),
              Text(
                'Description of stream:',
                style: TextStyle(fontSize: 16),
              ),
              SizedBox(height: 8),
              TextFormField(
                controller: _descriptionController,
                maxLines: 3,
                decoration: InputDecoration(
                  border: OutlineInputBorder(),
                  hintText: 'Enter description',
                ),
              ),
              SizedBox(height: 20),
              Text(
                'Category:',
                style: TextStyle(fontSize: 16),
              ),
              SizedBox(height: 8),
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
                onPressed: _pickVideoFile,
                child: Text('Choose video file'),
              ),
              if (_videoFileName != null) ...[
                SizedBox(height: 8),
                Text(
                  'Selected video file: $_videoFileName',
                  style: TextStyle(fontSize: 16, fontWeight: FontWeight.bold),
                ),
              ],
              SizedBox(height: 20),
              Text(
                'Thumbnail URL:',
                style: TextStyle(fontSize: 16),
              ),
              SizedBox(height: 8),
              TextFormField(
                controller: widget.thumbnailController,
                decoration: InputDecoration(
                  border: OutlineInputBorder(),
                  hintText: 'Enter thumbnail URL',
                ),
              ),
              SizedBox(height: 20),
              ElevatedButton(
                onPressed: _isUploading || _sourceIp.isEmpty
                    ? null
                    : () {
                        print('Submit button pressed');
                        _uploadFiles();
                      },
                child: Text(_isUploading ? 'Uploading...' : 'Submit'),
              ),
            ],
          ),
        ),
      ),
    );
  }
}