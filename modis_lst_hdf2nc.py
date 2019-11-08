# Creates a NetCDF file from a collection of MODIS observations.

# Input datasets (HDF format):
# - MxD11_L2 (MODIS Land Surface Temperature/Emissivity 5-Minute L2 Swath 1 km)
# - MxD03 (MODIS Geolocation Fields 5-Min L1A Swath 1km)

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
parser.add_argument('-l','--lstdir', required=True, help='Directory containing MxD11_L2 HDF files')
parser.add_argument('-g','--geodir', required=True, help='Directory containing MxD03 HDF files')
# TODO: fix output directory and filename arguments
#parser.add_argument('-o','--outdir', required=True, help='Directory to export NetCDF file to')
#parser.add_argument('-f','--outfile', required=False, help='Filename for output NetCDF')
parser.add_argument('-b','--bounds', required=False, help='Latitude and Longitude coordinates for bounding box: min_lon, max_lon, min_lat, max_lat')
args = parser.parse_args()

#-----------------------SET ARGUMENTS TO VARIABLES----------------------------#
# Check to make sure the directory inputs are valid
inDir = []
i = 0
for dir in [args.lstdir, args.geodir]: #, args.outdir]:
	if dir[-1] != '/' and dir[-1] != '\\': 
		inDir.append( dir.strip("'").strip('"') + os.sep )
	else: 
		inDir.append( dir )
	try:
		os.path.isdir(inDir[i])
	except FileNotFoundError:
		print('error: input directory provided does not exist or was not found:\n{}'.format(dir))
		sys.exit(2)
	i+=1
# Assign arguments to variables
lst_searchDir = inDir[0]
geo_searchDir = inDir[1]
#outDir = inDir[2]


#-----------------------FUNCTIONS----------------------------#
# Function to find all HDF files in a specified directory
def getListOfFiles(dirName,ext):
    '''Create a list of file names in the given directory with specified file extension.'''
    # https://thispointer.com/python-how-to-get-list-of-files-in-directory-and-sub-directories/
    listOfFile = os.listdir(dirName)
    allFiles = list()
    # Iterate over all the entries
    for entry in listOfFile:
        # Only match files with the correct extension
        if '.'+ext == os.path.splitext(entry)[1]:
            # Create full path and add to list
            fullPath = os.path.join(dirName, entry)
            allFiles.append(fullPath)       
    return allFiles


#-----------------------READ IN FILES----------------------------#
print('\n')

# Search specified directories for HDF files
lst_file_list = getListOfFiles(lst_searchDir,'hdf')
geo_file_list = getListOfFiles(geo_searchDir,'hdf')

print('Found {} LST files, {} GEO files'.format(len(lst_file_list),len(geo_file_list)))


# Open MxD11_L2 files and extract the LST, and view angle subdatasets.
lst_ds = []
viewangle_ds = []
print('Retrieving LST and Viewangle datasets from: {}'.format(lst_searchDir))
i = 1
for path in lst_file_list:
	print('{}/{}'.format(i,len(lst_file_list)), end="\r")
	try:
		lst_ds.append(gdal.Open('HDF4_EOS:EOS_SWATH:"{}":MOD_Swath_LST:LST'.format(path)))
		viewangle_ds.append(gdal.Open('HDF4_EOS:EOS_SWATH:"{}":MOD_Swath_LST:View_angle'.format(path)))
	except RuntimeError:
		break
	i = i+1
# TODO: could add option to select which SDS we want to include (right now only doing LST and view angles)

# Open MxD03 files and extract the latitude, and longitude subdatasets.
geo_lat_ds = []
geo_lon_ds = []
print('Retrieving Latitude and Longitude datasets from: {}'.format(geo_searchDir))
i = 1
for path in geo_file_list:
	print('{}/{}'.format(i,len(geo_file_list)), end="\r")
	try:
		geo_lat_ds.append(gdal.Open('HDF4_SDS:UNKNOWN:"{}":0'.format(path)))
		geo_lon_ds.append(gdal.Open('HDF4_SDS:UNKNOWN:"{}":1'.format(path)))
	except RuntimeError:
		print("Runtimeerror (while looking for lat and lon SDS")
	i = i+1



#-----------------------STACK DATA----------------------------#
# Match geolocation with LST products, stack into xarray dataset.

# Create empty arrays to stack data into.
n_files = len(lst_ds)
m_files = len(geo_lat_ds)

