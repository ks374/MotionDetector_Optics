import cv2
import numpy as np
import matplotlib.pyplot as plt

class MotionPlotter:
    """
    A class to dynamically plot motion data.
    """
    def __init__(self, reward_threshold = 500000, max_points=200):
        """
        Initializes the plot in interactive mode.

        Args:
            max_points (int): The maximum number of data points to display on the plot.
        """
        self.max_points = max_points
        self.motion_data = [0]*self.max_points

        plt.ion() # Enable interactive mode
        self.fig, self.ax = plt.subplots(figsize=(8, 4))
        self.line, = self.ax.plot([], [])
        self.ax.set_title('Real-time Motion Index')
        self.ax.set_xlabel('Frame Index')
        self.ax.set_ylabel('Total Pixel Difference')
        self.ax.axhline(y=reward_threshold,color='r',linestyle = '--')
        #self.ax.grid(True)

    def update(self, motion_index):
        """
        Appends a new motion index and updates the plot.

        Args:
            motion_index (int): The new motion index value.
        """
        self.motion_data.append(motion_index)
        
        # Keep the data list size limited
        if len(self.motion_data) > self.max_points:
            self.motion_data = self.motion_data[-self.max_points:]
            
        # Update plot data
        self.line.set_xdata(range(len(self.motion_data)))
        self.line.set_ydata(self.motion_data)
        
        # Adjust plot limits
        self.ax.relim()
        self.ax.autoscale_view()
        
        # Redraw the plot
        self.fig.canvas.draw()
        self.fig.canvas.flush_events()

    def release(self):
        """
        Turns off interactive mode and shows the final plot.
        """
        plt.ioff()
        plt.show()



"""
# Main execution block to demonstrate how the classes work together
if __name__ == '__main__':
    try:
        detector = MotionDetector(camera_index=0)
        plotter = MotionPlotter(max_points=100)
        
        while True:
            motion_index, frame = detector.get_motion_index()
            
            if frame is None:
                print("End of stream or error.")
                break
            
            # Update the motion plotter
            plotter.update(motion_index)
            
            # Show the live video feed
            cv2.imshow('Live Camera', frame)
            
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
                
    except IOError as e:
        print(f"An error occurred: {e}")
    finally:
        detector.release()
        plotter.release()
"""