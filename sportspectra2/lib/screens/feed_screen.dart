import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'package:sportspectra2/screens/broadcast_screen.dart';
import 'package:sportspectra2/providers/stream_provider.dart' as my_provider;
import '../models/stream.dart';
import 'package:sportspectra2/screens/video_screen.dart';

class FeedScreen extends StatefulWidget {
  const FeedScreen({Key? key}) : super(key: key);

  @override
  _FeedScreenState createState() => _FeedScreenState();
}

class _FeedScreenState extends State<FeedScreen> {
  final TextEditingController _searchController = TextEditingController();
  String _selectedFilter = 'All Streams';
  String _selectedCategory = 'All';
  int _currentPage = 1;
  final int _itemsPerPage = 6;

  @override
  void initState() {
    super.initState();
    WidgetsBinding.instance.addPostFrameCallback((_) {
      context.read<my_provider.StreamProvider>().loadStreams();
    });
  }

  @override
  Widget build(BuildContext context) {
    final size = MediaQuery.of(context).size;

    return Scaffold(
      appBar: AppBar(
        title: Text('Browse Streams'),
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
                      _currentPage = 1; // Reset the page to 1
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
                  final paginatedStreams = streams
                      .skip((_currentPage - 1) * _itemsPerPage)
                      .take(_itemsPerPage)
                      .toList();

                  if (streams.isEmpty) {
                    return Center(child: Text('No streams available'));
                  }
                  return Column(
                    children: [
                      Expanded(
                        child: GridView.builder(
                          itemCount: paginatedStreams.length,
                          gridDelegate:
                              SliverGridDelegateWithFixedCrossAxisCount(
                            crossAxisCount:
                                MediaQuery.of(context).size.width > 600 ? 3 : 1,
                            crossAxisSpacing: 10,
                            mainAxisSpacing: 10,
                          ),
                          itemBuilder: (context, index) {
                            final stream = paginatedStreams[index];
                            return InkWell(
                              onTap: () {
                                print(
                                    'Thumbnail clicked, stream channelID: ${stream.channelId}');
                                    print('Thumbnail clicked, stream ID: ${stream.id}');
                                Navigator.of(context).push(
                                  MaterialPageRoute(
                                    builder: (context) => VideoScreen(
                                      streamId: stream.id.toString(),
                                    ),
                                  ),
                                );
                              },
                              child: Card(
                                child: Column(
                                  crossAxisAlignment: CrossAxisAlignment.start,
                                  children: [
                                    Expanded(
                                      child: Image.network(
                                        stream.image,
                                        fit: BoxFit.cover,
                                        width: double.infinity,
                                      ),
                                    ),
                                    Padding(
                                      padding: const EdgeInsets.all(8.0),
                                      child: Column(
                                        crossAxisAlignment:
                                            CrossAxisAlignment.start,
                                        children: [
                                          Row(
                                            mainAxisAlignment:
                                                MainAxisAlignment.spaceBetween,
                                            children: [
                                              Text(
                                                stream.title,
                                                style: TextStyle(
                                                  fontWeight: FontWeight.bold,
                                                  fontSize: 16,
                                                ),
                                              ),
                                              Row(
                                                children: [
                                                  Text(
                                                    '${stream.totalLikes} ${stream.totalLikes == 1 ? 'like' : 'likes'}',
                                                    style:
                                                        TextStyle(fontSize: 16),
                                                  ), // Display total likes with correct wording
                                                  IconButton(
                                                    icon: Icon(
                                                      stream.liked
                                                          ? Icons.favorite
                                                          : Icons
                                                              .favorite_border,
                                                      color: stream.liked
                                                          ? Colors.red
                                                          : null,
                                                    ),
                                                    onPressed: () {
                                                      context
                                                          .read<
                                                              my_provider
                                                              .StreamProvider>()
                                                          .toggleLiked(stream);
                                                    },
                                                  ),
                                                ],
                                              ),
                                            ],
                                          ),
                                          Text(stream.description),
                                          Text('Category: ${stream.category}'),
                                          Text(
                                              'Organization: ${stream.organization}'),
                                          Text('Source IP: ${stream.sourceIp}'),
                                          Text('Viewers: ${stream.viewers}'),
                                        ],
                                      ),
                                    ),
                                  ],
                                ),
                              ),
                            );
                          },
                        ),
                      ),
                      Row(
                        mainAxisAlignment: MainAxisAlignment.center,
                        children: [
                          IconButton(
                            icon: Icon(Icons.arrow_back),
                            onPressed: _currentPage > 1
                                ? () {
                                    setState(() {
                                      _currentPage--;
                                    });
                                  }
                                : null,
                          ),
                          Text(
                              'Page $_currentPage of ${((streams.length - 1) ~/ _itemsPerPage) + 1}'),
                          IconButton(
                            icon: Icon(Icons.arrow_forward),
                            onPressed:
                                _currentPage * _itemsPerPage < streams.length
                                    ? () {
                                        setState(() {
                                          _currentPage++;
                                        });
                                      }
                                    : null,
                          ),
                        ],
                      ),
                    ],
                  );
                },
              ),
            ),
          ],
        ),
      ),
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
