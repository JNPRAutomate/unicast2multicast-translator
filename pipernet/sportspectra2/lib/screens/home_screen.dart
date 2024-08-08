import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'package:sportspectra2/providers/stream_provider.dart' as my_provider;
import 'package:sportspectra2/screens/add_stream_screen.dart';
import 'package:sportspectra2/screens/feed_screen.dart';
import 'package:sportspectra2/screens/go_live_screen.dart';
import 'package:sportspectra2/screens/browser_screen.dart'; 
import 'package:sportspectra2/utils/colors.dart';

class HomeScreen extends StatefulWidget {
  static String routeName = '/home';
  const HomeScreen({super.key});

  @override
  State<HomeScreen> createState() => _HomeScreenState();
}

class _HomeScreenState extends State<HomeScreen> {
  int _page = 0;

  List<Widget> pages = [
    const FeedScreen(),
    const AddStreamScreen(),
    const BrowserScreen(),
  ];

  // when you click on different icons the page changes
  onPageChange(int page) {
    setState(() {
      _page = page;
    });
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      bottomNavigationBar: BottomNavigationBar(
        selectedItemColor: buttonColor,
        unselectedItemColor: primaryColor,
        backgroundColor: backgroundColor,
        unselectedFontSize: 12,
        onTap: onPageChange,
        currentIndex: _page,
        items: const [
          BottomNavigationBarItem(
            icon: Icon(
              Icons.copy,
            ),
            label: 'Browse',
          ),
          BottomNavigationBarItem(
            icon: Icon(
              Icons.add_rounded,
            ),
            label: 'Add Stream',
          ),
          BottomNavigationBarItem(
            icon: Icon(
              Icons.dashboard,
            ),
            label: 'Manage Stream',
          ),
        ],
      ),
      body: pages[_page],
    );
  }
}
