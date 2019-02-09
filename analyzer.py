# -*- coding: utf-8 -*-

import numpy as np
import ioutils
import properties
from measurement import PropertyKeys, PatientKeys, ParameterKeys
import models


class Analyzer(object):
    '''
    A class to analyze aspiration depth measurements.
    '''
    SCALE = 4.0
    
    def __init__(self, measurement):
        self.measurement = measurement
      
    def _prepare_property_extraction(self):
        """ Read in a video and pressure file and store information """
        if self.measurement.data[PatientKeys.CLINIC.value]=='TAIWAN':
            video_frames, time = ioutils.read_video_file(180)
        elif self.measurement.data[PatientKeys.CLINIC.value]=='CHINA':
            video_frames, time = ioutils.read_video_file(90)
        else:
            video_frames, time = ioutils.read_video_file()
        self.measurement.set_property(PropertyKeys.VIDEO_FRAMES, video_frames)
        self.measurement.set_property(PropertyKeys.TIME, [time])
    
        pressure = ioutils.read_pressure_file()
        self.measurement.set_property(PropertyKeys.APPLIED_PRESSURE, pressure)
        # Calculate the applied force
        # Formula: Force = Pressure * Area
        # Area = (d/2)^2 * pi
        # Psi to N/m^2 := 6894.76 N/m2/psi
        # um to m := 10**-6 m/um
        force = (pressure * 6894.76 * np.pi 
                         * (self.measurement._pipette_size/2.0*(10**-6))**2)
        self.measurement.set_property(PropertyKeys.APPLIED_FORCE, force)
        return (video_frames, time)
    
    def _extract_properties(self):
        (video_frames, time) = self._prepare_property_extraction()
#        video_frames = self.measurement.data[PropertyKeys.VIDEO_FRAMES.value]
        pipette_size = properties.PipetteSize(video_frames, self.SCALE)
        
        self.measurement.set_property(PropertyKeys.PIPETTE_SIZE_PIXEL, 
                                      pipette_size.extract_property())
        
        self.measurement.set_property(PropertyKeys.MANUAL_CONVERSION_FACTOR,
                self.measurement.data[
                        PropertyKeys.MANUAL_CONVERSION_FACTOR.value]
                /self.measurement._pipette_size)
        
        pipette_position = properties.PipettePosition(video_frames, self.SCALE)
        self.measurement.set_property(PropertyKeys.PIPETTE_TIP_POSITION,
                                      pipette_position.extract_property())
        
        zona_thickness = properties.ZonaThickness(video_frames, self.SCALE,
                                self.measurement._conversion_factor)
        self.measurement.set_property(PropertyKeys.ZONA_THICKNESS,
                                      zona_thickness.extract_property())
        
#        self.measurement.data[PropertyKeys.TIME.value]
        aspiration_depth = properties.AspirationDepth(video_frames, self.SCALE,
                                self.measurement.data[PropertyKeys.ZONA_THICKNESS.value],
                                self.measurement._conversion_factor, time)
        results = aspiration_depth.extract_property()
        zona_position, aspiration_depth_pixel, aspiration_depth_mechanical = results
        
        self.measurement.set_property(PropertyKeys.ZONA_POSITION, zona_position)
        self.measurement.set_property(PropertyKeys.ASPIRATION_DEPTH_ZONA_PIXEL,
                                      [aspiration_depth_pixel])
        self.measurement.set_property(PropertyKeys.ASPIRATION_DEPTH_ZONA_MECH,
                                      [aspiration_depth_mechanical])
    
    def _fit_models(self):
        time = self.measurement.data[PropertyKeys.TIME.value][0]
        aspiration_depth = self.measurement.data[
                PropertyKeys.ASPIRATION_DEPTH_ZONA_MECH.value][0]
        applied_force = self.measurement.data[PropertyKeys.APPLIED_FORCE.value]
        modified_zener = models.ModifiedZener(time, aspiration_depth, 
                                              applied_force, [], weighted=True)
        params = modified_zener.fit()
        for key, value in params.items():
            if ParameterKeys.has_value(key):
                self.measurement.set_model_parameter(ParameterKeys(key), value)
    
    def analyze(self):
        self._extract_properties()
        self._fit_models()
        return True
        


if __name__ == '__main__':
    print('Analyzer')