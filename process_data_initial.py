import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import pathlib as pl



raw_base = pl.Path("/Volumes/Transcend/snowex_raw_met_data/raw/10minute")
processed_base = pl.Path("/Volumes/Transcend/snowex_raw_met_data/partially_processed")

list_of_newlines = []

#dfile = raw_base.joinpath("ME_Table1.dat")
#dfile = raw_base.joinpath("MM_Table1.dat")
#dfile = raw_base.joinpath("GMSP2_Table1.dat")
dfile = raw_base.joinpath("MW_Table1.dat")

with open(dfile, encoding='utf-16') as f:
    for i in f:
    	list_of_newlines.append(i[1:-2])


with open(processed_base.joinpath(dfile.name), encoding='utf-16', mode='w') as f:
    for i in list_of_newlines:
    	f.write(i)
    	f.write("\n")


print("done with dfile")

#df = pd.read_csv(processed_base.joinpath("GMSP2_Table1.txt"), encoding = 'utf-16', sep=',', skiprows=1)

#df = pd.read_csv(processed_base.joinpath(dfile.name), encoding='utf-16', skiprows=3)

df = pd.read_csv(processed_base.joinpath(dfile.name), encoding='utf-16', skiprows=4)