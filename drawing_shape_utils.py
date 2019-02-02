# -*- coding: utf-8 -*-

import cv2
from enum import Enum
import numpy as np

class Shape(Enum):
    arrow = 1
    line = 2
    zona = 3
    rectangle = 4
    offset = 5


class DrawingShapeUtils(object):
    LINE_THICKNESS = 3
    COLOR = (155, 155, 155)
    
    @staticmethod
    def _select_draw_function(shape):
        '''
        Selects the right function to draw the desired shape.
        
        shape   (enum)  The desired shape
        '''
        shapes = {
            Shape.arrow: DrawingShapeUtils._draw_arrow,
            Shape.line: DrawingShapeUtils._draw_line,
            Shape.zona: DrawingShapeUtils._draw_zona_position,
            Shape.rectangle: DrawingShapeUtils._draw_rectangle,
            Shape.offset: DrawingShapeUtils._draw_rectangle_with_offset}
        draw_function = shapes.get(shape)
        if draw_function:
            return draw_function
        else:
            raise ValueError('Selected shape ({}) is not available'.format(shape))
    
    @staticmethod
    def _draw_arrow(event,x,y,flags,params):
        '''
        Draw an arrow from the position where left mouse button is clicked to
        where left mouse button is released.
        
        event:      A mouse click event
        x:          x position of cursor
        y:          y position of cursor
        flags:      N/A
        params:     N/A
        '''
        global img, source_img, state
        global p1, p2
        if event == cv2.EVENT_LBUTTONDOWN:
            state = True
            p1 = (x,y)
            img = source_img.copy()
        elif event == cv2.EVENT_LBUTTONUP:
            state = False
            p2 = (x,y)
            img = source_img.copy()
            cv2.arrowedLine(img, p1, p2, DrawingShapeUtils.COLOR, 
                            DrawingShapeUtils.LINE_THICKNESS)
            cv2.arrowedLine(img, p2, p1, DrawingShapeUtils.COLOR, 
                            DrawingShapeUtils.LINE_THICKNESS)
        elif event == cv2.EVENT_MOUSEMOVE:
            if state:
                img = source_img.copy()
                cv2.arrowedLine(img, p1, (x,y), DrawingShapeUtils.COLOR, 
                                DrawingShapeUtils.LINE_THICKNESS)
                cv2.arrowedLine(img, (x,y), p1, DrawingShapeUtils.COLOR, 
                                DrawingShapeUtils.LINE_THICKNESS)
        
    @staticmethod        
    def _draw_line(event,x,y,flags,params):
        '''
        Draw a line at the position where the left mouse button is released.
                
        event:      A mouse click event
        x:          x position of cursor
        y:          y position of cursor
        flags:      N/A
        params:     N/A
        '''
        global img, source_img
        global p1, p2
        if event == cv2.EVENT_LBUTTONDOWN:
            img = source_img.copy()
            p1 = (x,y)
        elif event == cv2.EVENT_LBUTTONUP:
            p2 = (x,y)
            img = source_img.copy()
            text = 'position: %d' % p2[0]
            cv2.putText(img, text, (100,100), 
                        cv2.FONT_HERSHEY_SIMPLEX, 3, DrawingShapeUtils.COLOR, 
                        DrawingShapeUtils.LINE_THICKNESS)
            cv2.line(img, (x,y+100), (x,y-100), DrawingShapeUtils.COLOR, 
                     DrawingShapeUtils.LINE_THICKNESS)
    
    @staticmethod
    def _draw_zona_position(event,x,y,flags,params):
        '''
        Draw a vertical line at mouse position and a horizontal line 
        with the length of the zona thickness
        
        event:      A mouse click event
        x:          x position of cursor
        y:          y position of cursor
        flags:      N/A
        params:     zona thickness
        '''
        global img, source_img
        global p1, p2
        zp_thickness = params[0]
        if event == cv2.EVENT_LBUTTONDOWN:
            img = source_img.copy()
            p1 = (x,y)
        elif event == cv2.EVENT_LBUTTONUP:
            p2 = (x,y)
            img = source_img.copy()
            text = 'position: %d' % p2[0]
            cv2.putText(img, text, (100,100), 
                        cv2.FONT_HERSHEY_SIMPLEX, 3, DrawingShapeUtils.COLOR, 
                        DrawingShapeUtils.LINE_THICKNESS)
            cv2.line(img, (x,y+100), (x,y-100), DrawingShapeUtils.COLOR, 
                     DrawingShapeUtils.LINE_THICKNESS)
            cv2.line(img, (x,y), (x+zp_thickness,y), DrawingShapeUtils.COLOR, 
                     DrawingShapeUtils.LINE_THICKNESS)
    
    @staticmethod
    def _draw_rectangle(event,x,y,flags,params):
        '''
        Draw a rectangle on a mouse click event.
        
        INPUT
        --------------------------------------------------------------
        event:      A mouse click event
        x:          x position of cursor
        y:          y position of cursor
        flags:      N/A
        params:     desired width and height of the rectangle
        
        RETURN
        ---------------------------------------------------------------
        p1:         Coordinates of where left mouse button was clicked
        p2:         Coordinates of where left mouse button was released
        '''
        global img, source_img, state
        global p1, p2
        width, height = params
        if event == cv2.EVENT_LBUTTONDOWN:
            state = True
            img = source_img.copy()
            cv2.rectangle(img, (int(x-width/2),int(y-height/2)),
                          (int(x+width/2),int(y+height/2)), 
                          DrawingShapeUtils.COLOR, 
                          DrawingShapeUtils.LINE_THICKNESS)
            p1 = (x,y)
        elif event == cv2.EVENT_LBUTTONUP:
            state = False
            img = source_img.copy()
            cv2.rectangle(img, (int(x-width/2),int(y-height/2)),
                          (int(x+width/2),int(y+height/2)), 
                          DrawingShapeUtils.COLOR, 
                          DrawingShapeUtils.LINE_THICKNESS)
            p2 = (x,y)
        if event == cv2.EVENT_MOUSEMOVE:
            if state:
                img = source_img.copy()
                cv2.rectangle(img, (int(x-width/2),int(y-height/2)),
                              (int(x+width/2),int(y+height/2)), 
                              DrawingShapeUtils.COLOR, 
                              DrawingShapeUtils.LINE_THICKNESS)
               
    @staticmethod
    def _draw_rectangle_with_offset(event,x,y,flags,params):
        '''
        Draw a rectangle on a mouse click event.
        
        event:      A mouse click event
        x:          x position of cursor
        y:          y position of cursor
        flags:      Flags
        params:     desired width and height of the rectangle
        '''
        global img, source_img, state
        global p1, p2
        width, height = params
        if event == cv2.EVENT_LBUTTONDOWN:
            state = True
            img = source_img.copy()
            cv2.rectangle(img, (x,int(y-height/2)),(x+width,int(y+height/2)),
                          DrawingShapeUtils.COLOR, 
                          DrawingShapeUtils.LINE_THICKNESS)
            p1 = (x,y)
        elif event == cv2.EVENT_LBUTTONUP:
            state = False
            img = source_img.copy()
            cv2.rectangle(img, (x,int(y-height/2)),(x+width,int(y+height/2)), 
                          DrawingShapeUtils.COLOR, 
                          DrawingShapeUtils.LINE_THICKNESS)
            p2 = (x,y)
        if event == cv2.EVENT_MOUSEMOVE:
            if state:
                img = source_img.copy()
                cv2.rectangle(img, (x,int(y-height/2)),
                              (x+width,int(y+height/2)), 
                              DrawingShapeUtils.COLOR, 
                              DrawingShapeUtils.LINE_THICKNESS)
                
    @staticmethod
    def draw(pic, scale, prompt, shape, params):
        '''
        Display an image and draw the desired shape on mouse click.
        
        pic:        (array)     A grayscale image
        scale:      (float)     Scaling factor to enlarge image
        prompt:     (str)       Message to display with image
        shape:      (enum)      Desired shape
        params:     (list)      Additional parameters for drawing function
        '''
        global source_img, img, state
        global p1, p2
        
        state = False
        temp = cv2.resize(pic, (0,0), fx=scale, fy=scale)
        source_img = temp.copy()
        img = source_img.copy()
        draw_function = DrawingShapeUtils._select_draw_function(shape)
        cv2.namedWindow(prompt)
        cv2.moveWindow(prompt, 20, 20)
        cv2.setMouseCallback(prompt, draw_function, params)
        while True:
            cv2.imshow(prompt, img)
            key = 0xFF & cv2.waitKey(1)
            if key == 27: # escape key
                break
            elif key == 13: # enter key
                y1, y2 = p1, p2
                break
        cv2.destroyAllWindows()
        return y1, y2

if __name__ == '__main__':
    pic = np.ones((200,300), dtype=np.uint8)*255
    scale = 2.0
    prompt = 'Test image'
    shape = Shape.arrow
    params = []
    coord = DrawingShapeUtils.draw(pic, scale, prompt, shape, params)
    
    coord2 = DrawingShapeUtils.draw(pic, scale, prompt, 5, params)
        
