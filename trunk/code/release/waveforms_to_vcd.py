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
import datetime
import re

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger()

__version__ = 2

USAGE='''foo'''

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

def build_symbol_list(input_list):
    '''
    
    '''
    printable_start = 33
    printable_stop = 127
    symbol_list = []
    for i in xrange(printable_start, printable_stop):
        symbol_list.append(chr(i))
    q,r = divmod(len(input_list), len(symbol_list))
    if (q,r)  <= (1,0):
        return symbol_list
    else:
        for i in range(q):
            if i < q - 1:
                r_temp = printable_stop - printable_start
            else:
                r_temp = r
            for j in range(r_temp):
                new_symbol = symbol_list[i] + chr(j+printable_start)
                symbol_list.append(new_symbol)
        return symbol_list
    

class waveforms():
    def __init__(self,zero_timebase = False):
        self.zero_timebase = zero_timebase
        self.rows = []
        self.time_index = None
        self.header_row = None
        self.header_dict = {}
        self.old_row = None
        self.change_data = []
        self.time_re = re.compile('^Time$')
    
    def process_file(self,fn_input, fn_output):
        ifile = open(fn_input, 'rb')
        reader = csv.reader(ifile)
        self.header_row = reader.next()
        '''
        # get time index
        try:
            self.time_index = self.header_row.index('Time')
        except ValueError,e:
            logger.error('Could not identify a column header "Time".')
            logger.error('Make sure that the time column has the header "Time"')
            logger.error(('%s') % e)
            return False
        '''
        # build symbols list
        
        symbols = build_symbol_list(self.header_row)
        hzip = zip(self.header_row, range(len(self.header_row)))
        for i in hzip:
            value, indx = i
            m = self.time_re.search(value)
            if m:
                if self.time_index is None:
                    self.time_index = indx
                else:
                    raise ValueError('Duplicate "Time" index found.')
            else:
                symbol = symbols.pop()
                self.header_dict[indx] = {'name' : value, 'symbol' : symbol}
        if not self.time_index:
            logger.error('Failed to find time index')
            return False
        # normalize the timeebase on all the rows
        self.normalize_rows(reader)
        ifile.close()
        # start writing the VCD file
        ofile = open(fn_output, 'wb')
        self.write_vcd_header(ofile)
        self.initialize_change_data(ofile)
        last_time = self.compute_change_data()
        self.write_changes_to_vcd(ofile)
        ofile.write('#%s\n' %(last_time))
        ofile.close()
        return True
        
    def write_changes_to_vcd(self,ofile):
        logging.debug('write_changes_to_vcd')
        for change in self.change_data:
            time = change['time']
            change.pop('time')
            ofile.write('#%s\n' % (time))
            for symbol in change:
                ofile.write('%s%s\n' % (str(change[symbol]),symbol))
        
    def compute_change_data(self):
        '''
        
        returns the last time in the input data
        '''
        # we already consumed the first row in self.initialize_change_data()
        for row in self.rows[1:]:
            changes = {}
            t = row[self.time_index]
            del row[self.time_index]
            t,_ = str(t).split('.')
            if row != self.old_row:
                for i in range(len(row)):
                    if row[i] != self.old_row[i]:
                        value = row[i]
                        symbol = self.header_dict[i]['symbol']
                        changes[symbol] = value
                changes['time'] = t
                self.old_row = list(row)
                self.change_data.append(changes)
        return t
        
    def initialize_change_data(self, ofile):
        self.old_row = self.rows[0]
        t = self.old_row[self.time_index]
        del self.old_row[self.time_index]
        t,_ = str(t).split('.')
        if int(t) != 0:
            raise ValueError('First row of data does not contain "0" as the timestamp.')
        ofile.write('$comment\n Note: Executing $dumpvars on all variables at time 0\n$end\n')
        ofile.write('$dumpvars\n')
        for index in self.header_dict:
            symbol = self.header_dict[index]['symbol']
            value = self.old_row[index]
            ofile.write('%s%s\n' % (str(value),symbol))
        ofile.write('$end\n')
        
    def write_vcd_header(self, ofile):
        '''
        write out the VCD header
        this assumes a fixed timescale of 1 microsecond
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
        for i in self.header_dict:
            symbol = self.header_dict[i]['symbol']
            name = self.header_dict[i]['name']
            ofile.write('$var wire 1 %s %s $end\n' %(symbol,name))
        ofile.write('$upscope $end\n')
        ofile.write('$enddefinitions $end\n')
        return True
    
    def normalize_rows(self,csvreader):
        '''
        process_rows
        
        input
        csvreader
        '''
        if self.zero_timebase:
            row = csvreader.next()
            old_time = row[self.time_index]
            new_time = self.change_timebase(old_time)
            offset = get_offset(new_time)
            logger.debug('Computed offset:%s'%(str(offset)) )
            new_time = new_time + offset
            row[self.time_index] = new_time
            self.rows.append(row)
        if self.zero_timebase:
            for row in csvreader:
                old_time = row[self.time_index]
                new_time = self.change_timebase(old_time)
                new_time = new_time + offset
                row[self.time_index] = new_time
                self.rows.append(row)
        else:
            for row in csvreader:
                old_time = row[self.time_index]
                new_time = self.change_timebase(old_time)
                row[self.time_index] = new_time
                self.rows.append(row)
        return True

    def change_timebase(self,old_time):
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
    
    logger.debug('Welcome to the waveform to VCD tool')
    logger.debug('You have specified the file "%s" to transform into a valid source data.' % input_fn)
    logger.debug('You have specified the file "%s" to write data to.' % output_fn)
    if options.verbose:
        if not ask_ok("Is this what you intend do?"):
            sys.exit(-1)
    
    wf = waveforms(options.zero)
    logger.debug('Processing file')
    try:
        if wf.process_file(input_fn, output_fn):
            logger.debug('Sucessfully processed file')
            sys.exit(0)
        else:
            logger.debug('Failed to process file')
            sys.exit(-1)
    except ValueError, e:
        logger.error('Exception occured')
        logger.error('%s' % e)
        sys.exit(-1)
    
    
    
def opts():
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
    parser = optparse.OptionParser(option_list=opts(),epilog=USAGE)
    (options,args) = parser.parse_args()
    if not (options.input and options.output):
        logger.error('Must specify input and output files')
        logger.error('%s' % USAGE)
        sys.exit(-1)

    main(options)