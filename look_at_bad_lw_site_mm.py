
import matplotlib.pyplot as plt
import pandas as pd
import pathlib as pl
import numpy as np
import datetime

processed_base = pl.Path("/Volumes/Transcend/snowex_raw_met_data/pandas_ready")

# datalist  = ["LSOS_Table1_pandas_happy.dat",
#              "MM_Table1_pandas_happy.dat",
#              "ME_Table1_pandas_happy.dat",
#              "GMSP2_Table1_pandas_happy.dat",
#              "MW_Table1_pandas_happy.dat"]


def circular_mean(degrees):
    rads = np.radians(degrees)
    return np.degrees(np.arctan2(np.nanmean(np.sin(rads)), np.nanmean(np.cos(rads))))



def fix_mm_lw():
	data = "MM_Table1_pandas_happy.dat"

	### open up a differetn dataset

	# df2 = pd.read_csv(processed_base.joinpath("ME_Table1_pandas_happy.dat")).iloc[:,1:]
	# df2.TIMESTAMP = pd.to_datetime(df2.TIMESTAMP)
	# df2 = df2.set_index("TIMESTAMP")
	# met_vars  = ["LDnCo", "LDnCo_Avg", "LDnCo_Max", "LDnCo_Std", "LDnCo_Min"]
	# dfmet2 = df2[met_vars].loc["2018-09-01":"2019-07-01"]
	# dfmet2 = dfmet2.reset_index().drop_duplicates("TIMESTAMP", keep="last").set_index("TIMESTAMP")

	####

	# open up the dataframe...
	df = pd.read_csv(processed_base.joinpath(data)).iloc[:,1:]
	df.TIMESTAMP = pd.to_datetime(df.TIMESTAMP)
	df = df.set_index("TIMESTAMP")


	# list of some vars....
	met_vars  = ["LDnCo", "LDnCo_Avg", "LDnCo_Max", "LDnCo_Std", "LDnCo_Min"]

	# get just the met vars
	dfmet = df[met_vars].loc["2018-09-01":"2019-07-01"]

	#dfmet = df[met_vars]
	dfmet = dfmet.reset_index().drop_duplicates("TIMESTAMP", keep="last").set_index("TIMESTAMP")

	the_right_dates       = pd.date_range(dfmet.index[0], dfmet.index[-1], freq='10min')
	the_right_dates_daily = pd.date_range(dfmet.index[0], dfmet.index[-1]+datetime.timedelta(days=1), freq='1d')

	dfmet = dfmet.reindex(the_right_dates)

	# convert things to numeirc...
	dfmet = dfmet.apply(pd.to_numeric, errors='coerce')


	# start filtering
	lw = dfmet.LDnCo_Avg
	lwf = lw.where(lw<600.).where(lw>-600.)
	lwdiff = lwf.diff()

	# remove values where there is a greater than 20 w/m2 change in 10 minutes
	lwf = lwf.where(abs(lwdiff) < 20)

	# make a filter category
	dfmet['filt'] = np.where(abs(dfmet.LDnCo_Avg.values) > 1000., 1, 0)

	# if there are any points within 6*10 minutes of a high peak, remove that
	lwf = lwf.where(dfmet['filt'].rolling(window=6).max() != 1)

	# find the daily mean of the data ... there are still some outliers in here
	lwmean = lwf.resample("1d").median()

	# this is just so that we add a final day... required to match back up with the 10 min data
	lwmean = lwmean.reindex(the_right_dates_daily)

	# get the average .... standard deviation of daily longwave
	# this is one value for the entire series
	lwstd_daily = np.mean(lwf.resample("1d").std())

	# now reindex the mean to 10min again... using the "pad method"
	# and then smooth out this one on the edges
	lwmean_rsp = lwmean.resample("10min").pad().rolling(window=6*24*2).mean()[:-1]


	# final filrer... remove 10 minute timesteps that are g.t 2*std of the daily data
	lwf_filter_final = lwf.where(lwf < lwmean_rsp + 2*lwstd_daily)
	return lwf_filter_final



