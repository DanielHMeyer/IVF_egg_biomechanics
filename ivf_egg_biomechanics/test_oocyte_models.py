# -*- coding: utf-8 -*-

import unittest
import models
import numpy as np


class TestModels(unittest.TestCase):
    """ Test the Models class """
    def setUp(self):
        self.time = np.asarray([0.1, 0.2, 0.3, 0.4])
        self.aspiration_depth = np.asarray([9*1e-6, 10*1e-6, 10.5*1e-6, 11*1e-6])
        self.model = models.ModifiedZener(self.time, self.aspiration_depth, 1.39*1e-6)
        self.params = (0.0045, 0.103, 0.3447, 0.001) # k0, k1, n1, tau
    
    def test_init_function(self):
        """ Test that instance is initialized correctly """
        self.assertCountEqual(self.model.time, [0.1, 0.2, 0.3, 0.4])
        self.assertCountEqual(self.model.aspiration_depth, [9*1e-6, 10*1e-6, 10.5*1e-6, 11*1e-6])
        self.assertEqual(self.model.applied_force, 1.39*1e-6)
        
    def test_invalid_input_time(self):
        """ Test that TypeError is raised when input for time is invalid """
        with self.assertRaises(TypeError):
            models.ModifiedZener([1, 2, 3, 4], self.aspiration_depth, 1.0)
        with self.assertRaises(ValueError):
            models.ModifiedZener(np.asarray([[1, 2, 3, 4], [5, 6, 7, 8]]), self.aspiration_depth, 1.0)
    
    def test_invalid_input_aspiration_depth(self):
        """ Test that TypeError is raised when input for aspiration_depth is invalid """
        with self.assertRaises(TypeError):
            models.ModifiedZener(self.time, [1, 2, 3, 4], 1.0)
        with self.assertRaises(ValueError):
            models.ModifiedZener(self.time, np.asarray([[1, 2, 3, 4], [5, 6, 7, 8]]), 1.0)
            
    def test_invalid_input_applied_force(self):
        """ Test that TypeError is raised when input for applied_force is invalid """
        with self.assertRaises(TypeError):
            models.ModifiedZener(self.time, self.aspiration_depth, 1)
               
    def test_calculate_model_output(self):
        """ Test that calculate_model_output function returns correct result """
        k0, k1, n1, tau = self.params
        F0 = np.repeat(self.model.applied_force, len(self.model.time))
        X = [self.model.time, F0]
        result = self.model._calculate_model_output(X, k0, k1, n1, tau)*1e5
        result_correct = [1.3898, 1.4301, 1.4704, 1.5108]
        for res, resc in zip(result, result_correct):
            self.assertAlmostEqual(res, resc, places=3)
            
    def test_objective_function(self):
        """ Test that _objective_function returns correct result """
        asp_dep_temp = np.asarray([0.14*1e-6, 0.24*1e-6, 0.34*1e-6, 0.45*1e-6])
        F0 = np.repeat(self.model.applied_force, len(self.model.time))
        weights = np.repeat(0.1, len(self.model.time))
        X = [self.model.time, F0, weights]
        result = self.model._objective_fun(self.params, X, asp_dep_temp)
        self.assertAlmostEqual(result, 80.8234, places=3)
        
        
if __name__ == '__main__':
    unittest.main()
