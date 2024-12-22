import torch
import cv2
import time

device = torch.device('cuda:0' if torch.cuda.is_available() else 'cpu')
model = torch.hub.load('ultralytics/yolov5', 'custom', path='model.pt').to(device)

# Initialize webcam
cap = cv2.VideoCapture(0)

# Set the width and height of the video capture (resolution)
cap.set(cv2.CAP_PROP_XI_WIDTH, 1280)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)

# Initialize variables to calculate FPS
fps = 0
frame_count = 0
start_time = time.time()

frame_skip = 2 # Skip every 2nd frame for faster processing

while cap.isOpened():
    _, frame = cap.read()

    # Increment frame counter
    frame_count += 1

    # Skip frames to improve FPS (process only every other frame)
    if frame_count % frame_skip != 1:  # Skip frame 2, 4, 6, etc., and process 1, 3, 5, etc.
        continue

    # Calculate FPS every second (or adjust the timing as needed)
    elapsed_time = time.time() - start_time
    if elapsed_time >= 1:   # Update FPS every second
        fps = frame_count / elapsed_time
        frame_count = 0
        start_time = time.time()
    
    # Display FPS on the frame
    cv2.putText(frame, f"FPS: {fps:.2f}", (10, 40), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2, cv2.LINE_AA)
    
    results = model(frame)
    detections = results.pandas().xyxy[0]
    
    # Extract the coordinates, class name, and confidence for each detection
    for i, detection in detections.iterrows():
        x1, y1, x2, y2 = detection[['xmin', 'ymin', 'xmax', 'ymax']]
        x1, y1, x2, y2 = [round(num) for num in [x1, y1, x2, y2]]

        class_name = detection['name']
        confidence = detection['confidence']

        # Check confidence
        if confidence > 0.8:
            # Draw bounding box on input image
            cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)

            # Put label text on bounding box
            label = f'{class_name} {confidence:.2f}'
            label_size, baseline = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.5, 1)
            cv2.rectangle(frame, (x1, y1), (x1 + label_size[0], y1 - label_size[1] - baseline), (0, 255, 0), cv2.FILLED)
            cv2.putText(frame, label, (x1, y1 - baseline), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 1)
        
    
    # Display webcam
    cv2.imshow('Webcam', frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        cap.release()
        cv2.destroyAllWindows()
        break
