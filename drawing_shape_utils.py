# -*- coding: utf-8 -*-

import cv2

#rename class
class DrawingShapeUtils(object):
    LINE_THICKNESS = 3
    
    #TODO(dani): add comment
    @staticmethod
    def _draw(event,x,y,flags,params):
        shape = params[0]
        shapes = {
            'arrow': DrawingShapeUtils._draw_arrow,
            'line': DrawingShapeUtils._draw_line,
            'zona': DrawingShapeUtils._draw_zona_position,
            'rectangle': DrawingShapeUtils._draw_rectangle,
            'offset': DrawingShapeUtils._draw_rectangle_with_offset}
        draw_shape = shapes.get(shape)
        if draw_shape:
            draw_shape(event,x,y,flags,params)
    
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
            #TODO: change 0,255,0 to COLOR_BLUE or whatever it is
            # TODO: Look for autoformat in Spyder to have always same amount of spacing
            cv2.arrowedLine(img, p1,p2, (0,255,0), DrawingShapeUtils.LINE_THICKNESS)
            cv2.arrowedLine(img, p2,p1, (0,255,0), DrawingShapeUtils.LINE_THICKNESS)
        elif event == cv2.EVENT_MOUSEMOVE:
            if state:
                img = source_img.copy()
                cv2.arrowedLine(img, p1,(x,y), (0,255,0), DrawingShapeUtils.LINE_THICKNESS)
                cv2.arrowedLine(img, (x,y),p1, (0,255,0), DrawingShapeUtils.LINE_THICKNESS)
        
    @staticmethod        
    def _draw_line(event,x,y,flags,params):
        '''
        Draw a line at the position where the left mouse button is released.
        '''
        #TODO more comments here and elsewhere, describe the variables
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
                        cv2.FONT_HERSHEY_SIMPLEX, 3, (0,0,0), 3)
            cv2.line(img,(x,y+100),(x,y-100), (0,255,0), 3)
    
    @staticmethod
    def _draw_zona_position(event,x,y,flags,params):
        '''
        Draw a vertical line at mouse position and a horizontal line 
        with the length of the zona thickness
        '''
        global img, source_img
        global p1, p2
        zp_thickness = params[-1]
        if event == cv2.EVENT_LBUTTONDOWN:
            img = source_img.copy()
            p1 = (x,y)
        elif event == cv2.EVENT_LBUTTONUP:
            p2 = (x,y)
            img = source_img.copy()
            text = 'position: %d' % p2[0]
            cv2.putText(img, text, (100,100), 
                        cv2.FONT_HERSHEY_SIMPLEX, 3, (0,0,0), 3)
            cv2.line(img,(x,y+100),(x,y-100), (0,255,0), 3)
            cv2.line(img,(x,y),(x+zp_thickness,y), (0,255,0), 3)
    
    @staticmethod
    def _draw_rectangle(event,x,y,flags,params):
        '''
        Draw a rectangle on a mouse click event.
        
        event:      A mouse click event
        x:          x position of cursor
        y:          y position of cursor
        flags:      N/A
        params:     desired width and height of the rectangle
        '''
        global img, source_img, state
        global p1, p2
        width, height = params[1:]
        if event == cv2.EVENT_LBUTTONDOWN:
            state = True
            img = source_img.copy()
            cv2.rectangle(img,(int(x-width/2),int(y-height/2)),
                          (int(x+width/2),int(y+height/2)), (0,255,0), 3)
            p1 = (x,y)
        elif event == cv2.EVENT_LBUTTONUP:
            state = False
            img = source_img.copy()
            cv2.rectangle(img,(int(x-width/2),int(y-height/2)),
                          (int(x+width/2),int(y+height/2)), (0,255,0), 3)
            p2 = (x,y)
        if event == cv2.EVENT_MOUSEMOVE:
            if state:
                img = source_img.copy()
                cv2.rectangle(img,(int(x-width/2),int(y-height/2)),
                              (int(x+width/2),int(y+height/2)), (0,255,0), 3)
               
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
        width, height = params[1:]
        if event == cv2.EVENT_LBUTTONDOWN:
            state = True
            img = source_img.copy()
            cv2.rectangle(img,(x,int(y-height/2)),(x+width,int(y+height/2)),
                          (0,255,0), 3)
            p1 = (x,y)
        elif event == cv2.EVENT_LBUTTONUP:
            state = False
            img = source_img.copy()
            cv2.rectangle(img,(x,int(y-height/2)),(x+width,int(y+height/2)), 
                          (0,255,0), 3)
            p2 = (x,y)
        if event == cv2.EVENT_MOUSEMOVE:
            if state:
                img = source_img.copy()
                cv2.rectangle(img,(x,int(y-height/2)),
                              (x+width,int(y+height/2)), (0,255,0), 3)
                
    @staticmethod
    def capture_mouse_click(pic, scale, prompt, params, resize):
        global source_img, img, state
        global p1, p2
        
        state = False
        if resize:
            temp = cv2.resize(pic, (0,0), fx=scale,fy=scale)
        else:
            temp = pic.copy()
        source_img = temp.copy()
        img = source_img.copy()
        cv2.namedWindow(prompt)
        #TODO: make 20a constants
        cv2.moveWindow(prompt, 20, 20)
        cv2.setMouseCallback(prompt, DrawingShapeUtils._draw, params)
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