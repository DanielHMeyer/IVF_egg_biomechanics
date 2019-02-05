# -*- coding: utf-8 -*-

import os
import cv2
import imutils
import numpy as np
import drawing_shape_utils as dsu
from tkinter import Tk
from tkinter.filedialog import askopenfilename
import pandas as pd

def load_excel_file():
    '''
    Load data from an excel file
    
    return:
        data (dataframe):    A dataframe containing the excel header as column names
    '''
    Tk().withdraw()
    filename = askopenfilename(initialdir = "/",
                    title = "Select an excel file",
                    filetypes = (("excel files","*.xlsx"),("all files","*.*")))
    if filename.endswith('.xlsx'):
        data = pd.read_excel(filename)
        data.replace(np.nan, 0, inplace=True)
    else:
        print('{} is not an excel file.'.format(filename))
    return data

def read_video():
    '''
    Ask the user to choose the corresponding video file for the measurement
    and if the video has to be rotated.
    Read in the video frames and ask the user to specify the frame number
    before the first movement of the oocyte.
    
    return:
        video_frames (list):    list of arrays corresponding to the grayscale video frames
        time (array):           time vector
    '''
    Tk().withdraw()
    fullPath = askopenfilename()
    path = str(os.path.dirname(fullPath))
    filename = str(os.path.basename(fullPath))
    os.chdir(path)
    frames = []
    rot_angle = int(input('Enter an angle to rotate video (+ == clockwise): '))
    video = cv2.VideoCapture(filename)
    frame_rate = video.get(cv2.CAP_PROP_FPS)
    num_frames = 0
    cv2.namedWindow('Aspiration Depth Video')
    cv2.moveWindow('Aspiration Depth Video', 20, 20)
    while(video.isOpened()):
        ret, frame = video.read()
        if not ret:
            break
        gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        rot_frame = imutils.rotate_bound(gray_frame, rot_angle)
        cv2.imshow('Aspiration Depth Video',rot_frame)
        frames.append(rot_frame)
        num_frames += 1
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    video.release()
    cv2.destroyAllWindows()
    
    fr = 0
    while True:
        num_frame = 'Frame: %d' % fr
        frame = frames[fr]
        cv2.putText(frame, num_frame, (5,30), cv2.FONT_HERSHEY_SIMPLEX,
                    1, (0,0,0))
        prompt = 'Look for frame number before movement starts.'
        cv2.namedWindow(prompt)
        cv2.imshow(prompt, frames[fr])
        cv2.moveWindow(prompt, 20, 20)
        key = cv2.waitKey(1) & 0xFF
        if key == 46: # if period button is pressed, show next frame
            fr += 1
        elif key == 44: # if comma button is pressed, show previous frame
            fr -= 1
        elif (key == 27)|(key == 13): # if Esc is pressed, break from the loop
            break
    cv2.destroyAllWindows()
    
    time_valve_opened = int(input('Enter the frame number before first movement: '))
    
    max_time = (num_frames - time_valve_opened)/float(frame_rate) - 0.03
    crop_value = 0.5
    if crop_value <= max_time:
        time = np.linspace(0.0,crop_value,num=int(frame_rate*crop_value),endpoint=False)
        time = np.reshape(time, (len(time),1))
        time = time[:,0]
    else:
        time = np.linspace(0.0,max_time,num=int(frame_rate*max_time), endpoint=False)
        time = np.reshape(time, (len(time),0))
        time = time[:,0]
    video_frames = frames[time_valve_opened:time_valve_opened+len(time)]
    start_image = video_frames[0]
    x, y, roi_w, roi_h = _choose_roi(start_image, 200, 200)
    video_frames = video_frames[:][int(y-roi_w/2):int(y+roi_h/2),
                          int(x-roi_w/2):int(x+roi_h/2)]
    return (start_image, video_frames, time)

def _choose_roi(pic, roi_width, roi_height):
    '''
    Select an region of interest in an image
    
    args:
        pic (array):        an array with grayscale values of an image
        roi_width (int):    the desired width of the roi
        roi_height (int):   the desired height of the roi
    return:
        (tuple):            top left corner coordinates, width and height of the roi
    '''
    
    prompt = 'Select ROI'
    point_1, point_2 = dsu.DrawingShapeUtils.draw(
            pic, 1.0, prompt, dsu.Shape.rectangle, [roi_width, roi_height])
    return (point_2[0], point_2[1], roi_width, roi_height)

def read_pressure():
    '''
    Read the pressure log file and return the mean of the applied pressure.
    
    return:
        appliedPressure (float):     applied pressure in [psi]
    '''
    Tk().withdraw()
    fullPath = askopenfilename()
    path = str(os.path.dirname(fullPath))
    filename = str(os.path.basename(fullPath))
    os.chdir(path)
    pressRead = np.genfromtxt(filename, delimiter=' ', dtype=str)
    ind = np.ravel(np.where(pressRead[:,1]=='Valve'))
    pressRead = pressRead[ind[0]+1:,1]
    pressRead = pressRead.astype(np.float)
    appliedPressure = np.mean(pressRead)
    return appliedPressure
  
if __name__ == '__main__':
    video_frames, time = read_video()
    pressure = read_pressure()