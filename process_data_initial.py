import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import pathlib as pl



#raw_base = pl.Path("/Volumes/Transcend/snowex_raw_met_data/raw/10minute")

raw_base = pl.Path("/Volumes/Transcend/snowex_raw_met_data/NewDataAug2022")
processed_base = pl.Path("/Volumes/Transcend/snowex_raw_met_data/partially_processed")
final_processed_base = pl.Path("/Volumes/Transcend/snowex_raw_met_data/pandas_ready")

list_of_newlines = []


dfilelist = [#"ME_Table1.dat"]
  		    # "MM_Table1.dat"]
			#"GMSP2_Table1.dat"]
			 "MW_Table1.dat"]



# loop thru all of the files...
for d in dfilelist:

	### PART 1: DO INITIAL CLEANING
	dfile = raw_base.joinpath(d)

	# open up the file..
	with open(dfile, encoding='utf-16') as f:
	    for i in f:
	    	list_of_newlines.append(i[1:-2])


	# remove the file if it already exist...
	if processed_base.joinpath(dfile.name).is_file():
		processed_base.joinpath(dfile.name).unlink()


	 # this writes out a corrected one
	with open(processed_base.joinpath(dfile.name), encoding='utf-16', mode='w') as f:
	    for i in list_of_newlines:
	    	f.write(i)
	    	f.write("\n")

	#### PART 2: NOW MAKE IT PANDAS FRIENDLY ###

	cnames = pd.read_csv(processed_base.joinpath(dfile.name), encoding='utf-16', skiprows=0, nrows=1).columns
#	cnames = pd.read_csv(processed_base.joinpath(dfile.name), encoding='utf-16', skiprows=1, nrows=1).columns

	# make a new list for the corrected column names
	cnames_corr = []

	# this fixes some of the weird quotes
	for c in cnames:
	    if c[-2:] == '""':
	        cnames_corr.append(c[:-2])
	    else:
	        cnames_corr.append(c)

	# make the dataframe
	df = pd.read_csv(processed_base.joinpath(dfile.name), encoding='utf-16', skiprows=4)
	df.columns = cnames_corr

	dfix=[]
	for d in df.TIMESTAMP:
	    if str(d)[-1] == '"':
	        dfix.append(str(d)[:-1])
	    else:
	        dfix.append(str(d))


	df.TIMESTAMP = pd.to_datetime(dfix, errors="coerce")
	df = df.set_index("TIMESTAMP")
	df = df.sort_index()
	df = df[~df.index.isna()] # we get some spots where there are NaTs...drop the not times


	outname = final_processed_base.joinpath(dfile.name.split(".")[0] + "_pandas_ready.csv")

	# save the csv
	df.to_csv(outname)



### LOOK AT THE ORIGINAL DATA...

