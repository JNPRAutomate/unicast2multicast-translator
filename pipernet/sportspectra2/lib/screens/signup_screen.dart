
import 'package:flutter/material.dart';
import 'package:sportspectra2/resources/auth_methods.dart';
import 'package:sportspectra2/screens/home_screen.dart';
import 'package:sportspectra2/widgets/custom_button.dart';
import 'package:sportspectra2/widgets/custom_textfield.dart';
import 'package:sportspectra2/widgets/loading_indicator.dart';
import 'package:sportspectra2/providers/user_provider.dart';
import 'package:provider/provider.dart';

class SignUpScreen extends StatefulWidget {
  static const String routeName = '/signup';
  const SignUpScreen({super.key});

  @override
  State<SignUpScreen> createState() => _SignUpScreenState();
}

class _SignUpScreenState extends State<SignUpScreen> {
  final TextEditingController _usernameController = TextEditingController();
  final TextEditingController _emailController = TextEditingController();
  final TextEditingController _passwordController = TextEditingController();
  final AuthMethods _authMethods = AuthMethods();

  bool _isLoading = false;

  signUpUser() async {
    setState(() {
      _isLoading = true;
    });
    bool res = await _authMethods.signUpUser(
      context,
      _usernameController.text,
      _emailController.text,
      _passwordController.text,
    );

    if (res) {
      final userProvider = Provider.of<UserProvider>(context, listen: false);
      print('User signed up: ${userProvider.user.uid}, ${userProvider.user.username}, ${userProvider.user.email}');
      Navigator.pushReplacementNamed(context, HomeScreen.routeName);
    }

    setState(() {
      _isLoading = false;
    });
  }

  @override
  void dispose() {
    _usernameController.dispose();
    _emailController.dispose();
    _passwordController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final size = MediaQuery.of(context).size;
    return Scaffold(
      appBar: AppBar(
        title: const Text('Sign Up'),
      ),
      body: _isLoading
          ? const LoadingIndicator()
          : SingleChildScrollView(
              child: Padding(
                padding: const EdgeInsets.symmetric(horizontal: 18.0),
                child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      SizedBox(height: size.height * 0.1),
                      const Text('Username',
                          style: TextStyle(
                            fontWeight: FontWeight.bold,
                          )),
                      Padding(
                        padding: const EdgeInsets.symmetric(vertical: 8.0),
                        child: CustomTextField(controller: _usernameController),
                      ),
                      const SizedBox(
                        height: 20,
                      ),
                      const Text('Email',
                          style: TextStyle(
                            fontWeight: FontWeight.bold,
                          )),
                      Padding(
                        padding: const EdgeInsets.symmetric(vertical: 8.0),
                        child: CustomTextField(controller: _emailController),
                      ),
                      const SizedBox(
                        height: 20,
                      ),
                      const Text('Password',
                          style: TextStyle(
                            fontWeight: FontWeight.bold,
                          )),
                      Padding(
                        padding: const EdgeInsets.symmetric(vertical: 8.0),
                        child: CustomTextField(
                            controller: _passwordController, isPassword: true),
                      ),
                      const SizedBox(
                        height: 20,
                      ),
                      CustomButton(onTap: signUpUser, text: 'Sign Up')
                    ]),
              ),
            ),
    );
  }
}