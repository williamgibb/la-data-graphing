import numpy as np
import matplotlib.mlab as mlab
import matplotlib.pyplot as plt

file_name = "test_compress3.csv"
fh = open(file_name, "r")
r = mlab.csv2rec(fh)

num_records = len(r.dtype)
time = num_records - 1
first_column = 0

time_label = r.dtype.names[time]
sig1_label = r.dtype.names[first_column]
sig2_label = r.dtype.names[first_column+1]

x = r[time_label]
y1 = r[sig1_label]
y2 = r[sig2_label]

sig_label_x = -0.075
sig_label_y	= 0.75
label_size = 14

#plt.plot(x,y)
#plt.show()


plt.rc('axes', grid=True)
plt.rc('grid', color='0.75', linestyle='-', linewidth=0.5)

fillcolor = 'darkgoldenrod'


#left, width = 0.1, 0.8
#rect1 = [left, 0.7, width, 0.2]
#rect2 = [left, 0.3, width, 0.4]

n = num_records

left, width = 0.1, 0.8
#bottom, height = .25, .5
rect1 = [left, 0.55, width, 0.2]
rect2 = [left, 0.05, width, 0.4]


fig = plt.figure(facecolor='white')
axescolor  = '#f6f6f6'  # the axies background color

ax1 = fig.add_axes(rect1, axisbg=axescolor)  #left, bottom, width, height
ax2 = fig.add_axes(rect2, axisbg=axescolor, sharex=ax1)

#plot on ax1

ax1.plot (x,y1)

#ax1.axhline(1, color=fillcolor)
#ax1.axhline(0, color=fillcolor)

ax1.set_ylim(-0.1, 1.1)
ax1.set_yticks([0,1])

ax1.text(sig_label_x, sig_label_y, sig1_label, va='top', 
	transform=ax1.transAxes, fontsize=label_size)

ax1.set_title('%s signals'%file_name)
######## plot signal2
ax2.plot (x,y2)

ax2.axhline(1, color=fillcolor)
ax2.axhline(0, color=fillcolor)

ax2.set_ylim(-0.1, 1.1)
ax2.set_yticks([0,1])

ax2.text(sig_label_x, sig_label_y, sig2_label, va='top', 
	transform=ax2.transAxes, fontsize=label_size)


plt.show()


