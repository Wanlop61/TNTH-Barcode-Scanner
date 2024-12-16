import cv2
from pyzbar import pyzbar

# Initialize the webcam
cap = cv2.VideoCapture(0)

# Check if the webcam is opened correctly
if not cap.isOpened():
    print("Error: Could not open webcam.")
    exit()

print("Press 'q' to exit the webcam feed.")

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
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Release the webcam and close all OpenCV windows
cap.release()
cv2.destroyAllWindows()
