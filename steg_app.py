import customtkinter as ctk
import tkinter.messagebox
import PIL.Image
import os.path


def genData(data):

        # list of binary codes of given data
        newd = []

        for i in data:
            newd.append(format(ord(i), '08b'))
        return newd

def modPix(pix, data):

    datalist = genData(data)
    lendata = len(datalist)
    imdata = iter(pix)

    for i in range(lendata):

        # Extracting 3 pixels at a time
        pix = [value for value in imdata.__next__()[:3] + imdata.__next__()[:3] + imdata.__next__()[:3]]

        # Pixel value should be made odd for 1 and even for 0
        for j in range(0, 8):
            if datalist[i][j] == '0' and pix[j]% 2 != 0:
                pix[j] -= 1

            elif datalist[i][j] == '1' and pix[j] % 2 == 0:
                if(pix[j] != 0):
                    pix[j] -= 1
                else:
                    pix[j] += 1
                # pix[j] -= 1

        # Eighth pixel of every set tells whether to stop to read further. 0 means keep reading; 1 means the
        # message is over.
        if i == lendata - 1:
            if pix[-1] % 2 == 0:
                if pix[-1] != 0:
                    pix[-1] -= 1
                else:
                    pix[-1] += 1

        else:
            if pix[-1] % 2 != 0:
                pix[-1] -= 1

        pix = tuple(pix)
        yield pix[0:3]
        yield pix[3:6]
        yield pix[6:9]

def encode_enc(newimg, data):
    w = newimg.size[0]
    (x, y) = (0, 0)

    for pixel in modPix(newimg.getdata(), data):

        # Putting modified pixels in the new image
        newimg.putpixel((x, y), pixel)
        if x == w - 1:
            x = 0
            y += 1
        else:
            x += 1

def encode_image(file_path: str, message: str):
    img = file_path
    image = PIL.Image.open(img, 'r')

    newimg = image.copy()
    encode_enc(newimg, message)

    new_img_name = "encoded.png"
    newimg.save(new_img_name, str(new_img_name.split(".")[1].upper()))

def decode_image(encoded_image_path):
    img = encoded_image_path
    image = PIL.Image.open(img, 'r')

    data = ''
    imgdata = iter(image.getdata())

    while (True):
        pixels = [value for value in imgdata.__next__()[:3] + imgdata.__next__()[:3] + imgdata.__next__()[:3]]

        # string of binary data
        binstr = ''

        for i in pixels[:8]:
            if i % 2 == 0:
                binstr += '0'
            else:
                binstr += '1'

        data += chr(int(binstr, 2))
        if pixels[-1] % 2 != 0:
            return data


