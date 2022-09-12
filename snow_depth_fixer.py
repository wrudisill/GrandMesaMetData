import matplotlib.pyplot as plt
import pandas as pd
import pathlib as pl
import numpy as np
import datetime


def corr_dist(distance, temperature):
	# temperature must be in celcius
	return distance*np.sqrt((temperature + 273.15)/273.15)


def wy(dt):
	if dt.month in [10,11,12]:
		wy = dt.year + 1
	else:
		wy = dt.year
	return wy




def snow_depth_fixer(data):

	# this is the base data path...
	processed_base = pl.Path("/Volumes/Transcend/snowex_raw_met_data/pandas_ready")

	# these are the vars that we want...
	snow_vars = ["TCDT", "TCDT_Avg", "TCDT_Max", "TCDT_Min", "TCDT_Std", "AirTC_10ft"]

	# open up the dataframe...
	df = pd.read_csv(processed_base.joinpath(data)).iloc[:,1:]
	df.TIMESTAMP = pd.to_datetime(df.TIMESTAMP)
	df = df.set_index("TIMESTAMP")

	# check that the vars are in fact in there...
	for c in snow_vars:
		if c not in df.columns:
			print(c + " NOT FOUND. Skipping")
			print(data)
		continue


	# get all of the vars we might need...
	dfsd = df[snow_vars]

	# remove duplicate dates
	dfsd = dfsd.reset_index().drop_duplicates("TIMESTAMP", keep="last").set_index("TIMESTAMP")

	# make the index of the correct dates
	the_right_dates       = pd.date_range(dfsd.index[0], dfsd.index[-1], freq='10min')

	# reindex. fill with nans where missing
	dfsd = dfsd.reindex(the_right_dates)

	# # convert things to numeirc...
	dfsd = dfsd.apply(pd.to_numeric, errors='coerce')

	# apply the temp correction
	dfsd['TCDT_Avg'] = corr_dist(dfsd['TCDT_Avg'], dfsd['AirTC_10ft'])

	# get the differential
	sdavg_diff = dfsd.TCDT_Avg.diff()

	# remove the big jums. 10min change cant be less than/greather than .15 m
	dfsd = dfsd.where(abs(sdavg_diff) < .15)

	# now do a std. dev filtering
	dfsd = dfsd.where(dfsd.TCDT_Std < dfsd.TCDT_Std.mean()*1.2)

	# remove values taht are close to zero, this messes up things down the road
	tol = .001 #1mm
	dfsd = dfsd.where(dfsd.TCDT_Avg > tol)

	# add a water year column to the data
	dfsd['wy'] = [wy(x) for x in dfsd.index]

	# find the location of the maximum
	max_date_list = []
	max_list      = []

	#dfsd_corrected = dfsd.TCDT_Avg.deepcopy()

	# make a new column for this
	dfsd['SnowDepth'] = None


	# go thru unique years
	for y in dfsd.wy.unique():
		# get the weekly median
		wekmed = dfsd[dfsd.wy == y].TCDT_Avg.resample("1w").median()

		# find the location of hte max depth
		max_date_list.append(wekmed.idxmax())

		# do the same for the other one
		max_list.append(wekmed.max())

		# create the depth product... still needs to be resampled, etc.
		dfsd['SnowDepth'][dfsd.wy == y] = wekmed.max() - dfsd[dfsd.wy == y].TCDT_Avg


	# remove values that are very close to, or below, zero
	tol = .001

	# remove some more points..
	SnowDepth = dfsd["SnowDepth"].where(dfsd.SnowDepth > 0)
	SnowDepth = SnowDepth.astype(float)

	# now do some gap filling ...
	SnowDepth_interp = SnowDepth.interpolate()

	# get the number of consecutive gaps in the data
	# a bit ugly
	# each col/row says the number of consectuve NA values for that variable
	dfsdnull = dfsd.isnull()
	gaps = dfsdnull.ne(dfsdnull.shift()).cumsum().apply(lambda x: x.map(x.value_counts())).where(dfsdnull)

	# this is the maximum spacing that's allowed...
	# this is equivalent to 3 hrs
	max_gap = 18

	# loop through all of the vaiables them..
	SnowDepth_interp[gaps['SnowDepth']>max_gap] = np.NaN

	# now resample the data...
	hrly_sd = SnowDepth_interp.resample("1h").mean()

	return hrly_sd


# we do thi sjust so that this code doesnt get run on import
# lets us use the above function in other scripts
if __name__ == "__main__":


	datalist  = ["MM_Table1_pandas_happy.dat",
	         "LSOS_Table1_pandas_happy.dat",
	         "ME_Table1_pandas_happy.dat",
	         "GMSP2_Table1_pandas_happy.dat",
	         "MW_Table1_pandas_happy.dat"]


	#data = "MM_Table1_pandas_happy.dat"


	for data in datalist:
		snow_depth = snow_depth_fixer(data)
		outname = "_".join(data.split("_")[0:2]) + "_snowd_plot.png"

		# make a plot
		fig,ax = plt.subplots()
		ax.plot(snow_depth.index, snow_depth)
		plt.savefig(outname)
		plt.clf()







