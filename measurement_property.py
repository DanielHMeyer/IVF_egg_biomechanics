# -*- coding: utf-8 -*-

#import cv2
import numpy as np
import pandas as pd
from skimage.exposure import equalize_hist
from skimage.filters import gaussian
from drawing_shape_utils import DrawingShapeUtils, Shape
#from enum_utils import Shape


class Property(object):
    '''
    A parent class that represents different properties of an
    aspiration depth measurement.
    '''
    def __init__(self, video_frames, roi_coord, scale):
        '''
        Initializes the instance.
        video_frames     (list)     list of grayscale images
        roi_coord        (list)     x position, y position, width and height of roi
        scale:           (float)    scaling factor by which images are enlarged
        '''
        self.video_frames = video_frames
        self.roi_coord = roi_coord
        self.scale = scale
        

class PipetteSize(Property):
    '''
    A class used to analyze the pipette size in pixels manually.
    The user gets prompted with an enlarged image of the pipette tip and
    has to draw an arrow between the inner edges of the pipette.
    '''
    
    def get_property(self):
        '''
        Asks the user to draw an arrow between the edges of the pipette.
        Calculates the vertical distance between the edges in pixels.
        '''
        cx, cy, w, h = self.roi_coord
        pic = self.video_frames[0][cy-int(h/2):cy+int(h/2),
                                cx-int(w/2):cx+int(w/2)]
        prompt = 'Select inner edges of pipette'
        resize = True
        point_1, point_2 = DrawingShapeUtils.draw(pic, self.scale, prompt,
                                                     Shape.arrow, [], resize)
        return self._calculate_pipette_size(point_1,point_2)
    
    def _calculate_pipette_size(self, point_1, point_2):
        return np.abs(point_2[1]-point_1[1])/self.scale
    
    
class PipettePosition(Property):
    '''
    A class to get the position of the pipette tip in the image.
    '''
    
    def get_property(self):
        '''
        Asks the user to select the position of the pipette tip.
        '''
        cx, cy, w, h = self.roi_coord
        pic = self.video_frames[0][cy-int(h/2):cy+int(h/2),
                                cx-int(w/2):cx+int(w/2)]
        prompt = 'Click on pipette tip'
        resize = True
        point_1, point_2 = DrawingShapeUtils.draw(pic, self.scale, prompt, 
                                                     Shape.line, [], resize)
        return self._calculate_pipette_position(point_2)
    
    def _calculate_pipette_position(self, point_2):
        return point_2[0]/self.scale


class ZonaThickness(Property):
    '''
    A class to analyze the zona thickness of an oocyte.
    '''
    def __init__(self, video_frames, roi_coord, scale, conversion_factor):
        '''
        Initializes the class. For information on video_frames, roi_coord and
        scale see documentation of Procedure class.
        
        conversion_factor:     (float)    conversion factor [um/pixel] 
        '''
        super(ZonaThickness, self).__init__(video_frames, roi_coord, scale)
        self.conversion_factor = conversion_factor
    
    
    def get_property(self):
        '''
        Asks the user to draw an arrow between outer and
        inner diamter of the zona pellucida.
        '''
        pic = self.video_frames[0]
        resize = False
        w_roi, h_roi = 100, 100
        prompt = 'Select ROI for ZP thickness measurement'
        point_1, point_2 = DrawingShapeUtils.draw(
                pic, self.scale, prompt, Shape.rectangle,
                [w_roi, h_roi], resize)
        cx, cy = point_2
        pic_roi = pic[int(cy-h_roi/2):int(cy+h_roi/2), 
                      int(cx-w_roi/2):int(cx+w_roi/2)].copy()
        pic_roi = (equalize_hist(pic_roi)*255).astype(np.uint8)
        resize = True
        prompt = 'Select zona pellucida'
        point_1, point_2 = DrawingShapeUtils.draw(
                pic_roi, self.scale, prompt, Shape.arrow, [], resize)
        return self._calculate_zona_thickness(point_1, point_2)
    
    def _calculate_zona_thickness(self, point_1, point_2):
        zona_thickness = (
                np.sqrt((point_2[0]-point_1[0])**2+(point_2[1]-point_1[1])**2)
                / self.conversion_factor/self.scale)
        return zona_thickness
        

