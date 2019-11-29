# Creates a time series pickle file from a NetCDF packaged collection of MODIS observations.

# Input datasets (NetCDF format):
# - NetCDF file of MxD11_L2/MxD03 derived LST and Viewangle subdatasets

import xarray as xr
import numpy as np
import os
import pandas as pd
import datetime as dt
import gdal
import sys, argparse

gdal.UseExceptions()

#-----------------COMMAND LINE ARGUMENTS -------------------#
# Set up argument and error handling
parser = argparse.ArgumentParser(description='Creates a NetCDF file from a collection of MODIS LST observations')
parser.add_argument('-i','--infile', required=True, help='MODIS LST NetCDF file input')
# TODO: fix output directory and filename arguments
#parser.add_argument('-o','--outdir', required=True, help='Directory to export pickle file to')
#parser.add_argument('-f','--outfile', required=False, help='Filename for output pickle')
parser.add_argument('-l','--loc', required=False, nargs=2, type=float, help='Latitude and Longitude of location to extract timeseries for')
args = parser.parse_args()

#-----------------------SET ARGUMENTS TO VARIABLES----------------------------#
infile = args.infile
lat_obs = args.loc[0]
lon_obs = args.loc[1]

#-----------------------READ IN FILE----------------------------#
# Load nc file:
print('Retrieving MODIS NetCDF dataset from: {}'.format(infile))
ds = xr.open_dataset(infile)
print(ds)
#-----------------------FIND PIXEL COORDINATES----------------------------#
print(len(ds.time))
# Get the MODIS pixel coordinates for our ground based observations from each observation
# Find coordinates corresponding to this location at each timestep of MODIS observations
coordinates = [np.unravel_index((np.abs(ds.latitude[time] - lat_obs) 
                                + np.abs(ds.longitude[time] - lon_obs)).argmin(), 
                               ds.latitude[time].shape)
               for time in range(0,len(ds.time))]
               
#-----------------------EXTRACT TIMESERIES----------------------------#               
temp=[]
datetime=[]
viewtime=[]
viewangle=[]
temp_mean=[]
temp_min=[]
temp_max=[]
# Make a separate array of pixels around our point of interest
m = 1 # for a 3x3 grid, m=1

for t in range(len(coordinates)):
    # Find LST value at the specified coordinates
    temp.append(ds.lst[t][coordinates[t]].values - 273.15)
    # Get a grid of pixel values around Gaylor Pit
    line_coord_start = np.max([coordinates[t][0]-m, 0]) # detect if we're at the edge, < 0
    line_coord_stop = np.min([coordinates[t][0]+1+m, 2030]) # detect if we're at the edge, > 2030
    pixel_coord_start = np.max([coordinates[t][1]-m, 0]) # detect if we're at the edge, < 0
    pixel_coord_stop = np.min([coordinates[t][1]+1+m, 1354]) # detect if we're at the edge, >1354
    #print('trying to get pixels at: \n lines {} - {} \n pixels {} - {}'.format(line_coord_start,line_coord_stop,pixel_coord_start,pixel_coord_stop))
    
    temp_grid = ds.lst[t][line_coord_start:line_coord_stop,pixel_coord_start:pixel_coord_stop].values
    #print(temp_grid)
    temp_mean.append(np.nanmean(temp_grid) - 273.15) # Converting from K to C
    temp_min.append(np.nanmin(temp_grid) - 273.15)
    temp_max.append(np.nanmax(temp_grid) - 273.15)


    
    # Find the date and time of this observation
    datetime.append(pd.to_datetime(ds.time[t].values))
    
    # Record view time and view angle of this point
    #viewtime.append(f.View_time[coordinates].values)
    #viewangle.append(ds.viewangle[t][coordinates[t]].values)
    

d = {'datetime': datetime, 
     'temperature': temp, 
     #'viewtime': viewtime, 
     #'viewangle': viewangle,
     'temp_min': temp_min,
     'temp_max': temp_max,
     'temp_mean': temp_mean
     }
modis = pd.DataFrame(data=d)

# If we need to change the time zone of the satellite observations
hrs = -6
modis['datetime'] +=  pd.to_timedelta(hrs, unit='h')
modis = modis.sort_values('datetime').reset_index()

print(modis)
#-----------------------EXPORT TO PKL FILE----------------------------#
# Export this data:
modis.to_pickle("~/output.pkl", protocol=3)