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

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger()

USAGE='''
Python script to convert Agilent CSV waveforms into useful CSV files for 
plotting with gnuplot, or matlibplot or whatever.

csv formatted data is assumed, with the last column containing timestamp
information.

this script normalizes the timebase column into microseconds.  Please 
see the chip1.csv and chip1_normalized.csv for an example of usage.
'''


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


def main(options):
    
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
    
    timebase = None
    
    logger.debug('Welcome to the waveform normalization tool')
    logger.debug('You have specified the file "%s" to transform into a valid source data.' % input_fn)
    logger.debug('You have specified the file "%s" to write data to.' % output_fn)
    if options.verbose:
        if not ask_ok("Is this what you intend do process?"):
            sys.exit(-1)
    
    #now to open up csv file for reading and writing
    ifile = open(input_fn, 'r')
    reader = csv.reader(ifile)
    ofile = open(output_fn, 'wb')
    writer = csv.writer(ofile)
        
    header= reader.next()
    # Update the time field with the appropriate timebase information
    # since we will be stripping it out of the columns themselves
    num_columns = len(header)
    if options.verbose:
        logger.debug("Number of columns in source CSV: %d" % num_columns)
        if options.verbose:
            if not ask_ok("Continue?"):
                sys.exit(0)
    try:
        timeIndex = header.index('Time')
    except ValueError,e:
        logger.error('Could not identify a column header "Time".')
        logger.error('Make sure that the time column has the header "Time"')
        logger.error(('%s') % e)
        sys.exit(-1)
    header[timeIndex]="Time (us)"
    writer.writerow(header)
    
    # process the rows
    rows = []
    if not process_rows(reader,rows,timeIndex,options.zero):
        logger.error('Failed to process rows')
        sys.exit(-1)
    
    logger.debug('Writing out rows')
    for row in rows:
        writer.writerow(row)
    
    logging.info("done writing out normalized file")
    ifile.close()
    ofile.close()
    sys.exit()


def process_rows(csvreader,rows,timeIndex,zero=False):
    if zero:
        row = csvreader.next()
        old_time = row[timeIndex]
        new_time = change_timebase(old_time)
        offset = get_offset(new_time)
        logger.debug('Computed offset:%s'%(str(offset)) )
        new_time = new_time + offset
        row[timeIndex] = new_time
        rows.append(row)
    if zero:
        for row in csvreader:
            old_time = row[timeIndex]
            new_time = change_timebase(old_time)
            new_time = new_time + offset
            row[timeIndex] = new_time
            rows.append(row)
    else:
        for row in csvreader:
            old_time = row[timeIndex]
            new_time = change_timebase(old_time)
            row[timeIndex] = new_time
            rows.append(row)
    return True


def change_timebase(old_time):
    if old_time.endswith('ns'):
        # found nanoseconds
        new_time = (10**-3) * float(old_time[:-2])
    elif old_time.endswith('us'):
        # found microseconds
        new_time = (10**0) * float(old_time[:-2])
    elif old_time.endswith('ms'):
        # found milliseconds
        new_time = (10**3) * float(old_time[:-2])
    elif old_time.endswith('s'):
        new_time = (10**6) * float(old_time[:-1])
    else:
        logger.error("valid timebase given not found in source data")
        logger.error("please examine source data for correct timebase")
        raise ValueError('No valid timebase found in %s' % (old_time))
    return new_time

def get_offset(n):
    if n not in [0, 0.0]:
        offset = -n
    else:
        offset = 0.0
    return offset

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


if __name__ == "__main__":
    '''
    add optparse parsing here
    add option checking here
    '''
    parser = optparse.OptionParser(option_list=norm_opts(),epilog=USAGE)
    (options,args) = parser.parse_args()
    print options
    if not (options.input and options.output):
        logger.error('Must specify input and output files')
        logger.error('%s' % USAGE)
        sys.exit(-1)
    
    main(options)