class AspirationDepth(Property):
    '''
    A class to analyze the aspiration depth of zona pellucida and oolemma
    from video frames.
    '''
    def __init__(self, video_frames, roi_coord, scale, zona_thickness, 
                 conversion_factor, time):
        '''
        Initializes the class. For information on video_frames, roi_coord and
        scale see documentation of Procedure class.
        
        zona_thickness:      (float)     thickness of the zona pellucida
        conversion_factor:   (float)     conversion factor [um/pixels]
        time:               (float)     array with time stamps
        '''
        super(AspirationDepth, self).__init__(video_frames, roi_coord, scale)
        self.zona_thickness = zona_thickness
        self.conversion_factor = conversion_factor
        self.time = time
    
    def get_property(self, manual=False):
        '''
        Loads the video frames from the first movement and asks the user 
        to click on the zona/oolemma in each frame to track its movement.
        '''
        
        aspiration_depth = np.repeat(-1,len(self.time))
        cx, cy, w, h = self.roi_coord
        prompt = 'Click on inner diameter of zona pellucida'
        resize = True
        zp_thickness = int(round(self.zona_thickness
                                 * self.conversion_factor
                                 * self.scale))
        pic  = self.video_frames[0][int(cy-h/2):int(cy+h/2),
                                    int(cx-w/2):int(cx+w/2)].copy()
        point_1, point_2 = DrawingShapeUtils.draw(
                pic, self.scale, prompt, Shape.zona, [zp_thickness], resize)
        
        aspiration_depth[0] = (point_2[0] / self.scale 
                                + self.zona_thickness * self.conversion_factor)
        offset = aspiration_depth[0]
        
        w_roi, h_roi = 80,60
        prompt = 'Select inner pipette region for automated ZP tracking: '
        resize = False
        point_1, point_2 = DrawingShapeUtils.draw(
                pic, self.scale, prompt, Shape.offset, [w_roi, h_roi], resize)
        
        off_x, off_y = point_2
        off_x = off_x+w_roi/2
        background = pic[int(off_y-h_roi/2):int(off_y+h_roi/2), 
                             int(off_x-w_roi/2):int(off_x+w_roi/2)].copy()
        background = background.astype(np.uint8)
        background = (gaussian(background, sigma=2.0)*255).astype(np.int16)

        subtracted_imgs = []
        
        for i,img in enumerate(self.video_frames[1:]):
            roi = img[int(cy-h/2):int(cy+h/2),int(cx-w/2):int(cx+w/2)].copy()
            next_frame_cropped = roi[int(off_y-h_roi/2):int(off_y+h_roi/2), 
                                     int(off_x-w_roi/2):int(off_x+w_roi/2)].copy()
            next_frame_filtered = (gaussian(next_frame_cropped, 
                                            sigma=2.0)*255).astype(np.int16)
            subtracted_img = np.abs((next_frame_filtered-background))
            subtracted_imgs.append(subtracted_img.astype(np.uint8))
            
        subtracted_imgs = [np.sum(sub, axis=0) for sub in subtracted_imgs]
        dsubtracted_imgs = pd.DataFrame(subtracted_imgs)
        mov = dsubtracted_imgs.rolling(window=10, center=True, axis=1)
        mean_subtracted_imgs = mov.mean()
        derivative_subtracted_imgs = (mean_subtracted_imgs.iloc[:,1:].values
                                      - mean_subtracted_imgs.iloc[:,:-1].values)
        derivative_subtracted_imgs = np.nan_to_num(derivative_subtracted_imgs)
        position_zona = []
        for i in range(len(derivative_subtracted_imgs)):
                position_zona.append(np.argmin(derivative_subtracted_imgs[i,:]))

        position_zona = np.asarray(position_zona, dtype=np.uint8)
        position_zona += int(off_x-w_roi/2)
        aspiration_depth[1:] = position_zona
                 
        aspiration_depth_auto_pixel = np.asarray(aspiration_depth)
        aspiration_depth_auto_mechanical = ((aspiration_depth_auto_pixel-offset) 
                                            * (1e-6) / self.conversion_factor)
        
        if manual:
            prompt = 'Click on zona pellucida'
            aspiration_depth = np.repeat(-1,len(self.time))
            resize = True
            
            for i, im in enumerate(self.video_frames[1:]):
                pic = im[int(cy-h/2):int(cy+h/2),
                         int(cx-w/2):int(cx+w/2)].copy()
                point_1, point_2 = DrawingShapeUtils.draw(
                        pic, self.scale, prompt, Shape.line, [], resize)
                aspiration_depth[i] = point_2[0]

            aspiration_depth_manual_pixel = (
                    np.asarray(aspiration_depth)/self.scale)
            aspiration_depth_manual_mechanic = (
                    (aspiration_depth_manual_pixel-offset) 
                    * (1e-6) / self.conversion_factor)
            return (offset, aspiration_depth_auto_pixel, 
                    aspiration_depth_auto_mechanical,
                    aspiration_depth_manual_pixel, 
                    aspiration_depth_manual_mechanic)
        else:
            return (offset, aspiration_depth_auto_pixel, 
                    aspiration_depth_auto_mechanical)





if __name__ == '__main__':
    video_frames = list(np.ones((5,448,600), dtype=np.uint8)*100)
    roi_coord = [250, 220, 200, 200]
    scale = 4.0
    prop = PipetteSize(video_frames, roi_coord, scale)
    coord = prop.get_property()
    print(coord)
    
    prop1 = ZonaThickness(video_frames,roi_coord,scale,1.0)
    coord1 = prop1.get_property()
    print(coord1)
    
    prop2 = AspirationDepth(video_frames,roi_coord,scale,20.0,1.0, [0.0,0.1,0.2,0.3,0.4])
    coord2 = prop2.get_property()
    print(coord2)
    