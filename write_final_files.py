import matplotlib.pyplot as plt
import pandas as pd
import pathlib as pl
import numpy as np
from datetime import timedelta
import sys


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


	# reindex the data... this will ardd nans to spots where there is no data
	dfmet = dfmet.reindex(the_right_dates)

	# make the data numeric...
	dfmet = dfmet.apply(pd.to_numeric, errors='coerce')


	# interpolate the data linearly
	# later we will remove the values that have too-long of gaps
	dfmet_interp = dfmet.interpolate()

	# get the number of consecutive gaps in the data
	# a bit ugly
	# each col/row says the number of consectuve NA values for that variable
	dmetnull = dfmet.isnull()
	gaps = dmetnull.ne(dmetnull.shift()).cumsum().apply(lambda x: x.map(x.value_counts())).where(dmetnull)

	outname = "_".join(data.split("_")[0:2]) + "smois"

	dfmet_interp.plot()
	plt.savefig(outname)


	# this is the maximum spacing that's allowed...
	# max_gap = 18

	# # loop through all of the vaiables them..
	# for var in dfmet.columns:
	# 	print("%s: the maximum number of sequential timesteps missing is... %s"%(var, gaps[var].max()))
	# 	dfmet_interp[var][gaps[var]>max_gap] = np.NaN

	# # fill value = -9999
	# output_file = dfmet_interp.resample("1h").median()


	# # now save it
	# outname = "_".join(data.split("_")[0:2]) + "_final_output.csv"
	# output_file.to_csv(outname, index_label='TIMESTAMP')







