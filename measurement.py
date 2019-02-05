# -*- coding: utf-8 -*-

from enum import Enum

class MeasurementKeys(Enum):
    PATIENT_NUMBER = 'NUMBER'
    PATIENT_AGE = 'AGE'
    MATURE_OOCYTES = 'MII'
    CLINIC = 'CLINIC'
    OOCYTE_NUMBER = 'OOCYTE'
    POSITION = 'POSITION'
    FERTILIZED = 'FERTILIZED'
    DEGENERATED = 'DEGENERATED'
    NONFERT = 'NONFERT'
    ABNORMALFERT = 'ABNORMALFERT'
    D3_GRADE = 'D3GRADE'
    D3_VERY_GOOD = 'D3VERYGOOD'
    D3_VERY_BAD = 'D3VERYBAD'
    D3_GOOD = 'D3GOOD'
    D3_FAIR = 'D3FAIR'
    D3_POOR = 'D3POOR'
    ANY_BLAST = 'ANYBLAST'
    GOOD_BLAST = 'GOODBLAST'
    POOR_BLAST = 'POORBLAST'
    NO_BLAST = 'NOBLAST'
    BLAST_GRADE = 'BLASTGRADE'
    VIDEO_FRAMES = 'VIDEO_FRAMES'
    APPLIED_PRESSURE = 'APPLIED_PRESSURE'
    APPLIED_FORCE = 'APPLIED_FORCE'
    ROI_COORD = 'ROI_COORD'
    PIPETTE_SIZE_PIXEL = 'PIPETTE_SIZE_PIXEL'
    MANUAL_CONVERSION_FACTOR = 'MANUAL_CONVERSION_FACTOR'
    ZONA_THICKNESS = 'ZONA_THICKNESS'
    PERIVITELLINE_SPACE = 'PERIVITELLINE_SPACE'
    ZONA_POSITION = 'ZONA_POSITION'
    TIME = 'TIME'
    ASPIRATION_DEPTH_ZONA_PIXEL = 'ASPIRATION_DEPTH_ZONA_PIXEL'
    ASPIRATION_DEPTH_ZONA_MECH = 'ASPIRATION_DEPTH_ZONA_MECH'
    PIPETTE_TIP_POSITION = 'PIPETTE_TIP_POSITION'
    K0_ZP = 'K0_ZP'
    K1_ZP = 'K1_ZP'
    TAU_ZP = 'TAU_ZP'
    ETA0_ZP = 'ETA0_ZP'
    ETA1_ZP = 'ETA1_ZP'

