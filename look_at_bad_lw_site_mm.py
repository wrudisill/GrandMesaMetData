import matplotlib.pyplot as plt
import pandas as pd
import pathlib as pl
import numpy as np

processed_base = pl.Path("/Volumes/Transcend/snowex_raw_met_data/pandas_ready")

# datalist  = ["LSOS_Table1_pandas_happy.dat",
#              "MM_Table1_pandas_happy.dat",
#              "ME_Table1_pandas_happy.dat",
#              "GMSP2_Table1_pandas_happy.dat",
#              "MW_Table1_pandas_happy.dat"]


data = "MM_Table1_pandas_happy.dat"



# open up the dataframe...
df = pd.read_csv(processed_base.joinpath(data)).iloc[:,1:]
df.TIMESTAMP = pd.to_datetime(df.TIMESTAMP)
df = df.set_index("TIMESTAMP")

# list of some vars....
met_vars  = ["LDnCo", "LDnCo_Avg", "LDnCo_Max", "LDnCo_Std", "LDnCo_Min"]

# get just the met vars
dfmet = df[met_vars].loc["2018-09-01":"2019-07-01"]
#dfmet = df[met_vars]

# convert things to numeirc...
dfmet = dfmet.apply(pd.to_numeric, errors='coerce')


# start filtering
lw = dfmet.LDnCo_Avg
lwf = lw.where(lw<600.).where(lw>-600.)
lwdiff = lwf.diff()

# remove values where there is a greater than 50 w/m2 change in 10 minutes
lwf = lwf.where(abs(lwdiff) < 20)

# make a filter category
dfmet['filt'] = np.where(abs(dfmet.LDnCo_Avg.values) > 1000., 1, 0)

# if there are any points within 6*10 minutes of a high peak, remove that
lwf = lwf.where(dfmet['filt'].rolling(window=6).max() != 1)

# find the weekly median
lwmedian = lwf.resample("1w").median()

# filter
tol = .20 # values can be above/below 20% of the weekly median

#lwf_mfilt = lwf.where(lwf < lwmedian*(1+tol))
#lwf_mfilt = lwf_mfilt.where(lwf_mfilt > lwmedian*(1-tol))

# resample to an hour ...
#lwf.resample('1h').median().plot()
#lwf.resample('1w').median().plot()


