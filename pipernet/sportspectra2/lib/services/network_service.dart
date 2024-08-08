import 'package:http/http.dart' as http;
import 'package:sportspectra2/models/stream.dart';
import 'dart:convert';
import 'package:sportspectra2/models/user.dart';  // Ensure you import the User model
import 'dart:typed_data';

class NetworkService {
  //the simulator
  // static const String baseUrl = 'http://127.0.0.1:8000/api';

  // isabelle's home: regent terrace
  static const String baseUrl = 'http://10.0.0.54:8000/api';

  //juniper networks office herndon
  // static const String baseUrl = 'http://172.25.80.17:8000/api';

  //brandywine public
  // static const String baseUrl = 'http://192.168.2.110:8000/api';

  // Fetch the public IP address
  Future<String> getPublicIPAddress() async {
    try {
      final response =
          await http.get(Uri.parse('https://api.ipify.org?format=json'));
      if (response.statusCode == 200) {
        final data = json.decode(response.body);
        return data['ip'];
      } else {
        throw Exception('Failed to get public IP');
      }
    } catch (e) {
      print('Error: $e');
      return 'Error fetching IP';
    }
  }

  // Fetch streams
  Future<List<StreamModel>> fetchStreams() async {
    final response = await http.get(Uri.parse('$baseUrl/livestreams/'));
    if (response.statusCode == 200) {
      List<dynamic> body = json.decode(response.body);
      return body.map((dynamic item) => StreamModel.fromJson(item)).toList();
    } else {
      throw Exception('Failed to load streams');
    }
  }

  Future<Map<String, dynamic>> addStream({
    required String title,
    required String organization,
    required String description,
    required String category,
    required String image,
    String? videoFilePath,
    String? sourceIp,
    String? groupIp,
    String? udpPort,
    String? amtRelay,
    required String status,
    bool isWeb = false,
  }) async {
    final uploadUri = Uri.parse('$baseUrl/upload_video/');

    if (sourceIp == null) {
      sourceIp = await getPublicIPAddress();
    }

    var request = http.MultipartRequest('POST', uploadUri)
      ..fields['title'] = title
      ..fields['organization'] = organization
      ..fields['description'] = description
      ..fields['category'] = category
      ..fields['image'] = image
      ..fields['status'] = status
      ..fields['source_ip'] = sourceIp
      ..fields['is_web'] = isWeb.toString(); // Add this field

    if (groupIp != null) request.fields['group_ip'] = groupIp;
    if (udpPort != null) request.fields['udp_port'] = udpPort;
    if (amtRelay != null) request.fields['amt_relay'] = amtRelay;

    if (videoFilePath != null) {
      request.files
          .add(await http.MultipartFile.fromPath('file', videoFilePath));
    }

    var response = await request.send();
    print(
        'Upload to /upload_video/ completed with status: ${response.statusCode}');

    if (response.statusCode == 201) {
      var responseBody = await response.stream.bytesToString();
      var jsonResponse = json.decode(responseBody);
      print(
          'Stream uploaded and processed with source_ip: ${jsonResponse['source_ip']}');
      print(
          'Stream uploaded and processed with channel_id: ${jsonResponse['channel_id']}');
      return jsonResponse; // Ensure this returns a Map<String, dynamic>
    } else {
      throw Exception('Failed to upload stream');
    }
  }

  // Update an existing stream
  Future<void> updateStream(StreamModel stream) async {
    final response = await http.put(
      Uri.parse('$baseUrl/livestreams/${stream.id}/'),
      headers: {"Content-Type": "application/json"},
      body: json.encode(stream.toJson()),
    );
    if (response.statusCode != 200) {
      throw Exception('Failed to update stream');
    }
  }

  // Delete a stream
  Future<void> deleteStream(int id) async {
    final response = await http.delete(
      Uri.parse('$baseUrl/livestreams/$id/'),
    );
    print('Delete response status: ${response.statusCode}');
    if (response.statusCode != 204) {
      throw Exception('Failed to delete stream');
    }
  }

  // User login
  Future<Map<String, dynamic>?> loginUser(String email, String password) async {
    final response = await http.post(
      Uri.parse('$baseUrl/login/'),
      headers: {"Content-Type": "application/json"},
      body: json.encode({'email': email, 'password': password}),
    );
    if (response.statusCode == 200) {
      return jsonDecode(response.body);
    } else {
      return null;
    }
  }

  // Get user by email
  Future<Map<String, dynamic>?> getUserByEmail(String email) async {
    final response = await http.get(
      Uri.parse('$baseUrl/auth_users/?email=$email'),
    );
    if (response.statusCode == 200) {
      final List users = jsonDecode(response.body);
      if (users.isNotEmpty) {
        return users[0];
      }
      return null;
    } else {
      return null;
    }
  }

  // User signup
  Future<void> signUpUser(
      String username, String email, String password) async {
    final response = await http.post(
      Uri.parse('$baseUrl/signup/'),
      headers: {"Content-Type": "application/json"},
      body: json.encode({
        'username': username,
        'email': email,
        'password': password,
      }),
    );
    if (response.statusCode != 201) {
      throw Exception('Failed to sign up user');
    }
  }

  // Fetch current user
  Future<User?> getCurrentUser() async {
    final response = await http.get(
      Uri.parse('$baseUrl/current_user/'),
    );
    if (response.statusCode == 200) {
      final data = json.decode(response.body);
      return User.fromMap(data);
    } else {
      return null;
    }
  }
}