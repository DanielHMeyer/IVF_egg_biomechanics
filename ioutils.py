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
    """
    Load data from an excel file.
    
    Returns:
        data (dataframe):   A dataframe using the first line of the excel file
                            as column names.
    """
    filename = choose_file('.xlsx')
    if filename.endswith('.xlsx'):
        data = _extract_data_from_file(filename)
    else:
        print('{} is not an excel file.'.format(filename))
        data = pd.DataFrame()
    return data

def _extract_data_from_file(filename):
    """ 
    Extract data from a given file.
    
    Args:
        filename (str): full path to file
        
    Returns:
        data (dataframe): a dataframe with the data
    """
    data = pd.read_excel(filename)
    data.replace(np.nan, 0, inplace=True)
    data.columns = map(str.upper, data.columns)
    return data


def read_video_file(rot_angle=0):
    """
    Ask the user to choose the corresponding video file for the measurement
    and if the video has to be rotated.
    Read in the video frames and ask the user to specify the frame number
    before the first movement of the oocyte.
    
    Args:
        rot_angle (int): angle to rotate the video frames
    
    Returns:
        video_frames (list):    list of arrays corresponding to the grayscale video frames
        time (list):            list of time points
    """
    full_path = choose_file('.avi')
    path = str(os.path.dirname(full_path))
    filename = str(os.path.basename(full_path))
    os.chdir(path)
    frames = []
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
    time_valve_opened = _find_starting_point_of_movement(frames)
    time = _create_time_vector(num_frames, time_valve_opened, frame_rate)
    video_frames = frames[time_valve_opened:time_valve_opened+len(time)+1]
    video_frames_cropped = _crop_video_frames(video_frames)
    return (video_frames_cropped, time)
    
def choose_file(extension):
    """
    Ask user to choose a file with the correct extension.
    
    Args:
        extension (str): the desired file extension with a preceeding dot (e.g.: .xlsx)
    Returns:
        filename (str): full path of file
    """
    Tk().withdraw()
    filetype = '*' + extension
    filename = askopenfilename(initialdir = "/",
                    title = "Select a file with {} extension".format(extension),
                    filetypes = (("{} files".format(extension),filetype),
                                  ("all files","*.*")))
    return filename

def _find_starting_point_of_movement(frames):
    """
    Find the frame before the oocyte moves.
    
    Displays a frame and lets the user search for the frame number before the
    movement of the oocyte begins. The user has to input the frame number before
    movement starts.
    
    Args:
        frames (list): a list of video frames
    
    Returns:
        time_valve_opened (int): the frame number before the movement begins
    """
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
    return time_valve_opened

def _create_time_vector(num_frames, time_valve_opened, frame_rate):
    """
    Create a time vector for a measurement.
    
    Args:
        num_frames (int):           total number of frames
        time_valve_opened (int):    frame before movement starts
        frame_rate (int):           frame rate of the video [fps]
    Returns:
        time (list):    a list with time points
    """
    max_time = (num_frames - time_valve_opened)/float(frame_rate) - 0.03
    crop_value = 0.5
    if crop_value <= max_time:
        time = np.linspace(0.0,crop_value,num=int(frame_rate*crop_value),
                           endpoint=False)
        time = np.reshape(time, (len(time),1))
        time = time[:,0]
    else:
        time = np.linspace(0.0,max_time,num=int(frame_rate*max_time), 
                           endpoint=False)
        time = np.reshape(time, (len(time),1))
        time = time[:,0]
    return time

def _crop_video_frames(video_frames):
    start_image = video_frames[0]
    roi_width = 200
    roi_height = 200
    x, y = _choose_roi(start_image, roi_width, roi_height)
    video_frames_cropped = []
    for frame in video_frames:
        video_frames_cropped.append(
                frame[int(y-roi_height/2):int(y+roi_height/2),
                      int(x-roi_width/2):int(x+roi_width/2)])
    return video_frames_cropped

def _choose_roi(pic, roi_width, roi_height):
    """
    Select an region of interest in an image
    
    Args:
        pic (array):        an array with grayscale values of an image
        roi_width (int):    the desired width of the roi
        roi_height (int):   the desired height of the roi
    Returns:
        (tuple):            top left corner coordinates
    """
    
    prompt = 'Select ROI'
    point_1, point_2 = dsu.DrawingShapeUtils.draw(
            pic, 1.0, prompt, dsu.Shape.rectangle, [roi_width, roi_height])
    return (point_2[0], point_2[1])

def read_pressure_file():
    """
    Read the pressure log file and return the mean of the applied pressure.
    
    ReturnsS:
        appliedPressure (float):     applied pressure in [psi]
    """
    full_path = choose_file('.txt')
    path = str(os.path.dirname(full_path))
    filename = str(os.path.basename(full_path))
    os.chdir(path)
    pressRead = np.genfromtxt(filename, delimiter=' ', dtype=str)
    ind = np.ravel(np.where(pressRead[:,1]=='Valve'))
    pressRead = pressRead[ind[0]+1:,1]
    pressRead = pressRead.astype(np.float)
    appliedPressure = np.mean(pressRead)
    return appliedPressure
  
if __name__ == '__main__':
    data = load_excel_file()
    video_frames, time = read_video_file(180)
    pressure = read_pressure_file()