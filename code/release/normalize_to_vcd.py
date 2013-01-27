#
#    This script is Copyrighted (c) 2012 by William Gibb and 
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
import re
import datetime

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger()

__version__ = 1

USAGE='''
This script is designed to convert normalized waveforms into VCD files.

This is not designed to implement extended VCD format.

The input for this script is intended to come from normalize_waveforms.py
with the --zero_timescale option enabled.

'''

def main(options):
    '''
    stuff
    '''
    # constant RE to indentify the time coloumn
    time_re = '^Time\s\([\w]{1,2}\)$'
    compiled_time = re.compile(time_re)
    '''
    Generate a list of printable ASCII characters, in order to comply with
    IEEE Standard 1364-1995 Section 18.  These can be used to indentify all
    signals in a VCD.
    '''
    IEEE_PRINTABLE = []
    for i in range(33,127):
        IEEE_PRINTABLE.append(chr(i))
    
    if not os.path.isfile(options.input):
        logger.error('input file "%s" does not exist' %options.input)
        sys.exit(-1)
    else:
        input_fn = options.input
    
    if os.path.isdir(options.output):
        logger.error('output file "%s" is a directory. must be a filename.' % options.output)
        sys.exit(-1)
    if os.path.exists(options.output):
        logger.warning('output file "%s" already exists.  THIS WILL OVERWRITE THE EXISTING FILE' % options.output)
    output_fn = options.output
    
    if not options.verbose:
        logging.info('Disable verbose logging')
        logger.setLevel(logging.INFO)
    
    logger.debug('Welcome to the VCD waveform writer tool')
    logger.debug('You have specified the file "%s" to transform into a vcd file.' % input_fn)
    logger.debug('You have specified the file "%s" to write data to.' % output_fn)
    if options.verbose:
        if not ask_ok("Is this what you intend do process?"):
            sys.exit(-1)
    
    #now to open up csv file for reading and writing
    ifile = open(input_fn, 'r')
    reader = csv.reader(ifile)
    ofile = open(output_fn, 'wb')
    
    # build header and VCD symbol information
    # this will work for up to 96 columns
    symbols = list(IEEE_PRINTABLE)
    timeIndex = None
    header= reader.next()
    hzip = zip(header,range(len(header)))
    header_dict = {}
    for i in hzip:
        value,indx = i
        m = compiled_time.match(value)
        if m:
            timeIndex = indx
        else:
            symbol = symbols.pop()
            header_dict[indx] = {'name':value, 'symbol':symbol}
    if not timeIndex:
        logger.error('Did not identify time index')
        logger.error('Time column must match the regex: %s' % time_re)
        sys.exit(-1)
    # write VCD header information
    write_vcd_header(ofile,header_dict)
    # get the first row of data, and use that row to initialize the variables
    # at the first time #0
    row = reader.next()
    t = row[timeIndex]
    del row[timeIndex]
    t,_ = t.split('.')
    if int(t) != 0:
        logger.error('First row of data does not contain "0" as the timestamp.')
        sys.exit(-1)
    ofile.write('$comment\n Note: Executing $dumpvars on all variables at time 0\n$end\n')
    ofile.write('$dumpvars\n')
    for index in header_dict:
        symbol = header_dict[index]['symbol']
        value = row[index]
        ofile.write('%s%s\n' % (str(value),symbol))
    ofile.write('$end\n')
    old_row = list(row)
    change_data = []
    for row in reader:
        changes = {}
        t = row[timeIndex]
        del row[timeIndex]
        t,_ = t.split('.')
        if row != old_row:
            for i in range(len(row)):
                if row[i] != old_row[i]:
                    value = row[i]
                    symbol = header_dict[i]['symbol']
                    changes[symbol] = value
            changes['time'] = t
            old_row = list(row)
            change_data.append(changes)
    # write change data
    for change in change_data:
        write_changes(change,ofile)
    ofile.write('#%s\n' %(t))
    
    ifile.close()
    ofile.close()
    sys.exit(0)
    
    

def write_changes(changes, ofile):
    '''
    write out the value/time data to ofile in VCD format
    '''
    time = changes['time']
    changes.pop('time')
    ofile.write('#%s\n' % (time))
    for symbol in changes:
        ofile.write('%s%s\n' % (str(changes[symbol]),symbol))


def write_vcd_header(ofile,header_dict):
    '''
    write out the VCD header
    this assumes a fixed timestacle of 1 microsecond
    '''
    version_string = 'normalize_to_vcd %d' % (__version__)
    date_format = '%Y-%m-%dT%H:%M:%SZ'
    t = datetime.datetime.utcnow()
    date_string = t.strftime(date_format)
    ofile.write('$date %s $end\n' %(date_string))
    ofile.write('$version %s $end\n' %(version_string))
    ofile.write('$timescale 1 us $end\n')
    # scope
    ofile.write('$scope module logic_analyzer $end\n')
    for i in header_dict:
        symbol = header_dict[i]['symbol']
        name = header_dict[i]['name']
        ofile.write('$var wire 1 %s %s $end\n' %(symbol,name))
    ofile.write('$upscope $end\n')
    ofile.write('$enddefinitions $end\n')
    return True

def ask_ok(prompt, retries=4, complaint='Yes or no, please!'):
    while True:
        ok = raw_input(prompt)
        if ok in ('y', 'ye', 'yes'):
            return True
        if ok in ('n', 'no', 'nop', 'nope'):
            return False
        retries = retries - 1
        if retries < 0:
            raise IOError('refusenik user')
        print complaint

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


if __name__ == "__main__":
    '''
    add optparse parsing here
    add option checking here
    '''
    parser = optparse.OptionParser(option_list=vcd_opts(),epilog=USAGE)
    (options,args) = parser.parse_args()
    if not (options.input and options.output):
        logger.error('Must specify input and output files')
        logger.error('%s' % USAGE)
        sys.exit(-1)
    
    main(options)