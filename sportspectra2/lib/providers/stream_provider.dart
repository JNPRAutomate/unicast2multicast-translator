import 'package:flutter/material.dart';
import 'package:sportspectra2/models/stream.dart';
import 'package:sportspectra2/services/network_service.dart';

class StreamProvider with ChangeNotifier {
  List<StreamModel> _allStreams = [];
  List<StreamModel> _filteredStreams = [];
  final NetworkService _networkService = NetworkService();

  List<StreamModel> get streams => _filteredStreams;

  Future<void> loadStreams() async {
    try {
      _allStreams = await _networkService
          .fetchStreams(); // Fetch streams from the backend
      _filteredStreams =
          List.from(_allStreams); // Ensure _filteredStreams is updated
      print('Streams loaded: ${_allStreams.length}');
      print('Loaded stream id: ${_allStreams.map((s) => s.id).toList()}');
      print('Loaded streams: ${_allStreams.map((s) => s.channelId).toList()}');

      // Check for duplicates
      Set<String> uniqueChannelIds = {};
      _allStreams.forEach((stream) {
        if (!uniqueChannelIds.add(stream.channelId)) {
          print('Duplicate found: ${stream.channelId}');
        }
      });

      notifyListeners(); // Notify listeners to update the UI
    } catch (e) {
      print('Error loading streams: $e');
    }
  }

  Future<Map<String, dynamic>> addStream(StreamModel stream, {String? videoFilePath, bool isWeb = false}) async {
  try {
    final response = await _networkService.addStream(
      title: stream.title,
      organization: stream.organization,
      description: stream.description,
      category: stream.category,
      image: stream.image,
      videoFilePath: videoFilePath,
      sourceIp: stream.sourceIp,
      groupIp: stream.groupIp,
      udpPort: stream.udpPort,
      amtRelay: stream.amtRelay,
      status: stream.status,
      isWeb: isWeb, // Pass the parameter here
    );

    // Update the stream with the returned channelId and id
    stream = StreamModel(
      id: response['id'],
      channelId: response['channel_id'],
      title: stream.title,
      description: stream.description,
      category: stream.category,
      status: stream.status,
      image: stream.image,
      viewers: stream.viewers,
      organization: stream.organization,
      videoUrl: stream.videoUrl,
      liked: stream.liked,
      totalLikes: stream.totalLikes,
      sourceIp: stream.sourceIp,
      groupIp: stream.groupIp,
      udpPort: stream.udpPort,
      amtRelay: stream.amtRelay,
    );

    _allStreams.add(stream);
    _filteredStreams = List.from(_allStreams);
    print('Stream added: ${stream.title}');
    print('Total streams after addition: ${_allStreams.length}');
    notifyListeners();

    return response; // Return the backend response
  } catch (e) {
    print('Error adding stream: $e');
    throw e; // Rethrow the exception to be handled by the caller
  }
}

  Future<void> updateStream(StreamModel stream) async {
    try {
      await _networkService
          .updateStream(stream); // Update stream in the backend
      int index = _allStreams.indexWhere((s) => s.id == stream.id);
      if (index != -1) {
        _allStreams[index] = stream;
        _filteredStreams =
            List.from(_allStreams); // Update _filteredStreams as well
        notifyListeners();
      }
    } catch (e) {
      print('Error updating stream: $e');
    }
  }

  Future<void> deleteStream({int? id, String? channelId}) async {
    try {
      StreamModel? streamToDelete;

      if (id != null) {
        streamToDelete = _allStreams.firstWhere(
          (s) => s.id == id,
          orElse: () => StreamModel(
            id: -1,
            channelId: '',
            title: '',
            description: '',
            category: '',
            status: '',
            image: '',
            viewers: 0,
            organization: '',
          ),
        );
      } else if (channelId != null) {
        streamToDelete = _allStreams.firstWhere(
          (s) => s.channelId == channelId,
          orElse: () => StreamModel(
            id: -1,
            channelId: '',
            title: '',
            description: '',
            category: '',
            status: '',
            image: '',
            viewers: 0,
            organization: '',
          ),
        );
      }

      if (streamToDelete?.id != -1) {
        print('Deleting stream with id: ${streamToDelete?.id}');
        await _networkService.deleteStream(
            streamToDelete!.id!); // Delete stream from the backend
        print('Stream deleted from backend');
        _allStreams.removeWhere(
            (s) => s.id == streamToDelete!.id); // Remove from the list
        _filteredStreams.removeWhere((s) =>
            s.id ==
            streamToDelete!.id); // Remove from filtered list if applicable
        notifyListeners();
        print('Stream removed from local lists');
      } else {
        print("Stream not found for deletion.");
      }
    } catch (e) {
      print('Error deleting stream: $e');
    }
  }

  void filterStreams(String query) {
    if (query.isEmpty) {
      _filteredStreams =
          List.from(_allStreams); // Show all streams if query is empty
    } else {
      _filteredStreams = _allStreams
          .where((stream) =>
              stream.description.toLowerCase().contains(query.toLowerCase()) ||
              stream.title.toLowerCase().contains(query.toLowerCase()) ||
              stream.organization.toLowerCase().contains(query.toLowerCase()))
          .toList();
    }
    notifyListeners();
  }

  void filterByCategory(String category) {
    if (category.isEmpty) {
      _filteredStreams =
          List.from(_allStreams); // Show all streams if category is empty
    } else {
      _filteredStreams = _allStreams
          .where((stream) =>
              stream.category.toLowerCase() == category.toLowerCase())
          .toList();
    }
    notifyListeners();
  }

  void filterByStatus(String status) {
    if (status.isEmpty) {
      _filteredStreams =
          List.from(_allStreams); // Show all streams if status is empty
    } else {
      _filteredStreams = _allStreams
          .where(
              (stream) => stream.status.toLowerCase() == status.toLowerCase())
          .toList();
    }
    notifyListeners();
  }

  void filterByLiked() {
    _filteredStreams = _allStreams.where((stream) => stream.liked).toList();
    notifyListeners();
  }

  void toggleLiked(StreamModel stream) async {
    try {
      stream.liked = !stream.liked;
      if (stream.liked) {
        stream.totalLikes += 1; // Increment total likes
      } else {
        stream.totalLikes -= 1; // Decrement total likes if unliked
      }
      await _networkService
          .updateStream(stream); // Update the stream in the backend
      notifyListeners();
    } catch (e) {
      print('Error toggling liked: $e');
    }
  }
}
