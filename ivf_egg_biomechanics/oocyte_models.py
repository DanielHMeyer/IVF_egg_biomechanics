# -*- coding: utf-8 -*-

import numpy as np
from scipy.optimize import minimize
from matplotlib import pyplot as plt
from measurement import ParameterKeys


class Model(object):
    """
    A parent class for different models used to fit the experimental data.
    """
    def __init__(self, time, aspiration_depth, applied_force):
        """
        Initialize an instance of class Model.
        
        Args:
            time (array of float):   time vector
            aspiration_depth (array of float):  aspiration depth
            applied_force (float):  force applied to the oocyte during measurement
        """
        for i, arg in enumerate([time, aspiration_depth]):
            if not isinstance(arg, np.ndarray):
                raise TypeError('Input {} is invalid. Expected {}, '
                                ' but got {} instead.'.format(
                                        i+1, np.ndarray, type(arg)))
            if len(arg.shape)!=1:
                raise ValueError('Expected a 1D array, '
                                 'but got {} instead.'.format(len(arg.shape)))
        if not isinstance(applied_force, float):
            raise TypeError('Input for applied_force is invalid.'
                            'Expected {}, but got {} instead.'.format(
                                    float, type(applied_force)))
        self.time = time
        self.aspiration_depth = aspiration_depth
        self.applied_force = applied_force


class ModifiedZener(Model):
    """
    A class to fit the modified zener model to the experimental data.
    """
  
    @staticmethod
    def _calculate_model_output(X, k0, k1, n1, tau):
        """
        The spring-damper model used to fit the data.
        
        Args:
            X:                  array (size: Nx2) consisting of time and f0
                time:           time vector of an aspiration depth measurement
                f0:             applied force during the measurement
            k0, k1, n1, tau (float):    the parameters of the model
        Returns:
            asp_depth (array):  the calculated aspiration depth based on the parameter values
        """
        time = X[0]
        f0 = X[1]
        return f0/k1 * (1 - k0/(k0+k1)*np.exp(-time/tau)) + time*f0/n1
    
    @staticmethod
    def _objective_fun(p, X, y):
        """
        Determine the fitness of an solution by calculating the sum of squared errors. Lower is better.
        
        Args:
            p (float):  parameters (k0, k1, n1, tau) of the found solution
            X:          array (size: Nx3) consisting of time, F0 and w
                time:   time vector of an aspiration depth measurement
                F0:     applied force during the measurement
                w:      weights for the individual values of the aspiration depth measurement
            y:          measured aspiration depth (from video)
        Returns:    
            SSE (float):    the sum of squared errors between the actual aspiration depth and 
                            the calculated aspiration depth using the provided parameters p
        """
        k0, k1, n1, tau = p
        weights = X[2]
        asp_dep_test = ModifiedZener._calculate_model_output(X[0:2], k0, k1, n1, tau)*1e6
        asp_dep_temp = y*1e6
        return sum(weights*((asp_dep_test-asp_dep_temp)**2))
    
    @staticmethod
    def _optimize_model_parameters(time, aspiration_depth, applied_force,
                                   weights, bounds):
        """
        Optimize a cost function to get the best set of model parameters.
        
        Args:
            time (array of floats):                 time vector
            aspiration_depth (array of floats):     measured aspiration depth
            applied_force (float):                  force applied to the oocyte
            weights (array of float):               vector of weights for each data point
                                                    of aspiration depth
            bounds (tuple):                         bounds for each of the 4 model parameters
        Returns:
            params (dict): the optimal model parameters
        """
        f0 = np.repeat(applied_force, len(time))
        X = [time, f0, weights]
        # k0, k1, n1, tau
        params0 = [0.1, 0.2, 0.1, 0.1]
        if not bounds:
            res_min = minimize(ModifiedZener._objective_fun, params0, 
                               (X, aspiration_depth),
                               options={'gtol': 1e-14, 'disp': False})
        else:
            res_min = minimize(ModifiedZener._objective_fun, params0, 
                               (X, aspiration_depth), 
                               method='TNC', bounds=bounds, 
                               options={'gtol': 1e-14, 'disp': False})
        k0, k1, eta1, tau = res_min.x
        eta0 = tau*(k0*k1)/(k0 + k1)
        params = {ParameterKeys.K0_ZP.value: k0, ParameterKeys.K1_ZP.value: k1,
                  ParameterKeys.ETA0_ZP.value: eta0, 
                  ParameterKeys.ETA1_ZP.value: eta1,
                  ParameterKeys.TAU_ZP.value: tau}
        return params
    
    @staticmethod
    def _plot_fits(aspiration_depth, time, params, force):
        """
        Plot the results of fitting the modified zener model to the
        experimental data.
        
        Args:
            aspiration_depth (array of float):  the aspiration depth
            time (array of float):              time points
            params (dict):                      the model parameters
            force (float):                      the applied force
        """
        k0 = params[ParameterKeys.K0_ZP.value]
        k1 = params[ParameterKeys.K1_ZP.value]
        eta1 = params[ParameterKeys.ETA1_ZP.value]
        tau = params[ParameterKeys.TAU_ZP.value]
        t_fine = np.linspace(0, 0.5, num=1000)
        force_fine = np.repeat(force, len(t_fine))
        X = [t_fine, force_fine]
        asp_dep = ModifiedZener._calculate_model_output(X, k0, k1, eta1, tau)
        plt.figure()
        plt.plot(time, aspiration_depth, 'ro', label='Meas')
        plt.plot(t_fine, asp_dep, 'g', label='Fit')
        plt.legend(loc='lower right')
        plt.xlim([0,0.5])
        plt.ylim([0,0.000035])
        plt.show
        plt.pause(1)

    def fit(self, bounds=(), weighted=True):
        """
        Fit the model to the experimental data.
        
        Args:
            bounds (tuple): limits for the model parameters
            weighted (bool): True for weighted fit
        """
        if not isinstance(bounds, tuple):
            raise TypeError('Invalid type for input bounds.'
                            'Expected {}, but got {} instead.'.format(
                                    tuple, type(bounds)))
        if len(bounds)!=4:
            raise ValueError('Invalid size for input bounds.'
                             'Expected length 4, but got length {} instead.'.format(
                                     len(bounds)))
        if not isinstance(weighted, bool):
            raise TypeError('Invalid type for input weighted.'
                            'Expected {}, but got {} instead.'.format(
                                    bool, type(weighted)))
        if weighted:
            weights = np.repeat(0.1, len(self.time))
            weights[0] = 10
            weights[1:5] = 1
        else:
            weights = np.repeat(1,len(self.time))

        params = ModifiedZener._optimize_model_parameters(self.time, 
                                    self.aspiration_depth, 
                                    self.applied_force, weights, bounds)
        ModifiedZener._plot_fits(self.aspiration_depth, self.time, params, 
                                 self.applied_force)
        return params


if __name__ == '__main__':
    print('models')
