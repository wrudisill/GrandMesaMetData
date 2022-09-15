# Grand Mesa Meteorological Data Processing Notes 
Author: William Rudisill
Date 9/7/22


## Background
This collection of scripts are used to process NASA "Snowex" (https://snow.nasa.gov/campaigns/snowex) meteorological data collected during 2017-2020 field campaigns in Grand Mesa, Colorado. The "raw" data is in 10 minute format. These scripts clean and process data to a 1-hour frequency and correct/fix/remove anomalous values. The variables include radiation (4-component, short and long), temperature, relative humidity, pressure, snow-depth, soil-moisture, wind speed and wind direction.


## Data Variables 
The following data variables are targetted. Raw data comes at a 10 minute sampling frequency. "Level 3" products have hourly frequency. Users who desire sub-hourly data should work with the raw files and can use the scripts presented here to assist with this. 

Meteorological Variables
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

Soil Variables:
1. SM_5cm_Avg: Soil moisture at 5cm depth (volumetric)
2. SM_20cm_Avg: Soil moisture at 20cm depth (volumetric)
3. SM_50cm_Avg: Soil moisture at 50cm depth (volumetric)
4. TC_5cm_Avg: Soil temperature at 5cm depth  (degC)
5. TC_20cm_Avg: Soil temperature at 20cm depth (degC)
6. TC_50cm_Avg: Soil temperature at 50cm depth (degC)

Snow Variables:
1. SnowDepthFiltered(m): Depth of snowpack on the ground with periods of no-snow filtered out
2. SnowDepthUnFiltered(m): Depth of snowpack on the grounh, no filtering of snow free periods.

## Purpose and Methods

1. Convert .dat files from campbell logger to .csv files that are easily parsable by python “Pandas” library. The script "process_data_initial.py" was used to do this and the comments therein describe some of the steps. Bascially the only required steps were to fix some of slightly off formatting/additional quotation marks in the raw ".dat" files 
3. Clean 10-minute data to look for periods of suspect data quality 
   * Identify number of 1) missing and 2) duplicated timesteps
   * If a timestep is duplicated, keep the first one and discard the rest  
   * If a timestep is missing, fill with NaNs
4. Linearly interpolate between good and missing values IF there is less than a 3-hour gap. Otherwise leave values as NaN. This is performed using the pandas.interpolate function
https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.interpolate.html
4. Manually fix remove anomalies that remain. There are only a few, and the list of conditions where manual corrections are applied can be found in the write_final_files.py code. 
5. Resample the 10-minute data to an hourly frequency 
   * This is performed using the pandas.resample function
   * A mean filter is used to perform the resampling 
   * Wind direction (cirular quantity) is appropriately dealt with for both interpolation and the resampling 
   * https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.resample.html	

## Additional Methods/Special Cases
1. Longwave radiation at site MM (mes middle) was corrected for in the "look_at_bad_lw_site_mm" file. There was a period of too-high values interspersed throughout good data. To preserve good data, a filtering method is applied. The details are in the look_at_bad_lw_site_mm.py file.  It includes looking at the standard deviation of the 10minue intervals and applying several rule based filters. 

2. Snow depth is calculated for all stations using the "snow_depth_fixer.py" script. The sensor records distance-to-ground using an ultrasonic sound wave reflection. The distance is corrected to account for temperature (following manufacturer instructions). Returns can occur due to blowing snow and other factors -- these have been filtered as best as possible. To do so, timesteps with high standard deviations (10-minute window) are removed. An automated method is used to determine the ground surface (the maxium, weekly median for each October-October period). There is some ambiguity as vegetation growth/change and station subsidence can impact the maximum depth from sensor to ground. Snow free periods are identified using a rule based method, combining time of year and temperature measurements to identify no-snow periods. There is still some ambiguity on the start/end of the season, so the unfiltered snow-depth product is also included. Users should take care when interpreting snow depth and the beginning/ends of the accumulation/ablation seasons, respectively. 


## General Notes
1. In the raw data, in some instances the data logger does not report data at every 10 minute interval, so each data point can be “sandwiched” by NaN values. In this case a plotting library (such as python matplotlib…) may not plot lines through these data points by default, making it look like large chunks of data are missing 

2. There are some additional quotation marks in the “NaN” string in the .dat files. This can cause a headache potentially when reading the data. Applying the pandas “.to_numeric” method with the “coerce=True” simply converts any string character to NaN. 

3. The raw data contains some unrealistically low values for barometric pressure for some of the sites (~400 hPa). A value of ~700 hPa is more correct for the elevation (~10k feet). Also the Mesa Middle (mm) and Mesa West (mw) sites report pressure values incorrectly. They have been ommitted from the dataset. 

4. There are several notable data gaps. They are generally consistent for all of the variables, but not always. 

5. The downward facing and upward facing radiation measurements may cause some confusion. The "Dn" (down) and "Up" (upward) shorthand refers t the direction that the radiometer/pyrgeometer is facing. So a downward facing radiometer is actually measuring the radiation reflected/emitted from the ground (i.e., ground --> atmosphere). 

6. The snow depth data contains non-zero values that are likely a combination of vegetation and other phenomena during the spring/summer, after snowmelt. This can/should be accounted for by the user (masking by air temperature, for example). A temperature correction has been applied to correct the sonic depth measurement using the average (10 minute) air temperature at the 10ft level. The formula is provided in the Campbell documentation. Still, care should be taken if interpreting sub-daily snow depth patterns/trends as temperature fluctuations impact this. 


