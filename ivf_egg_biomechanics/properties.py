# -*- coding: utf-8 -*-

import numpy as np
import pandas as pd
from skimage.exposure import equalize_hist
from skimage.filters import gaussian
from utils.drawing_shape_utils import DrawingShapeUtils, Shape


class Property(object):
    """
    Extract different properties from an aspiration depth measurement.
    
    The property class is a parent class that represents different properties of an
    aspiration depth measurement.
    Every child class implements an extract_property method that extracts the property.
    """
    def __init__(self, video_frames, scale):
        """
        Initializes the instance of the class.
        
        Args:
            video_frames (list):    list of grayscale images
            scale (float):          scaling factor by which images are enlarged
        """
        if not isinstance(video_frames, list):
            raise TypeError('Expected {}, but got {}'.format(list, type(video_frames)))
        if not isinstance(scale, float):
            raise TypeError('Expected {}, but got {}'.format(float, type(scale)))
        self.video_frames = video_frames
        self.scale = scale
        

class PipetteSize(Property):
    """
    A class used to analyze the pipette size in pixels manually.
    The user gets prompted with an enlarged image of the pipette tip and
    has to draw an arrow between the inner edges of the pipette.
    """
    def extract_property(self):
        """
        Asks the user to draw an arrow between the edges of the pipette.
        Calculates the vertical distance between the edges in pixels.
        """
        pic = self.video_frames[0]
        prompt = 'Select inner edges of pipette'
        point_1, point_2 = DrawingShapeUtils.draw(pic, self.scale, prompt, Shape.arrow, [])
        return self._calculate_pipette_size(point_1, point_2)
    
    def _calculate_pipette_size(self, point_1, point_2):
        return np.abs(point_2[1]-point_1[1])/self.scale
    
    
class PipettePosition(Property):
    """
    A class to get the position of the pipette tip in the image.
    """
    def extract_property(self):
        """
        Asks the user to select the position of the pipette tip.
        """
        pic = self.video_frames[0]
        prompt = 'Click on pipette tip'
        point_1, point_2 = DrawingShapeUtils.draw(pic, self.scale, prompt, Shape.line, [])
        return self._calculate_pipette_position(point_2)
    
    def _calculate_pipette_position(self, point_2):
        return point_2[0]/self.scale


class ZonaThickness(Property):
    """
    A class to analyze the zona thickness of an oocyte.
    """
    WIDTH_ROI = 100
    HEIGHT_ROI = 100
    
    def __init__(self, video_frames, scale, conversion_factor):
        """
        Initializes the class. For information on video_frames, roi_coord and
        scale see documentation of Procedure class.
        
        conversion_factor (float):   conversion factor [um/pixel] 
        """
        super(ZonaThickness, self).__init__(video_frames, scale)
        self.conversion_factor = conversion_factor
    
    def extract_property(self):
        """
        Asks the user to draw an arrow between outer and
        inner diamter of the zona pellucida.
        """
        pic = self.video_frames[0]
        pic_roi = (equalize_hist(pic)*255).astype(np.uint8)
        prompt = 'Select zona pellucida'
        point_1, point_2 = DrawingShapeUtils.draw(
                pic_roi, self.scale, prompt, Shape.arrow, [])
        return self._calculate_zona_thickness(point_1, point_2)
    
    def _calculate_zona_thickness(self, point_1, point_2):
        zona_thickness = (
                np.sqrt((point_2[0]-point_1[0])**2+(point_2[1]-point_1[1])**2)
                / self.conversion_factor/self.scale)
        return zona_thickness
        

