# tuolumne-2017


#### modis_lst_hdf2nc.py

Creates a NetCDF file from a collection of MODIS observations, stacking along the time axis, and aligning each observation by pixel/line.

Input datasets (HDF format):
 - **MxD11_L2** (MODIS [Aqua](https://lpdaac.usgs.gov/products/myd11_l2v006/) and [Terra](https://lpdaac.usgs.gov/products/mod11_l2v006/) *Land Surface Temperature/Emissivity 5-Minute L2 Swath 1 km*)
 - **MxD03** (MODIS [Aqua](https://modaps.modaps.eosdis.nasa.gov/services/about/products/c6/MYD03.html) and [Terra](https://modaps.modaps.eosdis.nasa.gov/services/about/products/c6/MOD03.html) *Geolocation Fields 5-Min L1A Swath 1km*
 
 #### modis_lst_nc2pkl.py
 
 Creates a time series of MODIS LST observations for a single point, and outputs it as a pickle file (.pkl), from a NetCDF packaged collection of MODIS observations.
 
Input datasets (NetCDF format):
 - NetCDF file of **MxD11_L2**/**MxD03** derived LST and Viewangle subdatasets (produced by *modis_lst_hdf2nc.py*)