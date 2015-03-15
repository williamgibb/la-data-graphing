# Introduction #

Design notes for the logic behind the actual data plotting script, plot\_data.py.

# Details #

This script has a few assumptions and requirements.

Requirements: matplotlib and numpy to be installed.

Assumption:
Data visualized by this script is a csv file containing binary data in the first 1 through n-1 columns, and the last column contains time data.

It is also assumed that this data has been processed by compress\_data.py.  This prepares data to be graphed in a piecewise fashion.

Testing and development is being done with Windows XP using the python 2.7 release available www.python.com.



  * Text in **bold** or _italic_
  * Headings, paragraphs, and lists
  * Automatic links to other wiki pages