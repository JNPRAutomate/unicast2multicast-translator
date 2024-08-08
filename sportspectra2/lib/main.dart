import 'package:flutter/foundation.dart';
import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'package:sportspectra2/providers/stream_provider.dart' as my_provider;
import 'package:sportspectra2/providers/user_provider.dart';
import 'package:sportspectra2/resources/auth_methods.dart';
import 'package:sportspectra2/screens/home_screen.dart';
import 'package:sportspectra2/screens/login_screen.dart';
import 'package:sportspectra2/screens/onboarding_screen.dart';
import 'package:sportspectra2/screens/signup_screen.dart';
import 'package:sportspectra2/utils/colors.dart';
import 'package:sportspectra2/widgets/loading_indicator.dart';

void main() {
  // Ensure widgets are initialized
  WidgetsFlutterBinding.ensureInitialized();

  runApp(
    MultiProvider(
      providers: [
        ChangeNotifierProvider(
            create: (_) => my_provider.StreamProvider()..loadStreams()),
        ChangeNotifierProvider(create: (_) => UserProvider()),
      ],
      child: MyApp(),
    ),
  );
}

class MyApp extends StatelessWidget {
  const MyApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      debugShowCheckedModeBanner: false,
      title: 'sportspectra2',
      theme: ThemeData.light().copyWith(
        scaffoldBackgroundColor: backgroundColor,
        appBarTheme: AppBarTheme.of(context).copyWith(
          backgroundColor: backgroundColor,
          elevation: 0,
          titleTextStyle: const TextStyle(
            color: primaryColor,
            fontSize: 20,
            fontWeight: FontWeight.w600,
          ),
          iconTheme: const IconThemeData(
            color: primaryColor,
          ),
        ),
      ),
      routes: {
        OnboardingScreen.routeName: (context) => const OnboardingScreen(),
        LoginScreen.routeName: (context) => const LoginScreen(),
        SignUpScreen.routeName: (context) => const SignUpScreen(),
        HomeScreen.routeName: (context) => const HomeScreen(),
      },
      // When we close the app and reopen, we want users that have logged in to stay logged in
      home: FutureBuilder(
        future: AuthMethods().getCurrentUser(context).then((user) {
          if (user != null) {
            Provider.of<UserProvider>(context, listen: false).setUser(user);
            return true;
          }
          return false;
        }),
        builder: (context, snapshot) {
          if (snapshot.connectionState == ConnectionState.waiting) {
            return const LoadingIndicator();
          }

          if (snapshot.hasData && snapshot.data == true) {
            // If snapshot has data, that means user already logged in so go to home screen
            return const HomeScreen();
          }
          return const OnboardingScreen();
        },
      ),
    );
  }
}