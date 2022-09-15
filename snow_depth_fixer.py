import matplotlib.pyplot as plt
import pandas as pd
import pathlib as pl
import numpy as np
import datetime
import sys


def corr_dist(distance, temperature):
	# temperature must be in celcius
	return np.sqrt((temperature + 273.15)/273.15)



def wy(dt):
	if dt.month in [10,11,12]:
		wy = dt.year + 1
	else:
		wy = dt.year
	return wy


def snow_depth_fixer(data):

	#data = "MM_Table1_pandas_ready.csv"

	# this is the base data path...
	processed_base = pl.Path("/Volumes/Transcend/snowex_raw_met_data/pandas_ready")

	# these are the vars that we want...
	snow_vars = ["TCDT", "TCDT_Avg", "TCDT_Max", "TCDT_Min", "TCDT_Std", "AirTC_10ft_Avg", "IRsensor_nadir1_C_Avg"]

	# open up the dataframe...
	df = pd.read_csv(processed_base.joinpath(data))
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
	the_right_dates     = pd.date_range(dfsd.index[0], dfsd.index[-1], freq='10min')

	# reindex. fill with nans where missing
	dfsd = dfsd.reindex(the_right_dates)

	# # convert things to numeirc...
	dfsd = dfsd.apply(pd.to_numeric, errors='coerce')

	# apply the temp correction
	dfsd['TCDT_Avg'] = dfsd['TCDT_Avg'] * corr_dist(dfsd['TCDT_Avg'], dfsd['AirTC_10ft_Avg']).interpolate()


	# get the differential
	sdavg_diff = dfsd.TCDT_Avg.diff()

	# remove the big jums. 10min change cant be less than/greather than .15 m
	dfsd = dfsd.where(abs(sdavg_diff) < .15)

	# now do a std. dev filtering
	dfsd = dfsd.where(dfsd.TCDT_Std < .04)

	# remove values taht are close to zero, this messes up things down the road
	tol = .001 #1mm
	dfsd = dfsd.where(dfsd.TCDT_Avg > tol)

	# add a water year column to the data
	dfsd['wy'] = [wy(x) for x in dfsd.index]

	# find the location of the maximum
	max_date_list = []
	max_list      = []


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
	max_gap = 6*24*3

	# loop through all of the vaiables them..
	SnowDepth_interp[gaps['SnowDepth']>max_gap] = np.NaN







	dfsd['doy'] =  dfsd.index.dayofyear
	dfsd['no_snow'] = [1]*len(dfsd)

	# filter 1 n
	id1 = (dfsd.doy > 182) & (dfsd.doy <=259)

	# filter 2 -- the IR sensor is messed up for mesa east
	if data == "ME_Table1_pandas_ready.csv":
		tair = dfsd.AirTC_10ft_Avg
		tair_smooth = tair.resample("2w").mean()
		tair_smooth_bfill = tair_smooth.resample("10min").bfill()
		tair_smooth_bfill_re = tair_smooth_bfill.reindex(pd.date_range(dfsd.index[0], dfsd.index[-1], freq='10min'))

		# this has been chosen based on comparing the temperature and the snow depth data.
		id2 = tair_smooth_bfill_re >  13.

	# it works well for the other stations and can be used to filter out periods where
	# the ground is particularly warm (unlitkley to have snow)
	else:
		# do some filtering for now snow
		# filter the IR temp
		tir = dfsd.IRsensor_nadir1_C_Avg.where(dfsd.IRsensor_nadir1_C_Avg > -20).interpolate()
		tir_smooth = tir.resample("2w").mean()
		tir_smooth_bfill = tir_smooth.resample("10min").bfill()
		tir_smooth_bfill_re = tir_smooth_bfill.reindex(pd.date_range(dfsd.index[0], dfsd.index[-1], freq='10min'))
		id2 = tir_smooth_bfill_re > 10.

	dfsd['no_snow'] = dfsd['no_snow'].where(id1 | id2)
	dfsd['SnowDepth'] = SnowDepth_interp
	dfsd['SnowDepthFilt'] = SnowDepth_interp.where(dfsd.no_snow.isna())
	return dfsd

if __name__ == "__main__":

	datalist  = ["LSOS_Table1_pandas_ready.csv",
	             "MM_Table1_pandas_ready.csv",
	             "ME_Table1_pandas_ready.csv",
	             "GMSP2_Table1_pandas_ready.csv",
	             "MW_Table1_pandas_ready.csv"]


	for data in datalist:
		dfsd = snow_depth_fixer(data)

		fig,ax = plt.subplots()
		ax.plot(dfsd.index, dfsd.SnowDepth)
		ax.plot(dfsd.index, dfsd.SnowDepthFilt)
		plt.show()


#dfsd['no_snow'] = dfsd.no_snow.where(dfsd.TIR)


# idx2 = Tir > 10 & ~isnan(DEPTH_filtered_nosnow);
# idx3 = DEPTH_filtered_nosnow < 0;
# idx_NoSnow = idx1 | idx2 | idx3;
# DEPTH_filtered_nosnow(idx_NoSnow) = 0;



# now resample the data...
# hrly_sd = SnowDepth_interp.resample("1h").mean()


# dfog =pd.read_csv("snowex_raw_met_data/first_pass_data/pandas_ready/MM_Table1_pandas_happy.dat")
# dfog =dfog.set_index(dfog.TIMESTAMP)
# dfog.index = pd.to_datetime(dfog.index)
# dfog = dfog[snow_vars]
# dfog = dfog.apply(pd.to_numeric, errors="coerce")





