import cv2
import numpy as np
import matplotlib.pyplot as plt

threshold_value = 10 #The threshold for diff image in motion detection
max_plot_points = 200
reward_threshold = 500000

cap=cv2.VideoCapture(0)

cap.set(cv2.CAP_PROP_FRAME_WIDTH,640)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT,480)
cap.set(cv2.CAP_PROP_FPS,30)

frame_width = cap.get(cv2.CAP_PROP_FRAME_WIDTH)
frame_height = cap.get(cv2.CAP_PROP_FRAME_HEIGHT)
fps = cap.get(cv2.CAP_PROP_FPS)

ret,frame = cap.read()
if ret:
    frame_buf_0 = cv2.cvtColor(frame,cv2.COLOR_BGR2GRAY)
else:
    print("Error: Could not read first frame. ")
    exit()

motion_index = [0]*max_plot_points

print(f"Actual: {frame_width}x{frame_height} @ {fps} FPS")

if not cap.isOpened():
    print("Error: Could not open webcam. ")
    exit()

#Start dynamic plt:
plt.ion()
fig, ax = plt.subplots()
line, = ax.plot([],[])
ax.set_title('Real-time Motion Index')
ax.set_xlabel('Frame number')
ax.set_ylabel('Total Pixel Difference')
ax.axhline(y=reward_threshold,color='r',linestyle = '--')
#ax.grid(True)


print("Streaming start...")
while True:
    ret,frame = cap.read()
    if not ret:
        print("End of video stream. ")
        break

    frame = cv2.cvtColor(frame,cv2.COLOR_BGR2GRAY)
    temp_diff = cv2.absdiff(frame,frame_buf_0)
    frame_buf_0 = frame
    ret,threshold_diff = cv2.threshold(temp_diff,threshold_value,255,cv2.THRESH_TOZERO)
    motion_index.append(threshold_diff.sum())
    if len(motion_index) > max_plot_points:
        motion_index = motion_index[-max_plot_points:]

    line.set_xdata(range(len(motion_index)))
    line.set_ydata(motion_index)
    ax.relim()
    ax.autoscale_view()
    fig.canvas.draw()
    fig.canvas.flush_events()


cap.release()
cv2.destroyAllWindows()
plt.ioff()
plt.show()
