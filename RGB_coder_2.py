# A remake of the RGB encoder python project from scratch, to fight bugs in 1.0
# C Ethan Brucker
# Version 10-31-19
# Made for Jordan Schmerge, with love <3

from PIL import Image, ImageDraw # For image functionality
import tkinter as tk # For GUI
import tkinter.filedialog as fd # Explicit loading for CMD support (not used as fd)
import tkinter.messagebox as ms # Another CMD support feature
import string # To easily make the default master strings

def from_decimal_to_base(num, base):
    # Returns a list of digits of the given decimal number in the new base
    m = [] # List of digits

    while num != 0:
        r = num % base
        d = num // base
        m.append(r)
        num = d
    # Add extra values to make it 3 long
    while len(m) < 3:
        m.append(0)
    # Reverse the list to get the digits in the right order
    m.reverse()
    return m

def getbase(master_string):
    # Gets the minimum size base that can accomodate a master string
    max_color_offset = 0
    for i in range(10):
        if (i ** 3 - 1) > len(master_string): # Not equal b/c 0 index offset
            max_color_offset = i
            return max_color_offset

def encode(master_img, message, master_string, offset=0):
    # Codes an image and saves it based on the passed values
    #   master_img : the original master image to draw from
    #   message : the master message to encode
    #   master_string : the master string key
    #   offset : The number of spaces to Enigma offset each time

    # Get image width and height
    img_width, img_height = master_img.size
    
    # Create a new, blank image to draw to
    #new_img = Image.new('RGB', (img_width, img_height))
    new_img = master_img.copy()
    draw = ImageDraw.Draw(new_img)

    # Get the total number of pixels in the image, to iterate over
    # Careful when converting back to (x, y)
    total_pixels = img_width * img_height

    # Get length of message
    message_length = len(message)

    # If the message is too long, kill the process
    if message_length > total_pixels:
        return
    hop = total_pixels // (message_length + 1) # Get the amount of pix to jump

    # Find the max value of the (R, G, B) offset (the base)
    max_color_offset = getbase(master_string)

    # Else, continue with the encoding of each character in the message
    index = 0 # Where the process is in the image
    enigma = 0 # Enigma-style offset for each individual character
    for char in message:
        # Get the numerical representation of the character based on master_string
        num = 0
        for ref in master_string:
            if char is ref:
                break
            num += 1

        # Add the enigma offset
        num += enigma
        num %= len(master_string)

        # Add 1 so that index 0 still makes a change to the picture
        num += 1

        # Convert index into an (x, y) position
        x, y = index, 0
        while x > (img_width - 1):
            y += 1
            x -= img_width

        # Modify the new pixel at (x, y)
        # Change the num into an (R, G, B) offset
        colors_offset = from_decimal_to_base(num, max_color_offset)

        # Offset the color
        pix = list(master_img.getpixel((x, y)))
        for i in range(3): # Modify the RGB in a legal direction
            if (pix[i] + colors_offset[i]) > 255:
                pix[i] -= colors_offset[i]
            else:
                pix[i] += colors_offset[i]
        draw.point((x, y), tuple(pix))

        index += hop
        enigma += offset
        # Loop enigma (only really necessary for REALLY long messages)
        enigma %= len(master_string)

    # Save the image
    new_img.save("output.png")

def decode(master_img, encoded_img, master_string, offset=0):
    # Variable inits
    width, height = master_img.size
    base = getbase(master_string)
    enigma = 0
    
    # Get a list of all pixels that are different between images
    master_list = []
    for y in range(height):
        for x in range(width):
            pix1 = master_img.getpixel((x, y))
            pix2 = encoded_img.getpixel((x, y))
            if ((pix1[0] != pix2[0]) or (pix1[1] != pix2[1])
                 or (pix1[2] != pix2[2])):
                r_off = abs(pix1[0] - pix2[0])
                g_off = abs(pix1[1] - pix2[1])
                b_off = abs(pix1[2] - pix2[2])
                master_list.append((r_off, g_off, b_off))

    # Decode the message
    message = ""
    for pixel in master_list:
        # Get index of color offset in base 10
        index = (base ** 2) * pixel[0] # Red
        index += base * pixel[1] # Green
        index += pixel[2] # Blue

        # Do enigma offset
        index -= enigma
        while index < 0:
            index += len(master_string)

        # Loop enigma
        enigma += offset
        #while enigma >= len(master_string):
        enigma %= len(master_string)

        index -= 1 # Subtract 1 so index 0 still makes a change in the picture

        # Add the character at given index to the message
        message += master_string[index]

    return message

