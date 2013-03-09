#
#    This script is Copyrighted (c) 2013 by William Gibb and 
#    licensed under the OSI Educational Community License version 1.0
#    
#    Please see the LICENSE.txt file for a full reading of the appopriate
#    license.
#    

import sys
import os
import csv
import optparse
import string
import logging

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger()

def ask_ok(prompt, retries=4, complaint='yes or no, please!'):
    while True:
        ok = raw_input(prompt)
        if ok.lower() in ['y', 'ye', 'yes']:
            return True
        if ok.lower() in ['n', 'no', 'nop', 'nope']:
            return False
        retries = retries - 1
        if retries < 0:
            raise IOError('Can you just answer the question?')
        print complaint

        
def norm_opts():
    '''
    add optparse options here
    '''
    options = []
    options.append(optparse.make_option('-i','--input', dest='input', default=False, 
        help='input file'))
    options.append(optparse.make_option('-o','--output', dest='output', default=False,
        help='output file'))
    options.append(optparse.make_option('--zero_timescale', dest='zero', default=False, action='store_true',
        help='use the first entry as the offset from time zero. change all timestamps to reflect that offset as time zero.'))
    options.append(optparse.make_option('--verbose', dest='verbose', action='store_true',default=False, 
        help='Enable verbose output'))
    
    return options

def vcd_opts():
    '''
    add optparse options here
    '''
    options = []
    options.append(optparse.make_option('-i','--input', dest='input', default=False, 
        help='input file'))
    options.append(optparse.make_option('-o','--output', dest='output', default=False,
        help='output file'))
    options.append(optparse.make_option('--verbose', action='store_true',default=False, 
        help='Enable verbose output'))
    return options