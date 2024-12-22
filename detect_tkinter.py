import cv2
from tkinter import *
from PIL import Image, ImageTk
from pyzbar import pyzbar
import easyocr
import time

class WebcamApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Webcam Capture with Tkinter")
        # self.root.geometry('800x800')

        self.reader = easyocr.Reader(['en'])
        self.CAP_INDEX = 0
        self.initialize_menu()
        
        # Create a Label widget to display the webcam feed
        self.video_label = Label(root)
        self.video_label.pack()

        # Create the trackbar (scale) for manual focus adjustment
        self.focus_scale = Scale(root, from_=0, to=255, orient=HORIZONTAL, label="Focus", command=self.update_focus)
        self.focus_scale.set(0) # Initial focus value
        self.focus_scale.pack()
        
        # Open the webcam
        self.start_webcam()

        # Call the toggle_auto_focus method to hide the focus slider if autofocus is enabled
        self.toggle_auto_focus()
        
        # Start the video stream
        self.update_frame()
    
    def initialize_menu(self):
        menu_bar = Menu(self.root)

        # Create a File menu
        file_menu = Menu(menu_bar, tearoff=0)
        menu_bar.add_cascade(label="File", menu=file_menu)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.close)
        
        # Create a Webcam menu
        webcam_menu = Menu(menu_bar, tearoff=0)
        menu_bar.add_cascade(label="Webcam", menu=webcam_menu)
        # self.auto_focus = True
        self.auto_focus = IntVar(value=1)
        webcam_menu.add_checkbutton(label="Auto Focus", onvalue=1, offvalue=0, command=self.toggle_auto_focus, variable=self.auto_focus)
        
        # Display menu
        self.root.config(menu=menu_bar)
        

    def start_webcam(self):
        # Start the video stream
        self.cap = cv2.VideoCapture(self.CAP_INDEX)
        self.cap.set(cv2.CAP_PROP_AUTOFOCUS, 1) # Enable auto focus by default
        # self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 400)
        # self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 400)
        print(f"Webcam {self.CAP_INDEX} resolution: {int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH))}x{int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))}")
    
    def reconnect_webcam(self):
        print("Attempting to reconnect to the webcam...")
        self.root.title("Attempting to reconnect to the webcam...")
        self.cap.release()
        self.start_webcam()

    def toggle_auto_focus(self):
        """ Toggle the auto focus setting """
        auto_focus = self.auto_focus.get() == 1
        if auto_focus:
            self.cap.set(cv2.CAP_PROP_AUTOFOCUS, 1)  # Enable autofocus
            self.focus_scale.set(0)  # Reset scale to 0 when auto-focus is on
            self.focus_scale.pack_forget()  # Hide the scale widget when autofocus is on
        else:
            self.cap.set(cv2.CAP_PROP_AUTOFOCUS, 0)  # Disable autofocus
            self.focus_scale.pack()  # Show the scale widget when autofocus is off
    
    def update_focus(self, val):
        if not self.auto_focus:  # Only adjust focus if autofocus is off
            self.cap.set(cv2.CAP_PROP_FOCUS, int(val))

    def preprocess_image(self, frame):
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        blurred = cv2.GaussianBlur(gray, (3, 3), 0)
        _, thresh = cv2.threshold(blurred, 100, 255, cv2.THRESH_TRUNC)
        # clahe = cv2.createCLAHE(clipLimit=2, tileGridSize=(8,8))
        # cl1 = clahe.apply(thresh)
        return thresh
    
    def draw_ocr_area(self, frame):
        # Get the dimension of the image
        height, width = frame.shape[:2]  # Unpack to 2 variables (height, width)
        
        # Define the size of the rectangle (width and height)
        rect_width = width * 40 // 100
        rect_height = height * 30 // 100
        
        # Calculate the center of the frame
        center_x, center_y = width // 2, height // 2
        
        # Calculate the top-left corner of the rectangle
        top_left_x = center_x - rect_width // 2
        top_left_y = center_y - rect_height // 2
        
        # Calculate the bottom-right corner of the rectangle
        bottom_right_x = center_x + rect_width // 2
        bottom_right_y = center_y + rect_height // 2
        
        # Draw the rectangle at the center of the frame
        cv2.rectangle(frame, (top_left_x, top_left_y), (bottom_right_x, bottom_right_y), (0, 0, 255), 2)
        
        # Return the frame and the rectangle coordinates
        return frame, (top_left_x, top_left_y, bottom_right_x, bottom_right_y)

    def perform_ocr(self, frame, reader, bbox):
        # Crop the region of interest (ROI) inside the rectangle using bbox coordinates
        roi = frame[bbox[1]:bbox[3], bbox[0]:bbox[2]]
        
        # Perform OCR on the cropped region
        results = reader.readtext(roi)
        
        # Iterate over the result to draw bounding boxes and add text
        for (coord, text, prob) in results:
            (top_left, top_right, bottom_right, bottom_left) = coord
            tx, ty = (int(top_left[0]), int(top_left[1]))
            bx, by = (int(bottom_right[0]), int(bottom_right[1]))

            # Adjust coordinates for the main frame (since OCR is done on the cropped ROI)
            tx += bbox[0]  # Offset by the x-coordinate of the bounding box
            ty += bbox[1]  # Offset by the y-coordinate of the bounding box
            bx += bbox[0]
            by += bbox[1]

            # Draw a rectangle around the detected text in the original frame
            cv2.rectangle(frame, (tx, ty), (bx, by), (0, 255, 0), 2)

            # Put the detected text on the image
            cv2.putText(frame, text, (tx, ty - 10), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)

        return frame

    def update_frame(self):
        """Capture and display each frame from the webcam."""
        ret, frame = self.cap.read()

        if ret:
            self.root.title("Webcam Capture with Tkinter")
            bbox = self.draw_ocr_area(frame)[1]

            # Pre-processing image for better decoding
            morph = self.preprocess_image(frame)
            # cv2.imshow("Processing Image", morph)
          
            # Find the barcodes in the image and decode each barcode
            barcodes = pyzbar.decode(morph)
            if barcodes:
                frame = self.perform_ocr(frame, self.reader, bbox)
        
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

        else:
            self.reconnect_webcam()

        self.root.after(100, self.update_frame)

    def close(self):
        self.cap.release()
        self.root.quit()

def main():
    root = Tk()
    app = WebcamApp(root)
    
    # Ensure the window closes properly
    root.protocol("WM_DELETE_WINDOW", app.close)

    root.mainloop()

if __name__ == "__main__":
    main()
