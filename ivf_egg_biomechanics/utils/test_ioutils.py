# -*- coding: utf-8 -*-

import utils.ioutils as ioutils
import numpy as np
import pandas as pd
import unittest
from unittest.mock import MagicMock


class TestIoutils(unittest.TestCase):
    """ Test the ioutils class """
    def setUp(self):
        pass
    
    def test_extract_data_from_file(self):
        """ Test that data is extracted correctly """
        filename = 'D://Data Daniel//IVF//TaiwanData.xlsx'
        data = ioutils._extract_data_from_file(filename)
        column_names = ['NUMBER', 'AGE', 'MII', 'MEASURED', 'OOCYTE', 
                        'FERTILIZED', 'DEGENERATED', 'NONFERT', 'ABNORMALFERT',
                        'D3GRADE', 'D3VERYGOOD', 'D3VERYBAD', 'D3GOOD', 'D3FAIR', 
                        'D3POOR', 'ANYBLAST', 'GOODBLAST', 'POORBLAST', 'NOBLAST',
                        'BLASTGRADE', 'CLINIC', 'POSITION']
        for col in data.columns:
            self.assertIn(col, column_names)
            
    def test_load_excel_file(self):
        """ Test that data from excel file is loaded correctly """
        filename1 = 'D://Data Daniel//IVF//TaiwanData.xlsx'
        ioutils._choose_file = MagicMock(return_value=filename1)
        ioutils._extract_data_from_file = MagicMock()
        data = ioutils.load_excel_file()
        column_names = ['NUMBER', 'AGE', 'MII', 'MEASURED', 'OOCYTE', 
                        'FERTILIZED', 'DEGENERATED', 'NONFERT', 'ABNORMALFERT',
                        'D3GRADE', 'D3VERYGOOD', 'D3VERYBAD', 'D3GOOD', 'D3FAIR', 
                        'D3POOR', 'ANYBLAST', 'GOODBLAST', 'POORBLAST', 'NOBLAST',
                        'BLASTGRADE', 'CLINIC', 'POSITION']
        for col in data.columns:
            self.assertIn(col, column_names)
        ioutils._choose_file.assert_called_with('.xlsx')
        filename2 = 'D://Data Daniel//IVF//1699_1.avi'
        ioutils._choose_file = MagicMock(return_value=filename2)
        data = ioutils.load_excel_file()
        ioutils._extract_data_from_file.assert_called_once_with(filename1)
        self.assertEqual(data.empty, pd.DataFrame().empty)
            
    def test_create_time_vector(self):
        """ Test that time vector is created correctly """
        num_frames = 93
        time_valve_opened = 23
        frame_rate = 70
        time = ioutils._create_time_vector(num_frames, time_valve_opened, 
                                           frame_rate)
        time_correct = np.linspace(0.0, 0.5, num=int(frame_rate*0.5), endpoint=False)
        time_correct = np.reshape(time_correct, (len(time_correct), 1))
        time_correct = time_correct[:, 0].tolist()
        self.assertCountEqual(time, time_correct)
        
        num_frames = 53
        time = ioutils._create_time_vector(num_frames, time_valve_opened,
                                           frame_rate)
        max_time = (num_frames - time_valve_opened)/float(frame_rate) - 0.03
        time_correct = np.linspace(0.0, max_time,
                                   num=int(70*max_time), endpoint=False)
        time_correct = np.reshape(time_correct, (len(time_correct), 1))
        time_correct = time_correct[:, 0].tolist()
        self.assertCountEqual(time, time_correct)


if __name__ == '__main__':
    unittest.main()
