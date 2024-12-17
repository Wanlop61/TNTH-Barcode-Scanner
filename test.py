import cv2
from pyzbar import pyzbar

# Global variables
NAMED_WINDOW = "Barcode Reader" 

# Initialize the webcam
cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
cap.set(cv2.CAP_PROP_AUTOFOCUS, 0) # turn the autofocus off

# Check if the webcam is opened correctly
if not cap.isOpened():
    print("Error: Could not open webcam.")
    exit()

print("Press 'q' to exit the webcam feed.")

# Create a window to display the video focus
cv2.namedWindow(NAMED_WINDOW)

# Create a tracbar (slider) to control focus
# The tracbar will range from 0 to 255
cv2.createTrackbar("Focus", NAMED_WINDOW, 0, 255, lambda x: None)

while True:
    # Capture frame-by-frame from the webcam
    ret, frame = cap.read()

    # Check if the frame was captured successfully
    if not ret:
        print("Failed to capture image from webcam.")
        break

    # Get current position of trackbars
    focus_value = cv2.getTrackbarPos("Focus", NAMED_WINDOW)
    
    # Update value following trackbars
    cap.set(cv2.CAP_PROP_FOCUS, focus_value)

    # Find the barcodes in the image and decode each barcode
    barcodes = pyzbar.decode(frame)

    barcode_found = False # Flag to track if barcode is detected

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
        
        # Set the flag to True when a barcode is detected
        barcode_found = True

        # Print the barcode type and data to the terminal
        # print("[INFO] Found {} barcode: {}".format(barcodeType, barcodeData))
    
    # If a barcode was found, display a success message
    if barcode_found:
        cv2.putText(frame, "Barcode Detected! Focus is good.", (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 
                    1, (0, 255, 0), 2, cv2.LINE_AA)
    else:
        cv2.putText(frame, "No barcode detected.", (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 
                    1, (0, 0, 255), 2, cv2.LINE_AA) 

    # Display the resulting frame with barcode annotations
    cv2.imshow(NAMED_WINDOW, frame)

    # Exit the loop if the user presses the 'q' key
    key = cv2.waitKey(1)
    if key == ord('q'):
        break

# Release the webcam and close all OpenCV windows
cap.release()
cv2.destroyAllWindows()
