# -*- coding: utf-8 -*-

import measurement as m
import unittest

class TestMeasurement(unittest.TestCase):
    ''' Test the Measurement class '''
    def setUp(self):
        self.outcomes = {'D3GOOD': 1, 'D3FAIR': 0, 'D3POOR': 0}
    
    def test_init_function(self):
        ''' Test that instance is initialized correctly '''
        meas = m.Measurement(1234, 24, 14, 'STANFORD', 5, 6, self.outcomes)
        self.assertEqual(
                meas.measurement_data[m.PatientKeys.PATIENT_NUMBER.value], 1234)
        self.assertEqual(
                meas.measurement_data[m.PatientKeys.PATIENT_AGE.value], 24)
        self.assertEqual(
                meas.measurement_data[m.PatientKeys.MATURE_OOCYTES.value], 14)
        self.assertEqual(
                meas.measurement_data[m.PatientKeys.CLINIC.value], 'STANFORD')
        self.assertEqual(
                meas.measurement_data[m.PatientKeys.OOCYTE_NUMBER.value], 5)
        self.assertEqual(
                meas.measurement_data[m.PatientKeys.POSITION.value], 6)
        self.assertEqual(
                meas.measurement_data[m.OutcomesKeys.D3GOOD.value], 1)
        self.assertEqual(
                meas.measurement_data[m.OutcomesKeys.D3FAIR.value], 0)
        self.assertEqual(
                meas.measurement_data[m.OutcomesKeys.D3POOR.value], 0)
        self.assertEqual(
                meas.measurement_data[m.OutcomesKeys.ABNORMALFERT.value], -1)
        for keys in m.ParameterKeys:
            self.assertEqual(meas.measurement_data[keys.value], -1)
        for keys in m.PropertyKeys:
            self.assertEqual(meas.measurement_data[keys.value], -1)
        
    def test_init_function_empty_outcomes(self):
        ''' Test that instance is initialized correctly if outcomes is an empty dict '''
        meas = m.Measurement(1234, 24, 14, 'STANFORD', 5, 6, outcomes={})
        self.assertEqual(
                meas.measurement_data[m.PatientKeys.PATIENT_NUMBER.value], 1234)
        for keys in m.OutcomesKeys:
            self.assertEqual(meas.measurement_data[keys.value], -1)
    
    def test_init_function_no_outcomes(self):
        ''' Test that instance is initialized correctly if no outcomes are specified '''
        meas = m.Measurement(1234, 24, 14, 'STANFORD', 5, 6)
        self.assertEqual(
                meas.measurement_data[m.PatientKeys.PATIENT_NUMBER.value], 1234)
        for keys in m.OutcomesKeys:
            self.assertEqual(meas.measurement_data[keys.value], -1)
    
    def test_type_error_set_patient_information(self):
        ''' Test that a TypeError is raised if info is not a string '''
        with self.assertRaises(TypeError):
            m.Measurement.set_patient_information(
                    m.PatientKeys.CLINIC, 5.0)
        ''' Test that a TypeError is raised if info is not an int '''
        with self.assertRaises(TypeError):
            m.Measurement.set_patient_information(
                    m.PatientKeys.PATIENT_NUMBER, 4.2)
        ''' Test that a TypeError is raised if key is not in PatientKeys '''
        with self.assertRaises(TypeError):
            m.Measurement.set_patient_information('INVALIDKEY', 'STANFORD')
    
    def test_type_error_set_outcomes(self):
        ''' Test that a TypeError is raised if outcome is not a string '''
        with self.assertRaises(TypeError):
            m.Measurement.set_outcome(
                    m.OutcomesKeys.BLASTGRADE, 5.0)
        ''' Test that a TypeError is raised if outcome is not an int '''
        with self.assertRaises(TypeError):
            m.Measurement.set_outcome(
                    m.OutcomesKeys.D3FAIR, 4.2)
        ''' Test that a TypeError is raised if outcome is not in OutcomeKeys '''
        with self.assertRaises(TypeError):
            m.Measurement.set_outcome('INVALIDKEY', 1)
    
    def test_type_error_set_property(self):
        ''' Test that a TypeError is raised if property is not a list '''
        with self.assertRaises(TypeError):
            m.Measurement.set_property(
                    m.PropertyKeys.VIDEO_FRAMES, 5.0)
        ''' Test that a TypeError is raised if property is not a float '''
        with self.assertRaises(TypeError):
            m.Measurement.set_property(
                    m.PropertyKeys.APPLIED_PRESSURE, 4)
        ''' Test that a TypeError is raised if property is not in PropertyKeys '''
        with self.assertRaises(TypeError):
            m.Measurement.set_property('INVALIDKEY', [])
            
    def test_type_error_set_model_parameter(self):
        ''' Test that a TypeError is raised if parameter is not a float '''
        with self.assertRaises(TypeError):
            m.Measurement.set_property(
                    m.ParameterKeys.ETA0_ZP, 4)
        ''' Test that a TypeError is raised if parameter is not in ParameterKeys '''
        with self.assertRaises(TypeError):
            m.Measurement.set_model_parameter('INVALIDKEY', 4.7)
    
    
            
if __name__ == '__main__':
    unittest.main()