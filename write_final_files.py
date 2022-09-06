import matplotlib.pyplot as plt
import pandas as pd
import pathlib as pl
import numpy as np
from datetime import timedelta
import sys


### This code reads the files that are written by the previous script,
### called "process_data_initial.py"


## Purpose 
## -------
##  1) remove duplicate timesteps 
##  2) add missing timesteps and fill with NA value
##  3) **interpolate between missing values**. only do this step for gaps 
##     that are less than a certain lenght. the length is a variable that 
##     that can be changed around. 
##  4) resample the data from 10 minute to hourly
##  5) write a friendly and readable csv file 

# begin
processed_base = pl.Path("/Volumes/Transcend/snowex_raw_met_data/pandas_ready")

datalist  = ["MM_Table1_pandas_happy.dat",
             "LSOS_Table1_pandas_happy.dat",
             "ME_Table1_pandas_happy.dat",
             "GMSP2_Table1_pandas_happy.dat",
             "MW_Table1_pandas_happy.dat"]


#data = "MM_Table1_pandas_happy.dat"


for data in datalist:


	# open up the dataframe...
	df = pd.read_csv(processed_base.joinpath(data), low_memory=False).iloc[:,1:]
	df.TIMESTAMP = pd.to_datetime(df.TIMESTAMP)
	df = df.set_index("TIMESTAMP")

	# get just the vars that we want..
	met_vars  = ["RH_10ft", "BP_kPa_Avg", "AirTC_20ft", "AirTC_10ft", "WSms_20ft", "WSms_10ft", "SUp_Avg", "SDn_Avg", "LUpCo_Avg", "LDnCo_Avg"]
	dfmet = df[met_vars]
	print("\n \n")
	print("~~~Begin~~~")
	print("Examining file ... %s"%data)
	print("Total # of duplicated timestamps: %s"%dfmet.index.duplicated().sum())
	print("Dropping duplicates... keeping first instance of each")

	# drop duplicates method
	#https://pandas.pydata.org/docs/reference/api/pandas.Index.drop_duplicates.html
#	dfmet = dfmet.drop_duplicates()

	# the above doesn't quite work... only works if the entire row is duplicated
	# in some cases just the time is duplicated. ugh
	dfmet = dfmet.reset_index().drop_duplicates("TIMESTAMP", keep="last").set_index("TIMESTAMP")


	# now make a list of the dates that SHOULD be in there
	the_right_dates = pd.date_range(dfmet.index[0], dfmet.index[-1], freq='10min')

	# missing dates
	missing_times = (len(the_right_dates) - len(dfmet))

	# print out how many missing times there are
	print("Total # of missing timesteps: %s"%missing_times)

	# "reindex" the data... this will add nans to spots where there is no data
	dfmet = dfmet.reindex(the_right_dates)

	# make the data numeric...
        # this is because pandas treats the data as strings in some cases
        # also converts strings of "NaN" to numpy NaN types 
	dfmet = dfmet.apply(pd.to_numeric, errors='coerce')

	# interpolate the data linearly
	# later we will remove the values that have too-long of gaps
	dfmet_interp = dfmet.interpolate()

	# get the number of consecutive gaps in the data
	# a bit ugly
	# each col/row says the number of consectuve NA values for that variable
	dmetnull = dfmet.isnull()
	gaps = dmetnull.ne(dmetnull.shift()).cumsum().apply(lambda x: x.map(x.value_counts())).where(dmetnull)

	# this is the maximum spacing that's allowed...
	# this is equivalent to 3 hrs
        max_gap = 18 
	
        # loop through all of the vaiables them..
	for var in dfmet.columns:
		print("%s: the maximum number of sequential timesteps missing is... %s"%(var, gaps[var].max()))
		dfmet_interp[var][gaps[var]>max_gap] = np.NaN

	# apply a mean filter to resample from 10min --> 1hr 
	output_file = dfmet_interp.resample("1h").mean()


	# now save it
	outname = "_".join(data.split("_")[0:2]) + "_final_output.csv"
	output_file.to_csv(outname, index_label='TIMESTAMP')







