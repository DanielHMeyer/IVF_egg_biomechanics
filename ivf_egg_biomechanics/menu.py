# -*- coding: utf-8 -*-

import pandas as pd
import numpy as np
import measurement as m
import ioutils
from measurement_analyzer import MeasurementAnalyzer
import outcome_predictor


class Menu:
    """ Display a menu and run chosen routines. """

    def __init__(self):
        """ Initialize an instance of the Menu class """
        self.patient_data = pd.DataFrame()
        self.choices = {
            '1': self.load_patient_data,
            '2': self.analyze_measurement,
            '3': self.train_classifier,
            '4': self.quit_menu
        }

    def display_menu(self):
        """ Display the menu """
        print('''
              ****************************************
              EggBot Menu
              
              1. Load patient data
              2. Analyze a measurement
              3. Train classifier
              4. Quit
              ****************************************
              
              ''')

    def run(self):
        """ Display the menu and respond to choices. """
        status = True
        while status:
            self.display_menu()
            choice = input('Enter an option: ')
            print('')
            [c, status] = self._call_action(choice)

    def _call_action(self, choice):
        """ Call a chosen action """
        action = self.choices.get(choice)
        if action:
            status = action()
            return choice, status
        else:
            print('{0} is not a valid choice'.format(choice))
            return choice, True

    def load_patient_data(self):
        """ Load patient data from excel file """
        print('Loading experimental data...')
        self.patient_data = ioutils.load_excel_file()
        print('Experimental data successfully loaded!')
        return True

    def analyze_measurement(self):
        if self.patient_data.empty:
            print('No patient data loaded yet!')
            return True
        print('Preparing measurement analysis ...')
        patient_data = self.patient_data[self.patient_data['MEASURED'] == 1]
        patient_number = int(input('What is the patient number? '))
        if not (patient_data[m.PatientKeys.PATIENT_NUMBER.value] == patient_number).any():
            print('This patient number does not exist!')
            return True
        else:
            patient_data = patient_data[
                patient_data[m.PatientKeys.PATIENT_NUMBER.value] == patient_number]
        oocyte_number = int(input('What is the oocyte number? '))
        if not (patient_data[m.PatientKeys.OOCYTE_NUMBER.value] == oocyte_number).any():
            print('This oocyte number does not exist!')
            return True
        else:
            index = self.patient_data.index[
                (self.patient_data[m.PatientKeys.PATIENT_NUMBER.value] == patient_number) &
                (self.patient_data[m.PatientKeys.OOCYTE_NUMBER.value] == oocyte_number) &
                (self.patient_data['MEASURED'] == 1)].tolist()
            patient_data = patient_data[patient_data[m.PatientKeys.OOCYTE_NUMBER.value] == oocyte_number]
            keys = patient_data.columns.values.tolist()
            values = patient_data.values[0].tolist()
            patient_data = dict(zip(keys, values))
        manual = input('Analyze measurement manually [Y/N]? ').upper()
        if manual == 'Y':
            manual = True
        elif manual == 'N':
            manual = False
        else:
            print('{} is an invalid option.'.format(manual))
            return True
        patient_info = {patient_key.value: patient_data[patient_key.value]
                        for patient_key in m.PatientKeys}
        outcomes = {outcome_key.value: (patient_data[outcome_key.value]
                                        if isinstance(patient_data[outcome_key.value], str)
                                        else int(patient_data[outcome_key.value]))
                    for outcome_key in m.OutcomesKeys}
        measurement = m.Measurement(patient_info, outcomes)
        meas_analyzer = MeasurementAnalyzer(measurement)
        meas_analyzer.analyze()
        patient_data = pd.DataFrame(data=[measurement.data.values()],
                                    columns=measurement.data.keys(),
                                    index=index)
        self.patient_data.update(patient_data)
        filename = ioutils.choose_file('.xlsx')
        self.patient_data.to_excel(filename)
        return True

    def train_classifier(self):
        features = [m.ParameterKeys.K0_ZP.value,
                    m.ParameterKeys.K1_ZP.value,
                    m.ParameterKeys.TAU_ZP.value,
                    m.ParameterKeys.ETA0_ZP.value,
                    m.ParameterKeys.ETA1_ZP.value,
                    m.PatientKeys.PATIENT_AGE.value,
                    m.PatientKeys.MATURE_OOCYTES.value]
        X = self.patient_data[self.patient_data[
                                  m.OutcomesKeys.FERTILIZED.value] == 1]
        X = X[features]
        X = X.apply(np.log)
        y = self.patient_data[self.patient_data[
                                  m.OutcomesKeys.FERTILIZED.value] == 1]
        y = y[m.OutcomesKeys.ANYBLAST.value]
        predictor = outcome_predictor.OutcomePredictor('svm', 'forward')
        X_train, X_test, y_train, y_test = predictor._create_train_test_set(X, y)
        predictor.fit(X_train, y_train)
        return True

    def quit_menu(self):
        print('Thank you for using the EggBot today!')
        return False


if __name__ == '__main__':
    eggMenu = Menu()
    eggMenu.run()