class Measurement:
    ''' A container class to store data from aspiration depth measurements '''
    
    _conversion_factor = 1.55       # Conversion factor for pixels to micrometers: 155 pixels per 100 microns
    _pipette_size = 50.0            # pipette diameter [um]
    
    def __init__(self, patient_number, patient_age, mature_oocytes, clinic, oocyte_number,
                 measurement_number, position, outcomes={}):
        '''
        Initialize an instance of the Measurement object
        
        args:
            patient_number (int):       number of the patient
            patient_age (int):          age of the patient
            mature_oocytes (int):       number of mature oocytes collected from the patient
            clinic (str):               name of the clinic where measurement was performed
            oocyte_number (int):        number of the oocyte
            measurement_number (int):   number of the measurement
            position (int):             measurement position (3/9 or 6 o'clock)
            outcomes (dict):            dict with clinical results of embryo culture
        '''
        for key in MeasurementKeys:
            self.measurement_data[key.value] = -1

        self.measurement_data[
                MeasurementKeys.PATIENT_NUMBER.value] = patient_number
        self.measurement_data[MeasurementKeys.PATIENT_AGE.value] = patient_age
        self.measurement_data[
                MeasurementKeys.MATURE_OOCYTES.value] = mature_oocytes
        self.measurement_data[MeasurementKeys.CLINIC.value] = clinic
        self.measurement_data[
                MeasurementKeys.OOCYTE_NUMBER.value] = oocyte_number
        self.measurement_data[MeasurementKeys.POSITION.value] = position

        if outcomes:
            self.measurement_data.update(outcomes)
    
    def set_outcomes(self, outcomes):
        ''' 
        Set the development outcomes of the oocytes.
        
        args:
            outcomes (dict): dict with developmental outcomes
        '''
        self.measurement_data.update(outcomes)
    
    def set_video_frames(self, video_frames):
        '''
        Set the video_frames of the video.
        
        args:
            video_frames (list of array): a list of images
        '''
        self.measurement_data[
                MeasurementKeys.VIDEO_FRAMES.value] = video_frames
    
    def set_applied_pressure(self, pressure):
        '''
        Set the applied pressure.
        Calculate and set the force applied to the oocyte.
        
        args:
            pressure (float):     applied pressure in [psi]
              
        Formula: F = P*A (Force = Pressure * Area)
        '''
        self.measurement_data[
                MeasurementKeys.APPLIED_PRESSURE.value] = pressure
        PSI_TO_NM2 = 6894.76   # conversion factor from [psi] to [N/m^2]
        UM_TO_M = 1e-6       # conversion factor from [um] to [m]
        force = (pressure * PSI_TO_NM2 
                    * 3.1415 * (self._pipette_size/2.0*UM_TO_M)**2)
        self.set_applied_force(force)
        
    def set_applied_force(self, force):
        '''
        Set the applied force.
        
        args:
            force (float): applied force
        '''
        self.measurement_data[MeasurementKeys.APPLIED_FORCE.value] = force
        
    def set_roi_coordinates(self, coord):
        '''
        Set the coordinates of the region of interest.
        
        args:
            coord (tuple): top left corner coordinates, width and height
        '''
        self.measurement_data[MeasurementKeys.ROI_COORD.value] = coord
        
    def set_pipette_size(self, pipette_size):
        '''
        Set the pipette size in pixels. Calculate and set the conversion factor.
        
        args:
            pipette_size (int): pipette size [pixels]
        '''
        self.measurement_data[
                MeasurementKeys.PIPETTE_SIZE_PIXEL.value] = pipette_size
        conversion_factor = pipette_size/self._pipette_size
        self.set_manual_conversion_factor(conversion_factor)
        
    def set_manual_conversion_factor(self, conversion_factor):
        '''
        Set the manual conversion factor.
        
        args:
            conversion_factor (float): manually determined conversion factor
        '''
        self.measurement_data[
                MeasurementKeys.MANUAL_CONVERSION_FACTOR.value
                ] = conversion_factor
        
    def set_zona_thickness(self, zona_thickness):
        '''
        Set the zona thickness.
        
        args:
            zona_thickness (float): thickness of the zona pellucida
        '''
        self.measurement_data[
                MeasurementKeys.ZONA_THICKNESS.value] = zona_thickness
        
    def set_perivitelline_space(self, perivitelline_space):
        '''
        Set the perivitelline space.
        
        args:
            perivitelline_space (float): size of the perivitelline space
        '''
        self.measurement_data[
                MeasurementKeys.PERIVITELLINE_SPACE.value
                ] = perivitelline_space
    
    def set_zona_position(self, zona_position):
        '''
        Set the zona postion.
        
        args:
            zona_position (int): initial position of the zona pellucida in the image
        '''
        self.measurement_data[
                MeasurementKeys.ZONA_POSITION.value] = zona_position
    
    def set_time(self, time):
        '''
        Set the time vector.
        
        args:
            time (array of float): time vector [s]
        '''
        self.measurement_data[MeasurementKeys.TIME.value] = time
        
    def set_aspiration_depth_zona_pixel(self, aspiration_depth):
        '''
        Set the aspiration depth in pixels.
        
        args:
            aspiration_depth (list of int): aspiration depth of each image [pixels]
        '''
        self.measurement_data[
                MeasurementKeys.ASPIRATION_DEPTH_ZONA_PIXEL.value
                ] = aspiration_depth
        
    def set_aspiration_depth_zona_mech(self, aspiration_depth):
        '''
        Set the aspiration depth in um.
        
        args:
            aspiration_depth (list of float): aspiration depth of each image [um]
        '''
        self.measurement_data[
                MeasurementKeys.ASPIRATION_DEPTH_ZONA_MECH.value
                ] = aspiration_depth
        
    def set_pipette_tip_position(self, tip_position):
        '''
        Set pipette tip position.
        
        args:
            tip_position (int): position of the pipette tip in the first image
        '''
        self.measurement_data[
                MeasurementKeys.PIPETTE_TIP_POSITION.value] = tip_position
        
    def set_model_parameters(self, k0, k1, eta0, eta1, tau):
        '''
        Set the model parameters of the modified Zener model.
        
        args:
            k0, k1, eta0, eta1, tau (float): model parameters
        '''
        self.measurement_data[MeasurementKeys.K0_ZP.value] = k0
        self.measurement_data[MeasurementKeys.K1_ZP.value] = k1
        self.measurement_data[MeasurementKeys.ETA0_ZP.value] = eta0
        self.measurement_data[MeasurementKeys.ETA1_ZP.value] = eta1
        self.measurement_data[MeasurementKeys.TAU_ZP.value] = tau
     
        
if __name__ == '__main__':
    print('Measurement')
        
        

        

        

        
