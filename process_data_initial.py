import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import pathlib as pl


## README -- the purpose of this script is to fix some weird formatting that was
## in some, but not all, of the original .dat files
## there were extra commas at the beginning of some lines, which messed up 
## reading the data into pandas. i ran this script one-at-a time to 
## fix the files that had this issue 


raw_base = pl.Path("/Volumes/Transcend/snowex_raw_met_data/raw/10minute")
processed_base = pl.Path("/Volumes/Transcend/snowex_raw_met_data/partially_processed")

list_of_newlines = []

#dfile = raw_base.joinpath("ME_Table1.dat")
#dfile = raw_base.joinpath("MM_Table1.dat")
#dfile = raw_base.joinpath("GMSP2_Table1.dat")
dfile = raw_base.joinpath("MW_Table1.dat")


# you have to specify the encoding when opening
# some of the files might have been utf-8 for some reason...
# again i did this one file at a time since they were not all consistent 
with open(dfile, encoding='utf-16') as f:
    # loop through each line of the file and only keep the first to second to last lines
    for i in f:
    	list_of_newlines.append(i[1:-2])

# open up a new file and write the corrected lines there 
with open(processed_base.joinpath(dfile.name), encoding='utf-16', mode='w') as f:
    for i in list_of_newlines:
    	f.write(i)
        # this is the newline character 
    	f.write("\n")


print("done with dfile")

#df = pd.read_csv(processed_base.joinpath("GMSP2_Table1.txt"), encoding = 'utf-16', sep=',', skiprows=1)

#df = pd.read_csv(processed_base.joinpath(dfile.name), encoding='utf-16', skiprows=3)

df = pd.read_csv(processed_base.joinpath(dfile.name), encoding='utf-16', skiprows=4)
