import matplotlib.pyplot as plt
import pandas as pd
import pathlib as pl
import numpy as np
from datetime import timedelta
import sys

# import some functions fomr scripts in the same directory that we're runnign things in
# look at the fix_mm_lw.py script for this function
from fix_mm_lw import fix_mm_lw, circular_mean
from snow_depth_fixer import snow_depth_fixer


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

#datalist = ["GMSP1_Table1_pandas_happy.dat"]

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
    met_vars  = ["RH_10ft", "RH_20ft", "BP_kPa_Avg",
                 "AirTC_20ft", "AirTC_10ft",
                 "WSms_20ft", "WSms_10ft",
                 "WindDir_10ft_SD1_WVT", "WindDir_20ft_SD1_WVT",
                 "SUp_Avg", "SDn_Avg",
                 "LUpCo_Avg", "LDnCo_Avg",
                 "SM_5cm_Avg", "SM_20cm_Avg", "SM_50cm_Avg"]


    dfmet = df[met_vars]
    print("\n \n")
    print("~~~Begin~~~")
    print("Examining file ... %s"%data)
    print("Total # of duplicated timestamps: %s"%dfmet.index.duplicated().sum())
    print("Dropping duplicates... keeping first instance of each")

    # drop duplicates method
    #https://pandas.pydata.org/docs/reference/api/pandas.Index.drop_duplicates.html
#   dfmet = dfmet.drop_duplicates()

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


    # correct longwave...
    if data == "MM_Table1_pandas_happy.dat":

        # correct wierd lw data
        lw_corrected = fix_mm_lw()
        dfmet['LDnCo_Avg'][lw_corrected.index] = lw_corrected



    # make new vars for the sin and cos parts of wind direction...
    dfmet["WindDir_10ft_SD1_WVT_sin"] = np.sin(np.radians(dfmet["WindDir_10ft_SD1_WVT"]))
    dfmet["WindDir_10ft_SD1_WVT_cos"] = np.cos(np.radians(dfmet["WindDir_10ft_SD1_WVT"]))
    dfmet["WindDir_20ft_SD1_WVT_sin"] = np.sin(np.radians(dfmet["WindDir_20ft_SD1_WVT"]))
    dfmet["WindDir_20ft_SD1_WVT_cos"] = np.cos(np.radians(dfmet["WindDir_20ft_SD1_WVT"]))

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
    max_gap = 12

    # loop through all of the vaiables them..
    for var in dfmet.columns:
        print("%s: the maximum number of sequential timesteps missing is... %s"%(var, gaps[var].max()))
        dfmet_interp[var][gaps[var]>max_gap] = np.NaN


    # get the variables that we apply the normal mean to...
    #dfmet_regvars = dfmet[[x for x in dfmet.columns if x not in  ["WindDir_20ft_SD1_WVT", "WindDir_10ft_SD1_WVT"]]]

    # apply a mean filter to resample from 10min --> 1hr
    output_file = dfmet.resample("1h").mean()
    output_file["WindDir_10ft_SD1_WVT"] = np.degrees(np.arctan2(output_file["WindDir_10ft_SD1_WVT_sin"],
                                                                output_file["WindDir_10ft_SD1_WVT_cos"]))

    output_file["WindDir_20ft_SD1_WVT"] = np.degrees(np.arctan2(output_file["WindDir_20ft_SD1_WVT_sin"],
                                                                output_file["WindDir_20ft_SD1_WVT_cos"]))

    output_file =  output_file.drop(["WindDir_20ft_SD1_WVT_sin",
                                     "WindDir_20ft_SD1_WVT_cos",
                                     "WindDir_10ft_SD1_WVT_sin",
                                     "WindDir_10ft_SD1_WVT_cos"], axis=1)
    # this isnot quite correct. we must apply a circular mean function to the wind dir


    # DO THE SNOWDEPTH CALCULATION #
    snow_depth = snow_depth_fixer(data)
    output_file['SnowDepth(m)'] = snow_depth


    ####################################
    # APPLY SITE SPECIFIC FUNCTIONS HERE
    ####################################

    # Mesa Middle Corrections
    if data == "MM_Table1_pandas_happy.dat":

        # remove one anomalous pressure spike
        output_file.BP_kPa_Avg.loc["2020-10-06 22:00" : "2020-10-06 23:00"] = np.nan

    # Mesa East Corrections
    if data == "ME_Table1_pandas_happy.dat":
        # persistent pressure drop off
        output_file['BP_kPa_Avg'].loc['2021-12-11':] = np.nan

    # Mesa West Corrections
    if data == "MW_Table1_pandas_happy.dat":
        # pressure spike
        output_file.BP_kPa_Avg.loc["2020-02-25 17:00" : "2020-02-26 00:00"] = np.nan
        output_file.BP_kPa_Avg.loc["2018-04-13 20:00" : "2018-04-13 22:00"] = np.nan

    ####################################
    # END SITE SPECIFIC FUNCTIONS
    ####################################

    # now save it
    outname = "_".join(data.split("_")[0:2]) + "_final_output.csv"
    output_file.to_csv(outname, index_label='TIMESTAMP')
 #   sys.exit()






