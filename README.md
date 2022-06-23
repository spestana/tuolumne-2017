# tuolumne-2017

This repo started off for analysis of satellite imagery of the Tuolumne river basin in California and Grand Mesa in Colorado, as part of SnowEx 2017 research. Now I am using this repo to stash useful info for myself, particularly about using MODIS imagery.

Jupyter notebooks and python scripts for data-wrangling, and analysis of remote sensing datasets. Focused on surface temperatures in the Tuolumne River Basin in California and Grand Mesa in Colorado in 2017.

---

### Environment setup:

Create environment from [environment.yml](https://github.com/spestana/tuolumne-2017/blob/master/environment.yml) file:

```conda env create -f environment.yml```

Or from scratch (if needed):

```conda create -n modisenv```

```conda activate modisenv```

```conda install -c conda-forge gdal xarray netcdf4 ```

```conda install -c anaconda scipy```

---

### Download MODIS products from NASA Earthdata:

 - Using [NASA Earthdata Search](https://search.earthdata.nasa.gov/), search for **MxD03**, **MxD021KM**, or **MxD11_L2** products for the location and time range of interest (replace the "x" in the product name with "O" for MODIS/Terra and "Y" for MODIS/Aqua).
 - Select the "Direct Download" option and use one of the two options (this requires an Eartdata account):
   - Click **"View/Download Data Links"**, then "Download Links File" and save in the directory you'd like to download the MODIS products into.
     - Run wget to retrieve files in this list: ```wget --http-user=YOUR_USERNAME --ask-password --keep-session-cookies --auth-no-challenge=on -c -i download.txt``` (**NOTE:** see [this thread](https://oceancolor.gsfc.nasa.gov/forum/oceancolor/topic_show.pl?tid=11490) about recent wget issues and the --auth-no-challenge=on flag)
   - If you've used AppEEARS and have a download links file (as of June 2022):
     - Use curl to get an authentication token from the [Earthdata API](https://appeears.earthdatacloud.nasa.gov/api/#authentication): ```curl --request POST --user USERNAME --header "Content-Length: 0" "https://appeears.earthdatacloud.nasa.gov/api/login"```
     - Then run wget to retrieve files in this list: ```wget --header "Authorization: Bearer TOKEN" -i download-list.txt``` ([see more info here](https://forum.earthdata.nasa.gov/viewtopic.php?t=3052)) 
   - ~~Click **"Download Access Script"** and save the shell script within the directory you'd like to download the MODIS products into.~~ (**NOTE:** I've been having issues with these scripts, maybe a change in Earthdata authentication?)
     - ~~Change file permissions with chmod to allow execution: ```chmod 777 download.sh```~~
     - ~~Run the script: ```./download.sh``` (This requires that you sign in to your Earthdata account; **NOTE:** it is probably best to run this in a terminal multiplexer like [tmux](https://en.wikipedia.org/wiki/Tmux), or in the background)~~

---

### modis_lst_hdf2nc.py

Creates a NetCDF file from a collection of MODIS observations, stacking along the time axis, and aligning each observation by pixel/line.

Input datasets (HDF format):
 - **MxD11_L2** (MODIS [Aqua](https://lpdaac.usgs.gov/products/myd11_l2v006/) and [Terra](https://lpdaac.usgs.gov/products/mod11_l2v006/) *Land Surface Temperature/Emissivity 5-Minute L2 Swath 1 km*)
 - **MxD03** (MODIS [Aqua](https://modaps.modaps.eosdis.nasa.gov/services/about/products/c6/MYD03.html) and [Terra](https://modaps.modaps.eosdis.nasa.gov/services/about/products/c6/MOD03.html) *Geolocation Fields 5-Min L1A Swath 1km*
 
#### Usage:

```python modis_lst_hdf2nc.py -l <MxD11_L2 DIRECTORY> -g <MxD03 DIRECTORY>```

---
 
 ### modis_lst_nc2pkl.py
 
 Creates a time series of MODIS LST observations for a single point, and outputs it as a pickle file (.pkl), from a NetCDF packaged collection of MODIS observations.
 
Input datasets (NetCDF format):
 - NetCDF file of **MxD11_L2**/**MxD03** derived LST and Viewangle subdatasets (produced by *modis_lst_hdf2nc.py*)
 
#### Usage:

```python modis_lst_nc2pkl.py -i <INPUT NETCDF FILE> -l <LAT> <LON>```

---
