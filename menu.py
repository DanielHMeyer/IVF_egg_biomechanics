# -*- coding: utf-8 -*-

import pandas as pd
import measurement as m
import ioutils
import analyzer

class Menu:
    ''' Display a menu and run chosen routines. '''
    
    def __init__(self):
        ''' Initialize an instance of the Menu class '''
        self.patient_data = pd.DataFrame()
        self.choices = {
                '1': self.load_patient_data,
                '2': self.analyze_measurement,
                '3': self.create_dataset,
                '4': self.train_classifier,
                '5': self.quit_menu
                }
        
    def display_menu(self):
        ''' Display the menu '''
        print('''
              ****************************************
              EggBot Menu
              
              1. Load patient data
              2. Analyze a measurement
              3. Create a dataset of measurements
              4. Train classifier
              5. Quit
              ****************************************
              
              ''')
                
    def run(self):
        ''' Display the menu and respond to choices. '''
        status = True
        while status:
            self.display_menu()
            choice = input('Enter an option: ')
            print('')
            [c, status] = self._call_action(choice)
                
    def _call_action(self, choice):
        ''' Call a chosen action '''
        action = self.choices.get(choice)
        if action:
           status = action()
           return choice, status
        else:
           print('{0} is not a valid choice'.format(choice))
           return choice, True
    
    def load_patient_data(self):
        ''' Load patient data from excel file '''
        print('Loading experimental data...')
        self.patient_data = ioutils.load_excel_file()
        print('Experimental data successfully loaded!')
        return True
    
    def analyze_measurement(self):
        print('Preparing measurement analysis ...')
        patient_data = self.patient_data[self.patient_data['MEASURED']==1]
        patient_number = int(input('What is the patient number? '))
        if not (patient_data[
                m.PatientKeys.PATIENT_NUMBER.value]==patient_number).any():
            print('This patient number does not exist!')
            return True
        else:
            patient_data = patient_data[
                    patient_data[m.PatientKeys.PATIENT_NUMBER.value]
                    ==patient_number]
        oocyte_number = int(input('What is the oocyte number? '))
        if not (patient_data[
                m.PatientKeys.OOCYTE_NUMBER.value]==oocyte_number).any():
            print('This oocyte number does not exist!')
            return True
        else:
            index = self.patient_data.index[
                    (self.patient_data[
                    m.PatientKeys.PATIENT_NUMBER.value]==patient_number)&
                    (self.patient_data[
                    m.PatientKeys.OOCYTE_NUMBER.value]==oocyte_number)&
                    (self.patient_data['MEASURED']==1)].tolist()
            patient_data = patient_data[
                    patient_data[m.PatientKeys.OOCYTE_NUMBER.value]
                    ==oocyte_number]
            keys = patient_data.columns.values.tolist()
            values = patient_data.values[0].tolist()
            patient_data = dict(zip(keys, values))
        manual = input('Analyze measurement manually [Y/N]? ').upper()
        if manual=='Y':
            manual = True
        elif manual=='N':
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
        measurement_analyzer = analyzer.Analyzer(measurement)
        measurement_analyzer.analyze()
        patient_data = pd.DataFrame(data=[measurement.data.values()], 
                                          columns=measurement.data.keys(),
                                          index=index)
        self.patient_data.update(patient_data)
        self.patient_data.to_excel('TaiwanData.xlsx')
        return True
        
    def create_dataset(self):
        print('You entered 3')
        return True
        
    def train_classifier(self):
        print('You entered 4')
        return True
        
    def quit_menu(self):
        print('Thank you for using the EggBot today!')
        return False
        
if __name__ == '__main__':
    eggMenu = Menu()
    eggMenu.run()