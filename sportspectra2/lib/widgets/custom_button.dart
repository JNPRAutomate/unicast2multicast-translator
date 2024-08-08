import 'package:flutter/material.dart';
import 'package:sportspectra2/utils/colors.dart';

class CustomButton extends StatelessWidget {
  /* This is the constructor for the CustomButton class. It defines parameters for the button, including a Key parameter (key), an onTap function (onTap), and a string text to display on the button.
required indicates that the onTap and text parameters must be provided when creating an instance of CustomButton.
super(key: key) calls the constructor of the superclass (StatelessWidget) and passes the key parameter to it.*/
  const CustomButton({
    Key? key,
    required this.onTap,
    required this.text,
  }) : super(key: key);
  final String text;
  final VoidCallback onTap;

// build method overrides the build method of the superclass (StatelessWidget).
  @override
  /*constructing and returning the UI representation of the custom button widget.*/
  Widget build(BuildContext context) {
    return ElevatedButton(
      style: ElevatedButton.styleFrom(
        backgroundColor: buttonColor,
        minimumSize: const Size(double.infinity, 40),
      ),
      onPressed: onTap,
      child: Text(
        text,
        style: TextStyle(color: Colors.white), // Set text color to white
      ),
    );
  }
}
