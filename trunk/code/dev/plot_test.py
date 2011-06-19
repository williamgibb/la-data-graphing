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
#plt.plot(x,y)
#plt.show()


plt.rc('axes', grid=True)
plt.rc('grid', color='0.75', linestyle='-', linewidth=0.5)

fillcolor = 'darkgoldenrod'

textsize = 9
left, width = 0.1, 0.8
rect1 = [left, 0.7, width, 0.2]
rect2 = [left, 0.3, width, 0.4]


fig = plt.figure(facecolor='white')
axescolor  = '#f6f6f6'  # the axies background color

ax1 = fig.add_axes(rect1, axisbg=axescolor)  #left, bottom, width, height
ax2 = fig.add_axes(rect2, axisbg=axescolor, sharex=ax1)

#plot on ax1

ax1.plot (x,y1)

ax1.axhline(1, color=fillcolor)
ax1.axhline(0, color=fillcolor)

ax1.set_ylim(-0.1, 1.1)
ax1.set_yticks([0,1])

ax1.text(0.025, 0.95, 'RSI (14)', va='top', transform=ax1.transAxes, fontsize=textsize)
ax1.set_title('%s signals'%file_name)


plt.show()


