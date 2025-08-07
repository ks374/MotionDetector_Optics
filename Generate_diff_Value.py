import cv2
import numpy as np
import matplotlib.pyplot as plt

project_directory = "D:\\Research\\Projects\\Project_31_Postdoc_Start\\Sitting_Still_Optics\\Test_Videos\\"
cap = cv2.VideoCapture('D:\\Research\\Projects\\Project_31_Postdoc_Start\\Sitting_Still_Optics\\Test_Videos\\WIN_20250807_11_29_46_Pro.mp4')
#output_file = 'D:\\Research\\Projects\\Project_31_Postdoc_Start\\Sitting_Still_Optics\\Test_Videos\\WIN_20250807_11_21_24_Pro_processed.mp4'

threshold_value = 10 #The threshold for diff image in motion detection

motion_index = list()

if not cap.isOpened():
    print("Error: Could not open video file. ")
else:
    frame_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    frame_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fps = cap.get(cv2.CAP_PROP_FPS)
    print(f"Video props: Width = {frame_width}, Height = {frame_height}, FPS = {fps}")

    ret,frame = cap.read()
    frame_buf_0 = cv2.cvtColor(frame,cv2.COLOR_BGR2GRAY)
    
    #frame_reader = 1
    #dif_array = list()

    #fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    #out = cv2.VideoWriter(output_file,fourcc,fps,(frame_width,frame_height))
    
    while True:
        ret,frame = cap.read()
        if not ret:
            print("End of video stream. ")
            break

        frame = cv2.cvtColor(frame,cv2.COLOR_BGR2GRAY)
        temp_diff = cv2.absdiff(frame,frame_buf_0)
        #temp_diff = cv2.cvtColor(temp_diff,cv2.COLOR_GRAY2BGR)

        frame_buf_0 = frame

        ret,threshold_diff = cv2.threshold(temp_diff,threshold_value,255,cv2.THRESH_TOZERO)
        motion_index.append(threshold_diff.sum())

        #flattened_image = temp_diff.flatten()
        #hist_values,bin_edges = np.histogram(flattened_image,bins=256,range=[0,256])
        
        
        
        #out.write(temp_diff)
    #out.release()

    indices = np.array(list(range(len(motion_index))))
    indices = indices/fps
    plt.plot(indices,motion_index)
    plt.xlabel('Time/s')
    plt.ylabel('Motion_index')
    plt.title('Change in motion')
    plt.show()

    
    
    
    
