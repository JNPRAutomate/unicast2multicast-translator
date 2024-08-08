import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../models/stream.dart';
import '../providers/stream_provider.dart' as my_provider;
import '../services/network_service.dart';
import 'dart:math';
import 'broadcast_screen.dart';

class GoLiveScreen extends StatefulWidget {
  @override
  _GoLiveScreenState createState() => _GoLiveScreenState();
}

class _GoLiveScreenState extends State<GoLiveScreen> {
  final TextEditingController _titleController = TextEditingController();
  final TextEditingController _thumbnailController = TextEditingController();
  final TextEditingController _descriptionController = TextEditingController();
  final TextEditingController _organizationController = TextEditingController();
  String? _selectedCategory;

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
    String ip = await NetworkService().getPublicIPAddress();
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

  Future<void> _goLive(BuildContext context) async {
    if (_titleController.text.isEmpty ||
        _thumbnailController.text.isEmpty ||
        _organizationController.text.isEmpty ||
        _descriptionController.text.isEmpty ||
        _selectedCategory == null) {
      ScaffoldMessenger.of(context)
          .showSnackBar(SnackBar(content: Text('Please fill all fields')));
      return;
    }

    _groupIp = _generateMulticastGroupIp();
    _udpPort = _generateUdpPort().toString();

    var newStream = StreamModel(
      id: null,
      channelId: '',
      title: _titleController.text,
      description: _descriptionController.text,
      category: _selectedCategory!,
      image: _thumbnailController.text,
      organization: _organizationController.text,
      status: 'Live',
      viewers: 0,
      sourceIp: _sourceIp,
      groupIp: _groupIp,
      udpPort: _udpPort,
      amtRelay: _amtRelay,
    );

    print('New Stream before uploading: $newStream');

    var response = await context.read<my_provider.StreamProvider>().addStream(newStream);

    newStream = StreamModel(
      id: response['id'],
      channelId: response['channel_id'],
      title: newStream.title,
      description: newStream.description,
      category: newStream.category,
      image: newStream.image,
      organization: newStream.organization,
      status: newStream.status,
      viewers: newStream.viewers,
      sourceIp: newStream.sourceIp,
      groupIp: newStream.groupIp,
      udpPort: newStream.udpPort,
      amtRelay: newStream.amtRelay,
    );

    print('New Stream Channel ID: ${newStream.channelId}');

    await context.read<my_provider.StreamProvider>().loadStreams();

    Navigator.pop(context);

    Navigator.push(
      context,
      MaterialPageRoute(
        builder: (context) => BroadcastScreen(
          isBroadcaster: true,
          channelId: newStream.channelId,
        ),
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: Text('Go Live'),
      ),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(16.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            buildTextField('Title', _titleController),
            buildTextField('Thumbnail URL', _thumbnailController),
            buildTextField('Organization', _organizationController),
            buildTextField('Description', _descriptionController, maxLines: 3),
            buildCategoryDropdown(),
            SizedBox(height: 20),
            ElevatedButton(
              onPressed: _sourceIp.isEmpty
                  ? null
                  : () => _goLive(context),
              child: Text('Go Live'),
              style: ElevatedButton.styleFrom(
                padding: EdgeInsets.symmetric(vertical: 12),
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget buildTextField(String label, TextEditingController controller,
      {int maxLines = 1}) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(label, style: TextStyle(fontSize: 16)),
        SizedBox(height: 8),
        TextField(
          controller: controller,
          decoration: InputDecoration(
              border: OutlineInputBorder(), hintText: 'Enter $label'),
          maxLines: maxLines,
        ),
        SizedBox(height: 20),
      ],
    );
  }

  Widget buildCategoryDropdown() {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text('Category', style: TextStyle(fontSize: 16)),
        SizedBox(height: 8),
        DropdownButtonFormField<String>(
          value: _selectedCategory,
          onChanged: (newValue) {
            setState(() {
              _selectedCategory = newValue;
            });
          },
          items: ['Educational', 'Nature', 'Technology', 'Music']
              .map<DropdownMenuItem<String>>((value) =>
                  DropdownMenuItem<String>(value: value, child: Text(value)))
              .toList(),
          decoration: InputDecoration(border: OutlineInputBorder()),
        ),
        SizedBox(height: 20),
      ],
    );
  }
}