import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'package:sportspectra2/providers/stream_provider.dart' as my_provider;
import '../models/stream.dart';
import 'an_uploaded_file_screen.dart';

class ManuallyReportStreamScreen extends StatefulWidget {
  final TextEditingController thumbnailController;

  const ManuallyReportStreamScreen(
      {Key? key, required this.thumbnailController})
      : super(key: key);

  @override
  _ManuallyReportStreamScreenState createState() =>
      _ManuallyReportStreamScreenState();
}

class _ManuallyReportStreamScreenState
    extends State<ManuallyReportStreamScreen> {
  String? _selectedCategory;
  final TextEditingController _sourceIPController = TextEditingController();
  final TextEditingController _groupIPController = TextEditingController();
  final TextEditingController _udpPortController = TextEditingController();
  final TextEditingController _amtRelayController = TextEditingController();
  final TextEditingController _organizationController = TextEditingController();
  final TextEditingController _descriptionController = TextEditingController();
  final TextEditingController _titleController = TextEditingController();

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: Text('Report Existing Stream'),
        actions: [
          IconButton(
            icon: Icon(Icons.upload_file),
            onPressed: () {
              Navigator.push(
                context,
                MaterialPageRoute(
                  builder: (context) => AnUploadedFileScreen(
                    thumbnailController: widget.thumbnailController,
                  ),
                ),
              );
            },
          ),
        ],
      ),
      body: Padding(
        padding: const EdgeInsets.all(16.0),
        child: SingleChildScrollView(
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.stretch,
            children: [
              Text(
                'Enter the details of the stream that you want to report.',
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
                'Thumbnail URL:',
                style: TextStyle(fontSize: 16),
              ),
              SizedBox(height: 8),
              TextFormField(
                controller: widget.thumbnailController,
                decoration: InputDecoration(
                  border: OutlineInputBorder(),
                  hintText: 'Enter Thumbnail URL',
                ),
              ),
              SizedBox(height: 20),
              Text(
                'Source IP:',
                style: TextStyle(fontSize: 16),
              ),
              SizedBox(height: 8),
              TextFormField(
                controller: _sourceIPController,
                decoration: InputDecoration(
                  border: OutlineInputBorder(),
                  hintText: 'Enter Source IP',
                ),
              ),
              SizedBox(height: 20),
              Text(
                'Group IP:',
                style: TextStyle(fontSize: 16),
              ),
              SizedBox(height: 8),
              TextFormField(
                controller: _groupIPController,
                decoration: InputDecoration(
                  border: OutlineInputBorder(),
                  hintText: 'Enter Group IP',
                ),
              ),
              SizedBox(height: 20),
              Text(
                'UDP Port:',
                style: TextStyle(fontSize: 16),
              ),
              SizedBox(height: 8),
              TextFormField(
                controller: _udpPortController,
                decoration: InputDecoration(
                  border: OutlineInputBorder(),
                  hintText: 'Enter UDP Port',
                ),
              ),
              SizedBox(height: 20),
              Text(
                'AMT Relay:',
                style: TextStyle(fontSize: 16),
              ),
              SizedBox(height: 8),
              TextFormField(
                controller: _amtRelayController,
                decoration: InputDecoration(
                  border: OutlineInputBorder(),
                  hintText: 'amt-relay.m2icast.net',
                ),
              ),
              SizedBox(height: 20),
              Text(
                'Name of Originating Organization:',
                style: TextStyle(fontSize: 16),
              ),
              SizedBox(height: 8),
              TextFormField(
                controller: _organizationController,
                decoration: InputDecoration(
                  border: OutlineInputBorder(),
                  hintText: 'Enter Name',
                ),
              ),
              SizedBox(height: 20),
              Text(
                'Description of Stream:',
                style: TextStyle(fontSize: 16),
              ),
              SizedBox(height: 8),
              TextFormField(
                controller: _descriptionController,
                maxLines: 3,
                decoration: InputDecoration(
                  border: OutlineInputBorder(),
                  hintText: 'Enter Description',
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
                onPressed: () async {
                  try {
                    var newStream = StreamModel(
                      channelId: '',
                      title: _titleController.text,
                      description: _descriptionController.text,
                      category: _selectedCategory ?? 'Other',
                      status: 'New',
                      image: widget.thumbnailController.text,
                      viewers: 0,
                      organization: _organizationController.text,
                      sourceIp: _sourceIPController.text,
                      groupIp: _groupIPController.text,
                      udpPort: _udpPortController.text,
                      amtRelay: _amtRelayController.text,
                    );

                    final response = await context
                        .read<my_provider.StreamProvider>()
                        .addStream(newStream);

                    newStream = StreamModel(
                      id: response['id'],
                      channelId: response['channel_id'],
                      title: _titleController.text,
                      description: _descriptionController.text,
                      category: _selectedCategory ?? 'Other',
                      status: 'New',
                      image: widget.thumbnailController.text,
                      viewers: 0,
                      organization: _organizationController.text,
                      sourceIp: _sourceIPController.text,
                      groupIp: _groupIPController.text,
                      udpPort: _udpPortController.text,
                      amtRelay: _amtRelayController.text,
                    );

                    print('New Stream Channel ID: ${newStream.channelId}');
                    print('Stream added with ID: ${response['id']}');
                    await context
                        .read<my_provider.StreamProvider>()
                        .loadStreams();
                    Navigator.pop(context);
                  } catch (e) {
                    print('Error adding stream: $e');
                  }
                },
                child: Text('Submit'),
              )
            ],
          ),
        ),
      ),
    );
  }
}