class AspirationDepth(Property):
    """
    A class to analyze the aspiration depth of zona pellucida and oolemma
    from video frames.
    """
    WIDTH_ROI = 80
    HEIGHT_ROI = 60
    
    def __init__(self, video_frames, scale, zona_thickness, 
                 conversion_factor, time, manual=False):
        """
        Initializes the class. For information on video_frames, roi_coord and
        scale see documentation of Property class.
        
        zona_thickness (float):         thickness of the zona pellucida
        conversion_factor (float):      conversion factor [um/pixels]
        time (float):                   array with time stamps
        """
        super(AspirationDepth, self).__init__(video_frames, scale)
        self.zona_thickness = zona_thickness
        self.conversion_factor = conversion_factor
        self.time = time
        self.manual = manual
    
    def extract_property(self):
        """
        Loads the video frames from the first movement and asks the user 
        to click on the zona/oolemma in each frame to track its movement.
        """ 
        prompt = 'Click on inner diameter of zona pellucida'
        zp_thickness = int(round(self.zona_thickness
                                 * self.conversion_factor
                                 * self.scale))
        pic  = self.video_frames[0]
        point_1, point_2 = DrawingShapeUtils.draw(
                pic, self.scale, prompt, Shape.zona, [zp_thickness])
        
        offset = int((point_2[0] / self.scale + self.zona_thickness * self.conversion_factor))
        
        if not self.manual:
            prompt = 'Select inner pipette region for automated ZP tracking: '
            point_1, point_2 = DrawingShapeUtils.draw(pic, 1.0, prompt, Shape.offset,
                                                      [AspirationDepth.WIDTH_ROI, AspirationDepth.HEIGHT_ROI])
            
            off_x, off_y = point_2
            off_x = off_x+AspirationDepth.WIDTH_ROI/2
            background = pic[int(off_y-AspirationDepth.HEIGHT_ROI/2):int(off_y+AspirationDepth.HEIGHT_ROI/2),
                             int(off_x-AspirationDepth.WIDTH_ROI/2):int(off_x+AspirationDepth.WIDTH_ROI/2)].copy()
            background = background.astype(np.uint8)
            background = (gaussian(background, sigma=2.0)*255).astype(np.int16)
    
            subtracted_imgs = []
            
            for i, img in enumerate(self.video_frames[1:]):
                roi = img.copy()
                next_frame_cropped = roi[int(off_y-AspirationDepth.HEIGHT_ROI/2):
                                         int(off_y+AspirationDepth.HEIGHT_ROI/2),
                                         int(off_x-AspirationDepth.WIDTH_ROI/2):
                                         int(off_x+AspirationDepth.WIDTH_ROI/2)].copy()
                next_frame_filtered = (gaussian(next_frame_cropped, sigma=2.0)*255).astype(np.int16)
                subtracted_img = np.abs((next_frame_filtered-background))
                subtracted_imgs.append(subtracted_img.astype(np.uint8))
            
            subtracted_imgs = [np.sum(sub, axis=0) for sub in subtracted_imgs]
            dsubtracted_imgs = pd.DataFrame(subtracted_imgs)
            mov = dsubtracted_imgs.rolling(window=10, center=True, axis=1)
            mean_subtracted_imgs = mov.mean()
            derivative_subtracted_imgs = (mean_subtracted_imgs.iloc[:, 1:].values
                                          - mean_subtracted_imgs.iloc[:, :-1].values)
            derivative_subtracted_imgs = np.nan_to_num(derivative_subtracted_imgs)
            position_zona = []
            for i in range(len(derivative_subtracted_imgs)):
                position_zona.append(np.argmin(derivative_subtracted_imgs[i, :]))
    
            position_zona = np.asarray(position_zona, dtype=np.uint8)
            position_zona += int(off_x-AspirationDepth.WIDTH_ROI/2)
                     
            aspiration_depth_auto_pixel = np.asarray(position_zona)
            aspiration_depth_auto_mechanical = ((aspiration_depth_auto_pixel-offset) * 1e-6 / self.conversion_factor)
            return (offset, aspiration_depth_auto_pixel, aspiration_depth_auto_mechanical)
        
        else:
            prompt = 'Click on zona pellucida'
            aspiration_depth = np.repeat(-1,len(self.time))
            
            for i, im in enumerate(self.video_frames[1:]):
                pic = im.copy()
                point_1, point_2 = DrawingShapeUtils.draw(
                        pic, self.scale, prompt, Shape.line, [])
                aspiration_depth[i] = point_2[0]

            aspiration_depth_manual_pixel = (np.asarray(aspiration_depth)/self.scale)
            aspiration_depth_manual_mechanic = ((aspiration_depth_manual_pixel-offset) * 1e-6 / self.conversion_factor)
            return offset, aspiration_depth_manual_pixel, aspiration_depth_manual_mechanic


if __name__ == '__main__':
    video_frames = list(np.ones((5, 200, 200), dtype=np.uint8)*100)
    scale = 4.0
    prop = PipetteSize(video_frames[0], scale)
    coord = prop.extract_property()
    print(coord)
    
    prop1 = ZonaThickness(video_frames[0], scale, 1.0)
    coord1 = prop1.extract_property()
    print(coord1)
    
    prop2 = AspirationDepth(video_frames, scale, 20.0, 1.0, np.asarray([0.0, 0.1, 0.2, 0.3]))
    coord2 = prop2.extract_property()
    print(coord2)
