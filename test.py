import cv2
from pyzbar import pyzbar

# Initialize the webcam
cap = cv2.VideoCapture(0)
cap.set(cv2.CAP_PROP_AUTOFOCUS, 0) # turn the autofocus off
# cap.set(cv2.CAP_PROP_FOCUS, 100) # turn the autofocus off
update_focus = 0

# Check if the webcam is opened correctly
if not cap.isOpened():
    print("Error: Could not open webcam.")
    exit()

print("Press 'q' to exit the webcam feed.")
print("Press 'Up Arrow' to increase focus.")
print("Press 'Down Arrow' to decrease focus")
print("-------------- CAP SETTING --------------")
print("AUTO FOCUS : ", cap.get(cv2.CAP_PROP_AUTOFOCUS))
print("FOCUS : ", cap.get(cv2.CAP_PROP_FOCUS))

while True:
    # Capture frame-by-frame from the webcam
    ret, frame = cap.read()

    # Check if the frame was captured successfully
    if not ret:
        print("Failed to capture image from webcam.")
        break

    # Find the barcodes in the image and decode each barcode
    barcodes = pyzbar.decode(frame)

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

        # Print the barcode type and data to the terminal
        print("[INFO] Found {} barcode: {}".format(barcodeType, barcodeData))

    # Display the resulting frame with barcode annotations
    cv2.imshow("Barcode Scanner", frame)

    # Exit the loop if the user presses the 'q' key
    key = cv2.waitKey(1)
    if key == ord('q'):
        break
    elif key == ord('w'): # Up Arrow Key (increase focus)
        current_focus = update_focus
        new_focus = min(current_focus + 10, 255) # Increase focus, max value is 255
        update_focus = new_focus
        cap.set(cv2.CAP_PROP_FOCUS, update_focus)
        print("Increase focus from {} to {}.".format(current_focus, new_focus))
    elif key == ord('s'): # Down Arroy key (decase focus)
        current_focus = update_focus
        new_focus = max(current_focus - 10, 0) # Decrease focus, max value is 255
        update_focus = new_focus
        cap.set(cv2.CAP_PROP_FOCUS, update_focus)
        print("Decrease focus from {} to {}.".format(current_focus, new_focus))

# Release the webcam and close all OpenCV windows
cap.release()
cv2.destroyAllWindows()
