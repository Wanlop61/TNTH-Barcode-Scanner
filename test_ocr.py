import easyocr
import cv2

def draw_ocr_area(frame):
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

def initialize_webcam(cap_index=0):
    cap = cv2.VideoCapture(cap_index)
    if not cap.isOpened():
        print("Error: Could not access the camera.")
        exit()
    print(f"WIDTH: {cap.get(cv2.CAP_PROP_FRAME_WIDTH)}")
    print(f"HEIGHT: {cap.get(cv2.CAP_PROP_FRAME_HEIGHT)}")
    return cap

def perform_ocr(frame, reader, bbox):
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

def run_webcam():
    # Initialize the OCR reader
    reader = easyocr.Reader(['en'])
    
    # Initialize webcam
    cap = initialize_webcam(1)
    
    while True:
        ret, frame = cap.read()
        
        if not ret:
            print("Error: Failed to grab frame.")
            break

        # Draw the rectangle on the frame
        image, bbox = draw_ocr_area(frame)
        
        # Perform OCR on the area inside the rectangle
        image = perform_ocr(image, reader, bbox)
        
        # Display the image with the annotations
        cv2.imshow("Annotated Image", image)
        
        # Wait for a key press and close the displayed image
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    
    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    run_webcam()
