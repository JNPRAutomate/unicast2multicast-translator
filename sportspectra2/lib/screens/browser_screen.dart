import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../providers/stream_provider.dart' as my_provider;
import '../models/stream.dart';

class BrowserScreen extends StatefulWidget {
  const BrowserScreen({super.key});

  @override
  State<BrowserScreen> createState() => _BrowserScreenState();
}

class _BrowserScreenState extends State<BrowserScreen> {
  final TextEditingController _searchController = TextEditingController();
  String _selectedFilter = 'All Streams';
  String _selectedCategory = 'All';

  @override
  void initState() {
    super.initState();
    WidgetsBinding.instance.addPostFrameCallback((_) {
      context.read<my_provider.StreamProvider>().loadStreams();
    });
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: PreferredSize(
        preferredSize: Size.fromHeight(0),
        child: AppBar(
          backgroundColor: Colors.transparent,
          elevation: 0,
        ),
      ),
      body: Padding(
        padding: const EdgeInsets.all(10.0),
        child: Column(
          children: [
            Row(
              children: [
                Expanded(
                  child: TextField(
                    controller: _searchController,
                    decoration: InputDecoration(
                      hintText: 'Search by title...',
                      prefixIcon: Icon(Icons.search),
                      filled: true,
                      fillColor: Colors.white,
                      border: OutlineInputBorder(
                        borderRadius: BorderRadius.circular(10.0),
                        borderSide: BorderSide.none,
                      ),
                    ),
                    onChanged: (value) {
                      context
                          .read<my_provider.StreamProvider>()
                          .filterStreams(value);
                    },
                  ),
                ),
                SizedBox(width: 10),
                DropdownButton<String>(
                  value: _selectedFilter,
                  onChanged: (String? newValue) {
                    setState(() {
                      _selectedFilter = newValue!;
                      if (_selectedFilter == 'All Streams') {
                        context
                            .read<my_provider.StreamProvider>()
                            .filterStreams('');
                      } else if (_selectedFilter == 'Trending Streams') {
                        context
                            .read<my_provider.StreamProvider>()
                            .filterByStatus('Trending');
                      } else if (_selectedFilter == "Editor's Choice Streams") {
                        context
                            .read<my_provider.StreamProvider>()
                            .filterByStatus("Editor's Choice");
                      } else if (_selectedFilter == 'Liked Streams') {
                        context
                            .read<my_provider.StreamProvider>()
                            .filterByLiked();
                      }
                    });
                  },
                  items: <String>[
                    'All Streams',
                    'Trending Streams',
                    "Editor's Choice Streams",
                    'Liked Streams'
                  ].map<DropdownMenuItem<String>>((String value) {
                    return DropdownMenuItem<String>(
                      value: value,
                      child: Text(value),
                    );
                  }).toList(),
                  dropdownColor: Colors.white,
                  style: TextStyle(color: Colors.black),
                ),
              ],
            ),
            SizedBox(height: 10),
            Row(
              mainAxisAlignment: MainAxisAlignment.center,
              children: [
                Text('Category: ',
                    style: TextStyle(fontSize: 16, color: Colors.black)),
                ElevatedButton(
                  onPressed: () async {
                    final String? category = await showDialog<String>(
                      context: context,
                      builder: (BuildContext context) {
                        return CategorySelectionDialog(
                          selectedCategory: _selectedCategory,
                        );
                      },
                    );
                    if (category != null) {
                      setState(() {
                        _selectedCategory = category;
                        if (_selectedCategory == 'All') {
                          context
                              .read<my_provider.StreamProvider>()
                              .filterStreams('');
                        } else {
                          context
                              .read<my_provider.StreamProvider>()
                              .filterByCategory(_selectedCategory);
                        }
                      });
                    }
                  },
                  style: ElevatedButton.styleFrom(
                    backgroundColor: Colors.white,
                    foregroundColor: Colors.black,
                    shape: RoundedRectangleBorder(
                      borderRadius: BorderRadius.circular(10.0),
                      side: BorderSide(color: Colors.grey),
                    ),
                  ),
                  child: Row(
                    mainAxisSize: MainAxisSize.min,
                    children: [
                      Text(_selectedCategory),
                      Icon(Icons.filter_list, color: Colors.black),
                    ],
                  ),
                ),
              ],
            ),
            SizedBox(height: 10),
            Expanded(
              child: Consumer<my_provider.StreamProvider>(
                builder: (context, streamProvider, child) {
                  final streams = streamProvider.streams;
                  if (streams.isEmpty) {
                    return Center(child: Text('No streams available'));
                  }
                  return ListView.builder(
                    itemCount: streams.length,
                    itemBuilder: (context, index) {
                      final stream = streams[index];
                      return ListTile(
                        title: Text(stream.title),
                        subtitle: Text(stream.description),
                        trailing: Row(
                          mainAxisSize: MainAxisSize.min,
                          children: [
                            Text(stream.category),
                            Text('   Org: ${stream.organization}'),
                            IconButton(
                              icon: Icon(
                                Icons.delete,
                                color: Colors.red,
                              ),
                              onPressed: () {
                                _showDeleteConfirmationDialog(context, stream);
                              },
                            ),
                          ],
                        ),
                      );
                    },
                  );
                },
              ),
            ),
          ],
        ),
      ),
    );
  }

  void _showDeleteConfirmationDialog(BuildContext context, StreamModel stream) {
    showDialog(
      context: context,
      builder: (context) {
        return AlertDialog(
          title: Text('Delete Stream'),
          content: Text('Are you sure you want to delete this stream?'),
          actions: [
            TextButton(
              onPressed: () {
                Navigator.of(context).pop();
              },
              child: Text('Cancel'),
            ),
            TextButton(
              onPressed: () async {
                print('Delete button pressed for stream with id: ${stream.id}');
                await Provider.of<my_provider.StreamProvider>(context,
                        listen: false)
                    .deleteStream(id: stream.id);
                print('Delete stream request sent');
                Navigator.of(context).pop();
              },
              child: Text('Delete'),
            ),
          ],
        );
      },
    );
  }
}

class CategorySelectionDialog extends StatelessWidget {
  final String selectedCategory;

  const CategorySelectionDialog({required this.selectedCategory});

  @override
  Widget build(BuildContext context) {
    return SimpleDialog(
      title: const Text('Select Category'),
      children: <Widget>[
        SimpleDialogOption(
          onPressed: () {
            Navigator.pop(context, 'All');
          },
          child: const Text('All'),
        ),
        SimpleDialogOption(
          onPressed: () {
            Navigator.pop(context, 'Educational');
          },
          child: const Text('Educational'),
        ),
        SimpleDialogOption(
          onPressed: () {
            Navigator.pop(context, 'Nature');
          },
          child: const Text('Nature'),
        ),
        SimpleDialogOption(
          onPressed: () {
            Navigator.pop(context, 'Technology');
          },
          child: const Text('Technology'),
        ),
        SimpleDialogOption(
          onPressed: () {
            Navigator.pop(context, 'Music');
          },
          child: const Text('Music'),
        ),
      ],
    );
  }
}