# Class for managing all data storage without global variables
class Data():
    def __init__(self, root):
        # Misc. variables
        self.save = False
        self.enigma = 0
        self.enigma_string = tk.StringVar()
        self.enigma_string.set("0")
        # Changing string setups
        self.master_image_path = ""
        self.master_image = None
        self.master_image_string = tk.StringVar()
        self.master_image_string.set("No master image specified")
        
        self.encoded_image_path = ""
        self.encoded_image = None
        self.encoded_image_string = tk.StringVar()
        self.encoded_image_string.set("No encoded image specified")
        
        self.message_path = ""
        self.message = ""
        self.message_path_string = tk.StringVar()
        self.message_path_string.set("No message file specified")
        
        self.character_list_path = ""
        self.character_list = string.printable + string.whitespace # Default
        self.character_list_string = tk.StringVar()
        self.character_list_string.set("Using default character list")

    def update_enigma(self):
        # Fixes the enigma offset entry box
        # Call before every encode/decode
        s = self.enigma_string.get()
        if s.isdigit():
            self.enigma = int(s)
        else:
            self.enigma = 0
            self.enigma_string.set("0")

    def set_master_image(self):
        path = tk.filedialog.askopenfilename(title="Select master image file",
                                      filetypes=(("PNG files", "*.png"),))
        try: # Open the file
            self.master_image_path = path
            self.master_image = Image.open(path)
            self.master_image_string.set(path)
        except: # Couldn't open the file
            self.master_image_path = ""
            self.master_image = None
            self.master_image_string.set("No master image specified")

    def set_encoded_image(self):
        path = tk.filedialog.askopenfilename(title="Select encoded image file",
                                      filetypes=(("PNG files", "*.png"),))
        try: # Open the file
            self.encoded_image_path = path
            self.encoded_image = Image.open(path)
            self.encoded_image_string.set(path)
        except: # Couldn't open file
            self.encoded_image_path = ""
            self.encoded_image = None
            self.encoded_image_string.set("No encoded image specified")

    def set_message(self):
        filepath = tk.filedialog.askopenfilename(title="Select message file",
                                      filetypes=(("Text files", "*.txt"),
                                                 ("Python files", "*.py *.pyw"),
                                                 ("All files", "*.*")))
        try: # Open the message file
            file = open(filepath, "r", encoding="utf-8")
            self.message = file.read()
            self.message_path = filepath
            self.message_path_string.set(filepath)
        except: # Message file could not be opened
            self.message = ""
            self.message_path = ""
            self.message_path_string.set("No message file specified")

    def set_character_list(self):
        filepath = tk.filedialog.askopenfilename(title="Select character list file",
                                      filetypes=(("Text files", "*.txt"),))
        try: # Open the character list file
            file = open(filepath, "r", encoding="utf-8")
            self.character_list = file.read()
            self.character_list_path = filepath
            self.character_list_string.set(filepath)
        except:
            self.character_list = string.printable + string.whitespace # Default
            self.character_list_path = ""
            self.character_list_string.set("Using default character list")
            

    def toggle_save(self):
        if self.save:
            self.save = False
        else:
            self.save = True

    def decode(self):
        self.update_enigma() # Update the enigma option
        # Decode
        if (self.master_image_path is not "") and (self.encoded_image_path is
                                                   not ""): # Can decode  
            # Update images into memory (allows hotswapping w/o reselect)
            self.master_image = Image.open(self.master_image_path)
            self.encoded_image = Image.open(self.encoded_image_path)
            # Decode
            if self.save: # User wants to save to file
                file = open("decoded.txt", "w+")
                file.write(decode(self.master_image, self.encoded_image,
                         self.character_list, offset=self.enigma))
            else: # User wants a notification
                decoded = decode(self.master_image, self.encoded_image,
                         self.character_list, offset=self.enigma)
                tk.messagebox.showinfo("Decoded Message", decoded)

    def encode(self):
        self.update_enigma() # Update the enigma option
        # Encode
        if (self.master_image_path is not "") and (self.message_path is not ""):
            # Update image/message into memory (allows hotswapping w/o reselect)
            self.master_image = Image.open(self.master_image_path)
            file = open(self.message_path, "r", encoding="utf-8")
            self.message = file.read()
            # Encode
            encode(self.master_image, self.message, self.character_list,
                   offset=self.enigma)

