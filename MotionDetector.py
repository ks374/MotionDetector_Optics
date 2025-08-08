import cv2
import numpy as np
import time

class MotionDetector:
    """
    A class to detect motion from a live video stream.
    """
    def __init__(self, camera_index=0, width=640, height=480, fps = 30, threshold=10):
        """
        Initializes the motion detector.

        Args:
            camera_index (int): The index of the camera to use.
            width (int): The desired frame width.
            height (int): The desired frame height.
            threshold (int): The pixel difference threshold for motion.
        """
        self.cap = cv2.VideoCapture(camera_index)
        
        # Set camera properties
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, width)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, height)
        self.cap.set(cv2.CAP_PROP_FPS,fps)
        
        # Verify the actual set properties
        self.width = int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        self.height = int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        self.fps = self.cap.get(cv2.CAP_PROP_FPS)
        self.threshold = threshold
        
        if not self.cap.isOpened():
            raise IOError("Could not open webcam.")
        
        # Capture the first frame to initialize the background model
        ret, frame = self.cap.read()
        if not ret:
            raise IOError("Could not read first frame from webcam.")
            
        self.frame_buf_0 = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        
    def get_motion_index(self):
        """
        Reads a frame, calculates the motion index, and returns the result.

        Returns:
            tuple: A tuple containing the motion index and the current frame.
                   Returns (None, None) if the frame could not be read.
        """
        #ret, frame = self.cap.read()
        for _ in range(5):
            self.cap.grab()
        ret,frame = self.cap.retrieve()
        if not ret:
            return None, None
            
        frame_gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        
        temp_diff = cv2.absdiff(frame_gray, self.frame_buf_0)
        
        # Update the background model for the next frame
        self.frame_buf_0 = frame_gray
        
        _, threshold_diff = cv2.threshold(temp_diff, self.threshold, 255, cv2.THRESH_TOZERO)
        
        motion_index = threshold_diff.sum()
        
        return motion_index, frame
        
    def release(self):
        """
        Releases the camera and closes all OpenCV windows.
        """
        self.cap.release()
        cv2.destroyAllWindows()
"""
# Example Usage:
if __name__ == '__main__':
    try:
        detector = MotionDetector(camera_index=0, width=640, height=480, threshold=10)
        
        while True:
            motion_index, frame = detector.get_motion_index()
            
            if frame is None:
                print("End of stream or error.")
                break
            
            print(f"Motion Index: {motion_index}")
            
            # Show the live feed (optional)
            cv2.imshow('Live Camera', frame)
            
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
                
    except IOError as e:
        print(f"An error occurred: {e}")
    finally:
        detector.release()
"""