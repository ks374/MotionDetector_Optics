import cv2
import numpy as np
import pygame
import collections

class Motion_PYPE_System:
    """
    A class that integrates real-time motion detection from a webcam with
    a Pygame visualization system.

    This class handles camera setup, motion analysis, and drawing of both
    the live video feed and a dynamic motion plot on a Pygame window.
    """
    def __init__(self, camera_index=0, cam_width=640, cam_height=480, threshold=10, history_size=100):
        """
        Initializes the motion detection and Pygame display system.

        Args:
            camera_index (int): The index of the webcam to use (e.g., 0 for default).
            cam_width (int): The desired width for the camera feed and Pygame display.
            cam_height (int): The desired height for the camera feed and Pygame display.
            threshold (int): The pixel intensity difference threshold for motion detection.
            history_size (int): The number of recent motion values to display on the plot.
        """
        self.running = True
        self.threshold = threshold
        self.history_size = history_size

        # 1. Camera setup using OpenCV
        self.cap = cv2.VideoCapture(camera_index)
        if not self.cap.isOpened():
            raise IOError(f"Could not open webcam at index {camera_index}.")
        
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, cam_width)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, cam_height)
        self.cam_width = int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        self.cam_height = int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        print(f"Camera streaming at: {self.cam_width}x{self.cam_height}")

        ret, frame = self.cap.read()
        if not ret:
            raise IOError("Could not read initial frame for background model.")
        self.frame_buf_0 = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        
        # 2. Pygame setup
        pygame.init()
        self.screen_size = (self.cam_width, self.cam_height + 250) # Extra space for the plot
        self.screen = pygame.display.set_mode(self.screen_size)
        pygame.display.set_caption("Motion Detector with Pygame Plot")
        self.clock = pygame.time.Clock()
        
        # 3. Data structures for the motion plot
        self.motion_history = collections.deque(maxlen=self.history_size)
        
    def _get_motion_index_and_frame(self):
        """
        Internal function to read a frame and calculate the motion index.
        """
        ret, frame = self.cap.read()
        if not ret:
            return None, None
            
        frame_gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        
        temp_diff = cv2.absdiff(frame_gray, self.frame_buf_0)
        self.frame_buf_0 = frame_gray
        
        _, threshold_diff = cv2.threshold(temp_diff, self.threshold, 255, cv2.THRESH_TOZERO)
        
        motion_index = threshold_diff.sum()
        
        return motion_index, frame

    def _draw_motion_plot(self):
        """
        Internal function to draw the dynamic bar plot on the Pygame screen.
        """
        plot_x_start = 50
        plot_y_start = self.cam_height + 50
        plot_width = self.screen_size[0] - 100
        plot_height = self.screen_size[1] - plot_y_start - 50
        
        # Draw plot border
        pygame.draw.rect(self.screen, (200, 200, 200),
                         (plot_x_start, plot_y_start, plot_width, plot_height), 2)
        
        # Draw bars if there is data
        if self.motion_history:
            max_val = max(self.motion_history) if max(self.motion_history) > 0 else 1
            bar_width = plot_width / self.history_size
            
            for i, motion_val in enumerate(self.motion_history):
                # Normalize motion value to plot height
                height = int((motion_val / max_val) * plot_height)
                x_pos = plot_x_start + i * bar_width
                y_pos = plot_y_start + plot_height - height
                
                pygame.draw.rect(self.screen, (255, 255, 255), (x_pos, y_pos, bar_width, height))
        
        # Add labels
        font = pygame.font.Font(None, 24)
        text = font.render('Real-time Motion Index', True, (255, 255, 255))
        self.screen.blit(text, (plot_x_start, plot_y_start - 30))


    def update(self):
        """
        Main update function to be called inside your Pygame loop.
        It gets the latest motion data, handles events, and draws the screen.

        Returns:
            bool: True if the system is still running, False if it should exit.
        """
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
        
        # Get motion data and a frame
        motion_index, frame = self._get_motion_index_and_frame()
        if frame is None:
            self.running = False
            return self.running
        
        self.motion_history.append(motion_index)
        
        # Convert the OpenCV image to a Pygame Surface
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        frame_surface = pygame.surfarray.make_surface(frame_rgb.swapaxes(0, 1))

        # Clear the screen
        self.screen.fill((0, 0, 0))

        # Draw the live video feed
        self.screen.blit(frame_surface, (0, 0))

        # Draw the motion plot
        self._draw_motion_plot()
        
        # Update the display
        pygame.display.flip()
        
        self.clock.tick(30) # Limit FPS to 30 for stability
        
        return self.running

    def release(self):
        """
        Performs a clean shutdown of the camera and Pygame.
        """
        self.cap.release()
        pygame.quit()
        cv2.destroyAllWindows()