# Because the MODIS products are either 2030 or 2040 pixels in 5 minutes...
# I'm truncating them all to just 2030
along_track_px = 2030
cross_track_px = 1354

# LST scale factor
lst_scale_factor = 0.02
# View angle scale factor
view_scale_factor = 0.5
# TODO: alternatively, scale (and offset) factors can be pulled from HDF file metadata

# For each file in the timeseries of MODIS observations
k = 0
for i in range(0,n_files):
    # Read the date and time from the LST product
    date = lst_ds[i].GetMetadataItem('RANGEBEGINNINGDATE')
    time = lst_ds[i].GetMetadataItem('RANGEBEGINNINGTIME')
    eq_cross_time = lst_ds[i].GetMetadataItem('EQUATORCROSSINGTIME.1')
    # Find its matching MxD03 Geolocation product
    for j in range(0,m_files):
        # date_geo = geo_lat_ds[j].GetMetadataItem('RANGEBEGINNINGDATE')
        # time_geo = geo_lat_ds[j].GetMetadataItem('RANGEBEGINNINGTIME')
        eq_cross_time_geo = geo_lat_ds[j].GetMetadataItem('EQUATORCROSSINGTIME.1')
        # Once we find a match, load these into our arrays
        if eq_cross_time==eq_cross_time_geo:# and lst_ds[i].ReadAsArray() is not None:
			# TODO: use metadata item "AncillaryInputPointer" to find the corresponding geolocation product
            print('({}/{}) Found files for {} {}'.format(i,n_files,date,time), end="\r")
            # Load the LST values and scale them
            lst = lst_scale_factor * lst_ds[i].ReadAsArray()[0:along_track_px,0:cross_track_px]
            # Replace the nodata value 0, with Nans
            lst[lst==0.] = np.nan
            # Read the view angles from the LST product, scale and remove nodata values
            viewangle = viewangle_ds[i].ReadAsArray()[0:along_track_px,0:cross_track_px].astype(float)
            viewangle[viewangle==255] = np.nan
            viewangle = view_scale_factor * viewangle
            # Read the latitudes and longitudes from the geolocaiton product
            lat = geo_lat_ds[j].ReadAsArray()[0:along_track_px,0:cross_track_px]	
            lon = geo_lon_ds[j].ReadAsArray()[0:along_track_px,0:cross_track_px]
            # Add the MODIS data to an xarray dataset
            if k==0: # If this is our first file, make a new dataset
                ds = xr.Dataset({'lst': (['line', 'pixel'],  lst),
                                'viewangle': (['line', 'pixel'],  viewangle)},
                                coords={'longitude': (['line', 'pixel'], lon),
                                        'latitude': (['line', 'pixel'], lat),
                                        'time': pd.to_datetime('{} {}'.format(date,time))})
                k+=1 # add to the successful file load counter
            else: # append to existing dataset
                ds_new = xr.Dataset({'lst': (['line', 'pixel'],  lst),
                                'viewangle': (['line', 'pixel'],  viewangle)},
                                coords={'longitude': (['line', 'pixel'], lon),
                                        'latitude': (['line', 'pixel'], lat),
                                        'time': pd.to_datetime('{} {}'.format(date,time))})
                ds = xr.concat([ds,ds_new],'time') # concatenate along the time axis
                k+=1 # add to the successful file load counter
            break # go to next LST file

# Close all the original HDF files loaded
lst_ds = None
viewangle_ds = None
geo_lat_ds = None
geo_lon_ds = None

# Finally sort by time:
ds = ds.sortby(ds.time)
print('{} out of {} files loaded with geolocation information'.format(k,n_files))

# Update to the number of files we successfully loaded
n_files = ds.time.shape[0]

# TODO: allow subsetting to an area within a bounding box
#-----------------------EXPORT NETCDF----------------------------#


#-----------------------EXPORT NETCDF----------------------------#

print('Final stacked dataset:')
print(ds)

# Export this stack of MODIS observations as a new NetCDF file
#if args.outfile == None:
#	filename = 'output.nc'
#	print('Output to: {}'.format(outDir+filename))
#else:
#	filename = outfile
#	print('Output to: {}'.format(outDir+filename))
# TODO: use the output directory flag instead of this temp location
ds.to_netcdf('~/tuolumne-output.nc',mode='w')