# Tkinter window class
class Window(tk.Frame):
    def __init__(self, master=None, data_class=None):
        tk.Frame.__init__(self, master)
        self.master = master
        self.data = data_class # Used for storing/modifying ALL variables
        self.setup()

    def setup(self):
        # Window misc.
        self.master.title("Image Coder")
        self.pack(fill=tk.BOTH, expand=1)

        # Labels
        master_image_label = tk.Label(self, textvar=self.data.master_image_string,
                                      padx=5, pady=5, width=50)
        master_image_label.place(x=0, y=0)
        encoded_image_label = tk.Label(self, textvar=self.data.encoded_image_string,
                                      padx=5, pady=5, width=50)
        encoded_image_label.place(x=0, y=30)
        message_label = tk.Label(self, textvar=self.data.message_path_string,
                                      padx=5, pady=5, width=50)
        message_label.place(x=0, y=60)
        char_list_label = tk.Label(self, textvar=self.data.character_list_string,
                                      padx=5, pady=5, width=50)
        char_list_label.place(x=0, y=90)

        # Buttons
        master_button = tk.Button(self, text="Choose Master Image",
                                  command=self.data.set_master_image,
                                  padx=5, pady=5, width=20)
        master_button.place(x=425, y=0)
        encoded_button = tk.Button(self, text="Choose Encoded Image",
                                   command=self.data.set_encoded_image,
                                  padx=5, pady=5, width=20)
        encoded_button.place(x=425, y=30)
        message_button = tk.Button(self, text="Choose Message File",
                                    command=self.data.set_message,
                                    padx=5, pady=5, width=20)
        message_button.place(x=425, y=60)
        character_button = tk.Button(self, text="Choose Character List",
                                    command=self.data.set_character_list,
                                    padx=5, pady=5, width=20)
        character_button.place(x=425, y=90)
        # command = lambda : action(argument)
        encode_button = tk.Button(self, text="ENCODE", command=self.data.encode,
                                  padx=5, pady=5, width=9)
        encode_button.place(x=425, y=120)
        decode_button = tk.Button(self, text="DECODE", command=self.data.decode,
                                  padx=5, pady=5, width=9)
        decode_button.place(x=513, y=120)

        # Other
        enigma_label = tk.Label(self, text="Enigma Offset", padx=5, pady=5)
        enigma_label.place(x=10, y=120)
        enigma_entry = tk.Entry(self, width=5, textvar=self.data.enigma_string)
        enigma_entry.place(x=120, y=122)

        save_label = tk.Label(self, text="Save decoded message to file?",
                              padx=5, pady=5)
        save_label.place(x=200, y=120)
        save_checkbox = tk.Checkbutton(self, command=self.data.toggle_save)
        save_checkbox.place(x=392, y=122)

def main():
    # Create a Tkinter window for GUI support
    root = tk.Tk()
    root.geometry("600x150")
    
    # Create a data storage class
    data = Data(root)

    # Finish Tkinter window setup
    app = Window(root, data)
    root.mainloop()

if __name__ == "__main__":
    main()
