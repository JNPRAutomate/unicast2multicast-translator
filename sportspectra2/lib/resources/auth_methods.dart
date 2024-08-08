
import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'package:sportspectra2/providers/user_provider.dart';
import 'package:sportspectra2/services/network_service.dart';
import 'package:sportspectra2/models/user.dart';

class AuthMethods {
  final NetworkService _networkService = NetworkService();

  Future<User?> getCurrentUser(BuildContext context) async {
    User? user = await _networkService.getCurrentUser();
    if (user != null) {
      Provider.of<UserProvider>(context, listen: false).setUser(user);
    }
    return user;
  }

  Future<bool> loginUser(BuildContext context, String email, String password) async {
    Map<String, dynamic>? userMap = await _networkService.loginUser(email, password);
    if (userMap != null) {
      User user = User.fromMap(userMap);
      Provider.of<UserProvider>(context, listen: false).setUser(user);
      return true;
    } else {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text('Invalid email or password')),
      );
      return false;
    }
  }

  Future<bool> signUpUser(BuildContext context, String username, String email, String password) async {
    Map<String, dynamic>? existingUser = await _networkService.getUserByEmail(email);
    if (existingUser == null) {
      await _networkService.signUpUser(username, email, password);
      // After signup, log in the user to set the user data
      return await loginUser(context, email, password);
    } else {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text('Email already in use')),
      );
      return false;
    }
  }
}