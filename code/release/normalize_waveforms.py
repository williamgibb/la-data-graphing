

import sys
import csv
import getopt
import string

def usage():
	print '''
		
		python script to convert agilient CSV waveforms into useful 
		CSV files for plotting with gnuplot, or matlibplot.
		or whatever.
		
		-i, --input		input file
		-o, --output	output file
		-t,	--time		timebase (ms, us, ns) 	CURRENTLY NOT USED
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
		opts, args = getopt.getopt(sys.argv[1:], "hi:o:t:v", ["help", "input=","output=","time="])
	except getopt.GetoptError, err:
		# print help information and exit:
		print str(err) # will print something like "option -a not recognized"
		usage()
		sys.exit(2)
	input = None
	output = None
	timebase = None
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
		elif o in ("-t", "--time"):
			timebase =	a
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
#	if (timebase == None):
#		print "need to specify a timebase"
#		usage()
#		sys.exit(2)
	#	
	print "Welcome to the waveform normalization tool"
	print "You have specified the file: " + input + " to massage into a valid source data."
#	print "You have assumed the following timebase: " + timebase
	print "You have specified the file: " + output + " to write data to."
	if(ask_ok("Is this correct?") == False):
		sys.exit(0)
	
	#now to open up csv file for reading and writing
	ifile = open(input, 'r')
	reader = csv.reader(ifile)
	ofile = open(output, 'wb')
	writer = csv.writer(ofile)
		
	header= reader.next()
	# Update the time field with the appropriate timebase information
	# since we will be stripping it out of the columns themselves
	num_columns = len(header)
	if (verbose):
		print "Number of columns in source CSV :" + num_columns
	header[num_columns-1]="Time (us)"
	writer.writerow(header)
	
	for row in reader:
		old_time = row[num_columns-1]

		i=old_time.find("s")
		j=old_time.find("ms")
		k=old_time.find("us")
		l=old_time.find("ns")
		
		if((i!=-1) and (j==-1) and (k==-1) and (l!=-1)): #meaning we found "ns"
			new_time = (10**-3) * float(old_time[0:l-1])
		elif((i!=-1) and (j==-1) and (k!=-1) and (l==-1)): #meaning we found "us"
			new_time = (10**0) * float(old_time[0:k-1])
		elif((i!=-1) and (j!=-1) and (k==-1) and (l==-1)): #meaning we found "ms"
			new_time = (10**3) * float(old_time[0:k-1])
		elif((i!=-1) and (j==-1) and (k==-1) and (l==-1)): #meaning we found "s"
			new_time = (10**6) * float(old_time[0:k-1])
		else:
			print "valid timebase given not found in source data"
			print "please examine source data for correct timebase"
			sys.exit(2)
		if (verbose):
			print old_time
			print new_time
		new_row = row
		new_row[num_columns-1] = new_time
		writer.writerow(new_row)
		
	
	print "done writing out normalized file"
	ifile.close()
	ofile.close()
	sys.exit()
	

if __name__ == "__main__":
    main()








