# GrandMesaMetData

## Grand Mesa Meteorological Data Processing Notes 
## Author: Will Rudisill
## Date 9/7/22

## General Notes
1. In the raw data, in some instances the data logger does not report data at every 10 minute interval, so each data point can be “sandwiched” by NaN values. In this case a plotting library (such as python matplotlib…) may not plot lines through these data points by default, making it look like large chunks of data are missing 

2. There are some additional quotation marks in the “NaN” string in the .dat files. This can cause a headache potentially when reading the data. Applying the pandas “.to_numeric” method with the “coerce=True” simply converts any string character to NaN. 

## Data Variables 
The following data variables are targetted. Raw data comes at a 10 minute sampling frequency. Level (XX) products have hourly frequency. Users who desire sub-hourly data should work with the raw files and can use the scripts presented here to assist with this. 

1. Average AirTC_10ft (oC): Campbell HC253 Air Temperature, 10ft tower level
2. Average AirTC_20ft (oC): Campbell HC253 Air Temperature, 20ft tower level
3. Sample RH_10ft (oC): Campbell HC253 Relative Humidity, 10ft tower level
4. Sample RH_20ft (oC): Campbell HC253 Relative Humidity, 20ft tower level
5. WSms_10ft_S_WVT (m/s): RM Young 05103 unit vector mean wind speed, 10ft level
6. WSms_20ft_S_WVT (m/s): RM Young 05103 unit vector mean wind speed, 20ft level
7. WindDir_10ft_D1_WVT (deg): RMY05103 unit vector mean wind direction, 10ft
8. WindDir_20ft_D1_WVT (deg): RMY05103 unit vector mean wind direction, 20ft
9. Average BP_kPa_Avg (kPa): Campbell Scientific CS106 Barometric Pressure
10. Average SUp_Avg (Wm-2): CNR4 Pyranometer up facing (shortwave radiation)
11. Average SDn_Avg (Wm-2): CNR4 Pyranometer down facing (shortwave radiation)
12. Average LUpCo_Avg (Wm-2): CNR4 Temperature corrected pyrgeometer up facing
13. Average LDnCo_Avg (Wm-2): CNR4 Temperature corrected pyrgeometer down facing


## Methods

1. Convert .dat files from campbell logger to .csv files that are easily parsable by python “Pandas” library.
2. Clean 10-minute data
3. Identify number of 1) missing and 2) duplicated timesteps
   * If a timestep is duplicated, keep the first one and discard the rest  
   * If a timestep is missing, fill with NaNs
   * Linearly interpolate between good and missing values IF there is less than a 3-hour gap. Otherwise leave values as NaN. This is performed using the pandas.interpolate function
https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.interpolate.html
4. Resample the 10-minute data to an hourly frequency 
   * This is performed using the pandas.resample function
   * A mean filter is used to perform the resampling 
   * https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.resample.html	
5. Manually fix remove anomalies

