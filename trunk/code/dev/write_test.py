# Let's create a file and write it to disk.
filename = "test.dat"
# Let's create some data:
done = 0
namelist = []
while done < 10:
    name = raw_input("Enter a name:")
    if type(name) == type(""):
        namelist.append(name)
        done = done + 1
    else:
        break
    
# Create a file object:
# in "write" mode
FILE = open(filename,"w")

# Write all the lines at once:
#FILE.writelines(namelist)
    
# Alternatively write them one by one:
for name in namelist:
    FILE.write(name)
    
FILE.close()
