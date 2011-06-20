#
#	see chapter sixteen in the matplotlib docs!
#


import numpy as np
import matplotlib.mlab as mlab
import matplotlib.pyplot as plt

file_name = "test_compress3.csv"
fh = open(file_name, "r")
r = mlab.csv2rec(fh)
#numbers
num_records = len(r.dtype)
time = num_records - 1
n = time
first_column = 0
#get labels
time_label = r.dtype.names[time]
sig1_label = r.dtype.names[first_column]
sig2_label = r.dtype.names[first_column+1]
#get data
x = r[time_label]
y1 = r[sig1_label]
y2 = r[sig2_label]

sig_label_x = -0.075
sig_label_y	= 0.75
label_size = 14

plt.rc('axes', grid=True)
plt.rc('grid', color='0.75', linestyle='-', linewidth=0.5)

plt.figure(1)
#setup ax1
ax1 = plt.subplot(n,1,1)
ax1.set_ylim(-0.1, 1.1)
ax1.set_yticks([0,1])
ax1.text(sig_label_x, sig_label_y, sig1_label, va='top', 
	transform=ax1.transAxes, fontsize=label_size)
ax1.plot(x, y1)
#setup ax2
ax2=plt.subplot(n,1,2, sharex=ax1)
ax2.set_ylim(-0.1, 1.1)
ax2.set_yticks([0,1])
ax2.text(sig_label_x, sig_label_y, sig2_label, va='top', 
	transform=ax2.transAxes, fontsize=label_size)
ax2.plot(x,y2)
#title
ax1.set_title('%s signals'%file_name)
#graph
plt.show()
