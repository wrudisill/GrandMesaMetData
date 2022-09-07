# GrandMesaMetData

##Grand Mesa Meteorological Data Processing Notes 
##Author: Will Rudisill
##Date 9/7/22

##General Notes
In the raw data, in some instances the data logger does not report data at every 10 minute interval, so each data point can be “sandwiched” by NaN values. In this case a plotting library (such as python matplotlib…) may not plot lines through these data points by default, making it look like large chunks of data are missing 
There are some additional quotation marks in the “NaN” string in the .dat files. This can cause a headache potentially when reading the data. Applying the pandas “.to_numeric” method with the “coerce=True” simply converts any string character to NaN. 



##Methods

1. Convert .dat files from campbell logger to .csv files that are easily parsable by python “Pandas” library.
2. Clean 10-minute data
3. Identify number of 1) missing and 2) duplicated timesteps
   * If a timestep is duplicated, keep the first one and discard the rest  
   * If a timestep is missing, fill with NaNs
   * Linearly interpolate between good and missing values IF there is less than a 3-hour gap. Otherwise leave values as NaN. This is performed using the pandas.interpolate function
https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.interpolate.html
4. Resample the 10-minute data to an hourly frequency 
   * This is performed using the pandas.resample function
   * https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.resample.html	
5. Manually fix remove anomalies

