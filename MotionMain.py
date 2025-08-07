from MotionDetector import MotionDetector
from MotionPlotter import MotionPlotter

if __name__ == '__main__':
    try:
        detector = MotionDetector(camera_index=0)
        plotter = MotionPlotter(reward_threshold = 500000,max_points=200)
        
        while True:
            motion_index, frame = detector.get_motion_index()
            
            if frame is None:
                print("End of stream or error.")
                break
            
            # Update the motion plotter
            plotter.update(motion_index)
            
                
    except IOError as e:
        print(f"An error occurred: {e}")
    finally:
        detector.release()
        plotter.release()
