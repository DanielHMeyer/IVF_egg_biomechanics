# -*- coding: utf-8 -*-

from enum import Enum

class PropertyKeys(Enum):
    ''' A class with keywords of properties '''
    VIDEO_FRAMES = 'VIDEO_FRAMES'
    APPLIED_PRESSURE = 'APPLIED_PRESSURE'
    APPLIED_FORCE = 'APPLIED_FORCE'
    PIPETTE_SIZE_PIXEL = 'PIPETTE_SIZE_PIXEL'
    MANUAL_CONVERSION_FACTOR = 'MANUAL_CONVERSION_FACTOR'
    ZONA_THICKNESS = 'ZONA_THICKNESS'
    PERIVITELLINE_SPACE = 'PERIVITELLINE_SPACE'
    ZONA_POSITION = 'ZONA_POSITION'
    TIME = 'TIME'
    ASPIRATION_DEPTH_ZONA_PIXEL = 'ASPIRATION_DEPTH_ZONA_PIXEL'
    ASPIRATION_DEPTH_ZONA_MECH = 'ASPIRATION_DEPTH_ZONA_MECH'
    PIPETTE_TIP_POSITION = 'PIPETTE_TIP_POSITION'

class OutcomesKeys(Enum):
    ''' A class with keywords of embryo culture outcomes '''
    FERTILIZED = 'FERTILIZED'
    DEGENERATED = 'DEGENERATED'
    NONFERT = 'NONFERT'
    ABNORMALFERT = 'ABNORMALFERT'
    D3GRADE = 'D3GRADE'
    D3VERYGOOD = 'D3_VERYGOOD'
    D3VERYBAD = 'D3VERYBAD'
    D3GOOD = 'D3GOOD'
    D3FAIR = 'D3FAIR'
    D3POOR = 'D3POOR'
    ANYBLAST = 'ANYBLAST'
    GOODBLAST = 'GOODBLAST'
    POORBLAST = 'POORBLAST'
    NOBLAST = 'NOBLAST'
    BLASTGRADE = 'BLASTGRADE'
    
    @classmethod
    def has_value(cls, value):
        return any(value == item.value for item in cls)


class ParameterKeys(Enum):
    ''' A class with keywords of the modified Zener model '''
    K0_ZP = 'K0_ZP'
    K1_ZP = 'K1_ZP'
    TAU_ZP = 'TAU_ZP'
    ETA0_ZP = 'ETA0_ZP'
    ETA1_ZP = 'ETA1_ZP'
    
class PatientKeys(Enum):
    ''' A class with keywords of patient information '''
    PATIENT_NUMBER = 'NUMBER'
    PATIENT_AGE = 'AGE'
    MATURE_OOCYTES = 'MII'
    CLINIC = 'CLINIC'
    OOCYTE_NUMBER = 'OOCYTE'
    POSITION = 'POSITION'

