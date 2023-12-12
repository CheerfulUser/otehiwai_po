# -*- coding: utf-8 -*-
"""
Created on Tue Nov 29 04:47:48 2022

@author: porri
"""


from look_targets import make_look_list
from debass_targets import make_debass_list
from swope_targets import make_swope_list
from custom_targets import make_custom_list
from yse_targets import make_yse_list
from refsne_targets import make_refsne_list
from SchedulerMTJOHN import make_schedule
import time


if __name__ == '__main__':
    start = time.perf_counter()
    Tele =['moa', 'bc']
    
    make_look_list(name_priority=[['81P',1],['73P',1],['UN271',1]],mag_priority=[['22-19',3],['19-17',4],['17-15',5],['15-12',6]])
    # make_debass_list()
    # make_swope_list()
    make_yse_list()
    # make_refsne_list()
    
    custom_targets = [{'name':'2021 S3','filter':'R','exptime':300,'repeats':1},
                      {'name':'358P','filter':'R','exptime':300,'repeats':1}]
    make_custom_list(custom_targets)

    make_schedule(telescope = 'moa')
    end = time.perf_counter()
    total_time = (end - start)/60
    print('Total Time to generate schedule:', "{0:0.2f}".format(total_time), 'minutes')
