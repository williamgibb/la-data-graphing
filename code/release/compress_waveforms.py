#
#	This script is Copyrighted (c) 2011 by William Gibb and 
#	licensed under the OSI Educational Community License version 1.0
#	
#	Please see the LICENSE.txt file for a full reading of the appopriate
#	license.
#	

import sys
import csv
import getopt
import string


def usage():
	print '''
		
		script to convert normalized csv waveform files into a minimal
		representation of themselves.  this records datapoints around 
		transitions, vastly reducing the amount of data required to
		represent the captured data.
		
		THIS TOOL IS DESIGNED TO WORK ON CSV FILES PROCCESSED WITH
		normalize_waveforms.py.  Please see sample CSV files from the SVN tree
		for examples of the data this script expects.
		
		SWITCHS
		
		-i, --input		input file
		-o, --output	output file
		-v				verbose
		-h, --help		this message
	'''

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

def main():
	try:
		opts, args = getopt.getopt(sys.argv[1:], "hi:o:v", ["help", "input=","output="])
	except getopt.GetoptError, err:
		# print help information and exit:
		print str(err) # will print something like "option -a not recognized"
		usage()
		sys.exit(2)
	input = None
	output = None
	verbose = False
	for o, a in opts:
		if o == "-v":
			verbose = True
		elif o in ("-h", "--help"):
			usage()
			sys.exit()
		elif o in ("-i", "--input"):
			input = a
		elif o in ("-o", "--output"):
			output = a
		else:
			assert False, "unhandled option"
			
	if (input == None):
		print "need to specify input file"
		usage()
		sys.exit(2)
	if (output == None):
		print "need to specify output file"
		usage()
		sys.exit(2)

	skew_time = 0.0001

	print "Welcome to the waveform compression tool"
	print "You have specified the following input file:  " + input
	print "You have specified the following output file: " + output
	if(ask_ok("Is this correct?") == False):
		sys.exit(0)
	
	#now to open up csv file for reading and writing
	ifile = open(input, 'r')
	reader = csv.reader(ifile)
	ofile = open(output, 'wb')
	writer = csv.writer(ofile)


	header= reader.next()
	num_columns = len(header)
	#	
	#	num_columns 	= 	total number of rows
	#	num_columns-1 	=	time header
	#	num_columns-2	=	last data stamp
	last_column	=	num_columns - 2
	time_column	=	num_columns - 1

	if (verbose):
		print "Number of columns in source CSV :" + str(num_columns)
		if(ask_ok("Continue?") == False):
			sys.exit(0)
	writer.writerow(header)

	#	prep for loop - write out the first entry and record it as the 
	#	old_row for the interation loop
	old_row = reader.next()
	writer.writerow(old_row)
	last_time_written = 0
	#	iterate!
	for row in reader:
		i = 0
		write_row = False
		for item in row:
			if (item != old_row[i]):
				write_row = True
				break
			i = i+1
			if(i == (time_column)):
				break
				
		if(write_row):
#			print "writing row branch - last_time_written: " + str(last_time_written)
			if(last_time_written != old_row[time_column]):
				if(verbose):
					print "old_row time: " + str(old_row[time_column])
				writer.writerow(old_row)
			skew_row = old_row
			skew_row[time_column] = float(row[time_column]) - skew_time
			writer.writerow(skew_row)
			writer.writerow(row)
			last_time_written = row[time_column]
			if (verbose):
				print "new last_time_written: " + str(last_time_written)
		old_row = row
	
	#write out the last row
	writer.writerow(old_row)
	print "Done compressing CSV file!"
	ifile.close()
	ofile.close()
	sys.exit()
	
if __name__ == "__main__":
    main()