class Measurement:
    ''' A container class to store data from aspiration depth measurements '''
    
    _conversion_factor = 1.55       # Conversion factor for pixels to micrometers: 155 pixels per 100 microns
    _pipette_size = 50.0            # pipette diameter [um]
    
    def __init__(self, patient_number, patient_age, mature_oocytes, clinic, 
                 oocyte_number, position, outcomes={}):
        '''
        Initialize an instance of the Measurement object
        
        args:
            patient_number (int):       number of the patient
            patient_age (int):          age of the patient
            mature_oocytes (int):       number of mature oocytes collected from the patient
            clinic (str):               name of the clinic where measurement was performed
            oocyte_number (int):        number of the oocyte
            position (int):             measurement position (3/9 or 6 o'clock)
            outcomes (dict):            dict with clinical results of embryo culture
        '''
        self.measurement_data = {}
        self.set_patient_information(PatientKeys.PATIENT_NUMBER, patient_number)
        self.set_patient_information(PatientKeys.PATIENT_AGE, patient_age)
        self.set_patient_information(PatientKeys.MATURE_OOCYTES, mature_oocytes)
        self.set_patient_information(PatientKeys.CLINIC, clinic)
        self.set_patient_information(PatientKeys.OOCYTE_NUMBER, oocyte_number)
        self.set_patient_information(PatientKeys.POSITION, position)

        for key in PropertyKeys:
            self.measurement_data[key.value] = -1
        for key in ParameterKeys:
            self.measurement_data[key.value] = -1
        for key in OutcomesKeys:
            self.measurement_data[key.value] = -1

        if outcomes:
            for key, value in outcomes.items():
                if OutcomesKeys.has_value(key):
                    self.set_outcome(OutcomesKeys[key], value)
    
    def set_patient_information(self, key, info):
        '''
        Set information of a patient.
        
        args:
            key (PatientKeys): an attribute of the PatientKeys class
            info (str or int): patient information
        '''
        if not isinstance(key, PatientKeys):
            raise TypeError('Key is invalid. Expected {},' 
                    ' but got {} instead.'.format(PatientKeys, type(key)))
        if (key == PatientKeys.CLINIC):
            if not isinstance(info, str):
                raise TypeError('Info is invalid. Expected {},'
                                ' but got {} instead.'.format(str, type(info)))
        else:
            if not isinstance(info, int):
                raise TypeError('Info is invalid. Expected {},'
                                ' but got {} instead.'.format(
                        int, type(info)))
        self.measurement_data[key.value] = info
    
    def set_outcome(self, key, outcome):
        ''' 
        Set a development outcome of an oocyte.
        
        args:
            key (OutcomeKey): an attribute of the OutcomeKey class
            outcome (str or int): value of the outcome
        '''
        if not isinstance(key, OutcomesKeys):
            raise TypeError('Key is invalid. Expected {},'
                            ' but got {} instead.'.format(
                            OutcomesKeys, type(key)))
        if ((key == OutcomesKeys.BLASTGRADE) | (key == OutcomesKeys.D3GRADE)):
            if not isinstance(outcome, str):
                raise TypeError('Outcome is invalid. Expected {},'
                                ' but got {} instead.'.format(
                        str, type(outcome)))
        else:
            if not isinstance(outcome, int):
                raise TypeError('Outcome is invalid. Expected {},'
                                ' but got {} instead.'.format(
                        int, type(outcome)))
        self.measurement_data[key.value] = outcome
    
    def set_property(self, key, measurement_property):
        '''
        Set a property of a measurement.
        
        args:
            key (PropertyKey): an attribute of the PropertyKey class
            property (list, float): the value of the property
        '''
        if not isinstance(key, PropertyKeys):
            raise TypeError('Key is invalid. Expected {},'
                            ' but got {} instead.'.format(
                    PropertyKeys, type(key)))
        if ((key == PropertyKeys.VIDEO_FRAMES) | 
            (key == PropertyKeys.ASPIRATION_DEPTH_ZONA_MECH) |
            (key == PropertyKeys.ASPIRATION_DEPTH_ZONA_PIXEL) |
            (key == PropertyKeys.TIME)):
            if not isinstance(measurement_property, list):
                raise TypeError('Property is invalid. Expected {},'
                                ' but got {} instead.'.format(list,
                            type(measurement_property)))
        else:
            if not isinstance(measurement_property, float):
                raise TypeError('Property is invalid. Expected {},'
                                ' but got {} instead.'.format(float,
                                type(measurement_property)))
        
        self.measurement_data[key.value] = property
       
    def set_model_parameter(self, key, parameter):
        '''
        Set a model parameter of the modified Zener model.
        
        args:
            key (ParameterKeys): an attribute of the ParameterKeys class
            parameter (float): value of the model parameter
        '''
        if not isinstance(key, ParameterKeys):
            raise TypeError('Key is invalid. Expected {},'
                            ' but got {} instead.'.format(
                    ParameterKeys, type(key)))
        if not isinstance(parameter, float):
            raise TypeError('Parameter is invalid. Expected {},'
                            ' but got {} instead.'.format(
                    float, type(parameter)))
        self.measurement_data[key.value] = parameter
     
        
if __name__ == '__main__':
    print('Measurement')
        
        

        

        

        