class Main:

    ctk.set_appearance_mode("Dark")
    ctk.set_default_color_theme("green")
    secret_message = None
    current_image_pth = None

    def __init__(self):
        self.__main_window = ctk.CTk()
        self.__main_window.title("Steganography App")
        self.__main_window.geometry("1280x700")
        self.__main_window.minsize(800, 500)
        self.__main_window.maxsize(1280, 700)
        self.__main_window.resizable(True, False)

        # original/compressed image frame
        self.__original_image_frame = ctk.CTkFrame(self.__main_window)
        self.__original_image_frame.pack(fill="both", side="left", padx=18, pady=18, expand=True)
        self.__original_image_frame.pack_propagate(False)

        self.__image_frame_org = ctk.CTkLabel(self.__original_image_frame, text="")
        self.__image_frame_org.pack(fill="both", expand=True, padx=10, pady=10)

        self.__open_image_org_btn = ctk.CTkButton(self.__original_image_frame, text="Open Image", cursor="hand2", height=34)
        self.__open_image_org_btn.configure(command=self.open_org_image, font=("Normal", 18))
        self.__open_image_org_btn.pack(fill="x", padx=10, pady=10)

        self.__file_name_label = ctk.CTkLabel(self.__original_image_frame, text="File Name: ", anchor="w", font=("Normal", 18))
        self.__file_name_label.pack(fill="x", padx=10, pady=(0, 10))

        self.__file_size_label = ctk.CTkLabel(self.__original_image_frame, text="File Size: ", anchor="w", font=("Normal", 18))
        self.__file_size_label.pack(fill="x", padx=10, pady=(0, 10))

        # button frame
        self.__button_frame = ctk.CTkFrame(self.__main_window)
        self.__button_frame.pack(side="left", padx=18, pady=18)

        self.__enter_message_btn = ctk.CTkButton(self.__button_frame, text="Enter Secret Message", height=34, cursor="hand2")
        self.__enter_message_btn.configure(command=self.enter_message)
        self.__enter_message_btn.pack()

        self.__hide_message_btn = ctk.CTkButton(self.__button_frame, text="Encode Image", state="disabled", height=34, cursor="hand2")
        self.__hide_message_btn.configure(command=self.hide_message)
        self.__hide_message_btn.pack(pady=(10, 0))

        self.__extract_hidden_message = ctk.CTkButton(self.__button_frame, text="Extract Hide Image", state="disabled", height=34, cursor="hand2")
        self.__extract_hidden_message.configure(command=self.decode_message)
        self.__extract_hidden_message.pack(pady=(10, 0))

        # compressed image frame
        self.__hidden_message_image_frame = ctk.CTkFrame(self.__main_window)
        self.__hidden_message_image_frame.pack(fill="both", expand=True, side="left", padx=18, pady=18)
        self.__hidden_message_image_frame.pack_propagate(False)

        self.__image_frame_com = ctk.CTkLabel(self.__hidden_message_image_frame, text="")
        self.__image_frame_com.pack(fill="both", expand=True, padx=10, pady=10)

        self.__open_image_com_btn = ctk.CTkButton(self.__hidden_message_image_frame, text="Open Image", cursor="hand2", height=34)
        self.__open_image_com_btn.configure(state="disabled", font=("Normal", 18))
        self.__open_image_com_btn.pack(fill="x", padx=10, pady=10)

        self.__file_name_label_com = ctk.CTkLabel(self.__hidden_message_image_frame, text="File Name: ", anchor="w", font=("Normal", 18))
        self.__file_name_label_com.pack(fill="x", padx=10, pady=(0, 10))

        self.__file_size_label_com = ctk.CTkLabel(self.__hidden_message_image_frame, text="File Size: ", anchor="w", font=("Normal", 18))
        self.__file_size_label_com.pack(fill="x", padx=10, pady=(0, 10))

        self.__main_window.mainloop()

    def open_org_image(self):
        self.__image_frame_com.configure(image=None)

        try:
            file_types = [("Image files", "*.jpg;*.jpeg;*.png;")]
            selected_image_path = ctk.filedialog.askopenfile(filetypes=file_types, title="Select an image file",
                                                             initialdir=r"C:\Users\niiantiaye\Pictures\3")
            self.__file_name_label.configure(text=f"File Name: {str(os.path.basename(selected_image_path.name))}")

            image_label_width, image_label_height = self.__image_frame_org.winfo_width(), self.__image_frame_org.winfo_height()
            image_copy = PIL.Image.open(selected_image_path.name)
            image = image_copy.resize((image_label_width, image_label_height))
            label_image = ctk.CTkImage(image, size=(image_label_width, image_label_height))

            self.__image_frame_org.configure(image=label_image, text="")
            self.__file_size_label.configure(text=f"File Size: {os.path.getsize(selected_image_path.name)/ (1024 * 1024):1f} MB")

            self.__hide_message_btn.configure(state="normal")
            self.__extract_hidden_message.configure(state="normal")
            self.current_image_pth = selected_image_path.name
        except AttributeError:
            pass

    def enter_message(self):
        toplevel = ctk.CTkToplevel(self.__main_window)
        toplevel.title("Enter Message")
        toplevel.geometry("500x300")

        message_entry = ctk.CTkTextbox(toplevel, font=("Normal", 18))
        message_entry.pack(fill="both", pady=10, padx=10, expand=True)

        enter_btn = ctk.CTkButton(toplevel, text="Enter Message", height=34, font=("Normal", 18))
        enter_btn.configure(command=lambda: self.entering_message(message_entry.get(1.0, ctk.END), toplevel))
        enter_btn.pack(fill="x", pady=10, padx=10)

        toplevel.mainloop()

    def entering_message(self, message, toplevel):
        self.secret_message = message
        toplevel.destroy()
        tkinter.messagebox.showinfo("Message Loaded", "The message has been loaded in bytes format")

    def hide_message(self):
        if self.secret_message is None:
            tkinter.messagebox.showerror("Encoding Image", "Enter the Secret Message before encoding the Image")
            return

        encode_image(self.current_image_pth, self.secret_message)
        self.open_com_image()

    def open_com_image(self):
        try:
            file_types = [("Image files", "*.jpg;*.jpeg;*.png;")]
            selected_image_path = ctk.filedialog.askopenfile(filetypes=file_types, title="Select the encoded file", initialdir=r"./")
            self.__file_name_label_com.configure(text=f"File Name: {str(os.path.basename(selected_image_path.name))}")

            image_label_width, image_label_height = self.__image_frame_com.winfo_width(), self.__image_frame_com.winfo_height()
            image_copy = PIL.Image.open(selected_image_path.name)
            image = image_copy.resize((image_label_width, image_label_height))
            label_image = ctk.CTkImage(image, size=(image_label_width, image_label_height))

            self.__image_frame_com.configure(image=label_image, text="")
            self.__file_size_label_com.configure(text=f"File Size: {os.path.getsize(selected_image_path.name)/ (1024 * 1024):1f} MB")
        except AttributeError:
            pass

    def decode_message(self):
        message = decode_image(self.current_image_pth)
        tkinter.messagebox.showinfo("Message", f"Your secret message in the image was:\n{message}")


if __name__ == "__main__":
    Main()