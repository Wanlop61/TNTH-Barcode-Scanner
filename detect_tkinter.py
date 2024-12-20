import cv2
from tkinter import *
from tkinter import messagebox
from PIL import Image, ImageTk
from pyzbar import pyzbar

class WebcamApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Webcam Capture with Tkinter")
        self.root.geometry('600x600')

        """ Variables for functions """
        self.CAP_INDEX = 0

        # Create a Menu widget (Menu bar)
        self.menu_bar = Menu(self.root)
    
        """ Create a menu options """
        # Create a File menu
        self.file_menu = Menu(self.menu_bar, tearoff=0)

        # Create a Settings menu under the File menu
        self.settings_menu = Menu(self.file_menu, tearoff=0)
        self.settings_menu.add_command(label="Color")
        self.file_menu.add_cascade(label="Settings", menu=self.settings_menu)

        self.webcam_menu = Menu(self.menu_bar, tearoff=0)
        # Create the Auto Focus checkbutton, default state is 'on'
        self.auto_focus_var = IntVar(value=1)  # Set the default value to 1 (Auto Focus enabled)
        self.webcam_menu.add_checkbutton(label="Auto Focus", onvalue=1, offvalue=0, command=self.toggle_auto_focus, variable=self.auto_focus_var)
        self.file_menu.add_separator()
        self.file_menu.add_command(label="Exit", command=self.close)

        # Create a Menu
        self.templates_menu = Menu(self.menu_bar, tearoff=0)
        self.templates_menu.add_command(label="Choose")

        # Add the 'File' menu to the menu bar
        self.menu_bar.add_cascade(label="File", menu=self.file_menu)
        # Add the 'Webcam' menu to the menu bar
        self.menu_bar.add_cascade(label="Webcam", menu=self.webcam_menu)
        # Add the 'Templates' menu to the menu bar
        self.menu_bar.add_cascade(label="Templates", menu=self.templates_menu)

        # Configure the window to use the menu bar
        self.root.config(menu=self.menu_bar)
        
        # Create a Label widget to display the webcam feed
        self.video_label = Label(root)
        self.video_label.pack()

        # Create the trackbar (scale) for manual focus adjustment
        self.focus_scale = Scale(root, from_=0, to=255, orient=HORIZONTAL, label="Focus", command=self.update_focus)
        self.focus_scale.set(0) # Initial focus value
        self.focus_scale.pack()
        
        # Open the webcam
        # self.cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
        self.start_webcam()

        # Initial settings
        self.auto_focus = True

        # Call the toggle_auto_focus method to hide the focus slider if autofocus is enabled
        self.toggle_auto_focus()
        
        # Start the video stream
        self.update_frame()

    def start_webcam(self):
        # Start the video stream
        self.cap = cv2.VideoCapture(self.CAP_INDEX, cv2.CAP_DSHOW)
        self.cap.set(cv2.CAP_PROP_AUTOFOCUS, 1) # Enable auto focus by default
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 800)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 800)
    
    def reconnect_webcam(self):
        print("Attempting to reconnect to the webcam...")
        self.root.title("Attempting to reconnect to the webcam...")
        self.cap.release()
        self.start_webcam()

    def toggle_auto_focus(self):
        """ Toggle the auto focus setting """
        self.auto_focus = self.auto_focus_var.get() == 1
        if self.auto_focus:
            self.cap.set(cv2.CAP_PROP_AUTOFOCUS, 1)  # Enable autofocus
            self.focus_scale.set(0)  # Reset scale to 0 when auto-focus is on
            self.focus_scale.pack_forget()  # Hide the scale widget when autofocus is on
        else:
            self.cap.set(cv2.CAP_PROP_AUTOFOCUS, 0)  # Disable autofocus
            self.focus_scale.pack()  # Show the scale widget when autofocus is off
    
    def update_focus(self, val):
        """Callback function for scale to update the focus."""
        if not self.auto_focus:  # Only adjust focus if autofocus is off
            self.cap.set(cv2.CAP_PROP_FOCUS, int(val))

    def preprocess_image(self, frame):
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        blurred = cv2.GaussianBlur(gray, (3, 3), 0)
        _, thresh = cv2.threshold(blurred, 100, 255, cv2.THRESH_TRUNC)
        # clahe = cv2.createCLAHE(clipLimit=2, tileGridSize=(8,8))
        # cl1 = clahe.apply(thresh)
        return thresh

    def update_frame(self):
        """Capture and display each frame from the webcam."""
        ret, frame = self.cap.read()

        if ret:
            self.root.title("Webcam Capture with Tkinter")
            # Pre-processing image for better decoding
            morph = self.preprocess_image(frame)
            cv2.imshow("Processing Image", morph)
          
            # Find the barcodes in the image and decode each barcode
            barcodes = pyzbar.decode(morph)

            # Loop over the detected barcodes
            for barcode in barcodes:
                # Extract the bounding box location of the barcode and draw a bounding box around the barcode
                (x, y, w, h) = barcode.rect
                frame = cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 0, 255), 2)

                # The barcode data is a bytes object, so we need to convert it to a string
                barcodeData = barcode.data.decode("utf-8")
                barcodeType = barcode.type

                 # Draw the barcode data and barcode type on the image
                text = "{} ({})".format(barcodeData, barcodeType)
                cv2.putText(frame, text, (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX,
                            0.5, (0, 0, 255), 2)
            # Convert the frame from BGR to RGB (OpenCV uses BGR)
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            
            # Convert the frame to a PIL Image
            img = Image.fromarray(frame)
            
            # Convert the Image to a format tkinter can handle (PhotoImage)
            img_tk = ImageTk.PhotoImage(image=img)
            
            # Update the label with the new image
            self.video_label.config(image=img_tk)
            self.video_label.image = img_tk

            # Call the method again after 10ms to update the frame
            # self.root.after(50, self.update_frame)
        else:
            self.reconnect_webcam()

        self.root.after(50, self.update_frame)

    def close(self):
        """Release the webcam and close the tkinter window."""
        # self.cap.release()
        self.root.quit()

def main():
    root = Tk()
    app = WebcamApp(root)
    
    # Ensure the window closes properly
    root.protocol("WM_DELETE_WINDOW", app.close)

    root.mainloop()

if __name__ == "__main__":
    main()
