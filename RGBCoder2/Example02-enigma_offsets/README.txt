In this next example, we will be adding a layer of complexity to our encoded messages. Much like the famed Enigma Machine, the Enigma offset of this program will change the encoding index of each character by a different amount. This makes encoded messages, even if intercepted, very difficult to crack.

Luckily, usage of Enigma offsets is extremely easy in RGBCoder2. Simply enter a nonzero integer to the box labelled 'Enigma Offset' whenever encoding or decoding a message. As long as both the sending and receiving parties have the same integer, communication is still seamless.

This time, the 'secret_message2.png' file has been encoded with an Enigma Offset... Try to decode it!
(HINT: The offset is between 0 and 5...)