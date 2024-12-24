import cv2
import numpy as np

class LabelAreaDetector:
    def __init__(self, width=640, height=480, top_margin=15, right_margin=8, 
                 bottom_margin=8, left_margin=8):
        self.width = width
        self.height = height
        self.top_margin = top_margin
        self.right_margin = right_margin
        self.bottom_margin = bottom_margin
        self.left_margin = left_margin

    def _draw_rectangle(self, biggest_points, frame):
        """Draw rectangle on the frame using the detected points"""
        for i in range(4):
            j = (i + 1) % 4
            start = (biggest_points[i][0][0], biggest_points[i][0][1])
            end = (biggest_points[j][0][0], biggest_points[j][0][1])
            cv2.line(frame, start, end, (0, 255, 0), 2)

    def _adjust_points_with_margins(self, points):
        """Adjust points with individual margins for each side"""
        # Calculate center point
        center_x = np.mean(points[:, 0])
        center_y = np.mean(points[:, 1])
        
        # Create new points array
        new_points = points.copy()
        
        # Process each point
        for i in range(4):
            x, y = points[i]
            
            # Determine point position relative to center
            is_left = x < center_x
            is_top = y < center_y
            
            # Apply horizontal margin
            if is_left:
                x_margin = self.left_margin
            else:
                x_margin = self.right_margin
                
            # Apply vertical margin
            if is_top:
                y_margin = self.top_margin
            else:
                y_margin = self.bottom_margin
                
            # Calculate new position
            if x < center_x:
                new_points[i][0] = x + x_margin
            else:
                new_points[i][0] = x - x_margin
                
            if y < center_y:
                new_points[i][1] = y + y_margin
            else:
                new_points[i][1] = y - y_margin
                
        return new_points

    def get_warped_image(self, image):
        """Main function to process image and return warped perspective"""
        # Resize image to standard dimensions
        image = cv2.resize(image, (self.width, self.height))
        
        # Image preprocessing
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        blur = cv2.GaussianBlur(gray, (5, 5), 1)
        canny = cv2.Canny(blur, 30, 150)
        
        # Find contours
        contours, _ = cv2.findContours(canny, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        # Find biggest rectangular contour
        max_area = 0
        biggest = []
        for contour in contours:
            area = cv2.contourArea(contour)
            if area > 500:
                peri = cv2.arcLength(contour, True)
                edges = cv2.approxPolyDP(contour, 0.02 * peri, True)
                if area > max_area and len(edges) == 4:
                    biggest = edges
                    max_area = area
        
        # If no suitable contour found, return original image
        if len(biggest) == 0:
            return image
            
        # Process corner points
        biggest = biggest.reshape((4, 2))
        biggest_new = np.zeros((4, 1, 2), dtype=np.int32)
        
        # Find corners using sum and difference
        add = biggest.sum(1)
        biggest_new[0] = biggest[np.argmin(add)]  # Top-left
        biggest_new[3] = biggest[np.argmax(add)]  # Bottom-right
        diff = np.diff(biggest, axis=1)
        biggest_new[1] = biggest[np.argmin(diff)]  # Top-right
        biggest_new[2] = biggest[np.argmax(diff)]  # Bottom-left

        # Adjust points with margins
        biggest_new = biggest_new.reshape((4, 2))
        adjusted_points = self._adjust_points_with_margins(biggest_new)
        biggest_new = adjusted_points.reshape((4, 1, 2))
        
        # Apply perspective transform
        pts1 = np.float32(biggest_new)
        pts2 = np.float32([[0, 0], [self.width, 0], [0, self.height], [self.width, self.height]])
        matrix = cv2.getPerspectiveTransform(pts1, pts2)
        warped_image = cv2.warpPerspective(image, matrix, (self.width, self.height))
        
        return warped_image