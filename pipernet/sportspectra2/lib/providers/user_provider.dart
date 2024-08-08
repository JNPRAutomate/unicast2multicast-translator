
import 'package:flutter/material.dart';
import '../models/user.dart';

class UserProvider extends ChangeNotifier {
  User _user = User(
    uid: '',
    username: '',
    email: '',
  );

  User get user => _user;

  void setUser(User user) {
    _user = user;
    print('User set in UserProvider: ${_user.uid}, ${_user.username}, ${_user.email}');
    notifyListeners();
  }
}