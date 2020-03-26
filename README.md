# tuolumne-2017

Jupyter notebooks and python scripts for data-wrangling, and analysis of remote sensing datasets. Focused on surface temperatures in the Tuolumne River Basin in California and Grand Mesa in Colorado in 2017.

---

### Download MODIS products from NASA Earthdata

 - Using [NASA Earthdata Search](https://search.earthdata.nasa.gov/), search for **MxD03**, **MxD021KM**, or **MxD11_L2** products for the location and time range of interest (replace the "x" in the product name with "O" for MODIS/Terra and "Y" for MODIS/Aqua).
 - Select the "Direct Download" option and use one of the two options (this requires an Eartdata account):
   - Click **"View/Download Data Links"**, then "Download Links File" and save in the directory you'd like to download the MODIS products into (**NOTE:** this option has worked best for me).
     - Run wget to retrieve files in this list: ```wget -i download.txt```
   - Click **"Download Access Script"** and save the shell script within the directory you'd like to download the MODIS products into.
     - Change file permissions with chmod to allow execution: ```chmod 777 download.sh```
     - Run the script: ```./download.sh``` (This requires that you sign in to your Earthdata account; **NOTE:** it is probably best to run this in a terminal multiplexer like [tmux](https://en.wikipedia.org/wiki/Tmux), or in the background)

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
---

### environment setup from scratch (if needed):
```conda create -n modisenv```

```conda install -c conda-forge gdal xarray netcdf4 ```

```conda install -c anaconda scipy```