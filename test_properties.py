# -*- coding: utf-8 -*-

''' Test the property class '''

import properties as prop
import unittest

class TestProperty(unittest.TestCase):
    def setUp(self):
        pass
    
    def test_type_error_video_frames(self):
        '''
        Test that type error is raised when video_frames is not a list
        '''
        with self.assertRaises(TypeError):
            prop.Property(2.0, 5.1)
    
    def test_type_error_scale(self):
        '''
        Test that type error is raised when scale is not a float
        '''
        with self.assertRaises(TypeError):
            prop.Property([5, 4, 3], 3)
            
    def test_pipette_size(self):
        '''
        Test that pipette size is calculated correctly.
        '''
        pipette_size = prop.PipetteSize([],4.0)
        self.assertAlmostEqual(
                pipette_size._calculate_pipette_size((0,0), (100,50)), 12.5)
        
    def test_pipette_position(self):
        '''
        Test that pipette position is calculated correctly.
        '''
        pipette_position = prop.PipettePosition([], 4.0)
        self.assertAlmostEqual(
                pipette_position._calculate_pipette_position((100,50)), 25.0)
        
    def test_zona_thickness(self):
        '''
        Test that zona thickness is calculated correctly
        '''
        zona_thickness = prop.ZonaThickness([], 4.0, 2.0)
        self.assertAlmostEqual(
                zona_thickness._calculate_zona_thickness((100,50), (140,80)), 
                6.25)


if __name__ == '__main__':
    unittest.main()