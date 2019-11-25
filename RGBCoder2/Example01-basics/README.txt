NOTE: PIL, tkinter, and string libraries all have to be set up and working for program to execute.

This example showcases the basic functionality of the program. When the 'puppy.png' file is loaded as the master image, and the 'secret_message.png' file is loaded as the encoded image, you should be able to hit 'DECODE' and get a secret message popup without any further fiddling about.

To encode your own personal message, modify the text of 'message.txt' to your liking, select it as the message file in the program, and hit 'ENCODE' (make sure to still have the master image file selected!). This will create a new image in your working directory named 'output.png'. Try to decode your secret message!

If you want a more permanent version of your secret message to stick around, the 'Save decoded message to file' checkbox will store the message as 'decoded.txt' in your working directory instead of displaying a popup.