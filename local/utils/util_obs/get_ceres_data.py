'''
# ------------------------
#  CERES data (radiation)
# ------------------------

'''

# == imports ==
# -- packages --
import xarray as xr
import os
import pandas as pd
import importlib
import glob
import re
import numpy as np

# -- imported scripts --
import os
import sys
sys.path.insert(0, os.getcwd())
def import_relative_module(module_name, file_path):
    ''' import module from relative path '''
    if file_path == 'utils':
        cwd = os.getcwd()
        if not os.path.isdir(os.path.join(cwd, 'utils')):
            print('put utils folder in cwd')
            print(f'current cwd: {cwd}')
            print('exiting')
            exit()
        module_path = f"utils.{module_name}"        
    else:
        cwd = os.getcwd()
        relative_path = os.path.relpath(file_path, cwd) # ensures the path is relative to cwd
        module_base = os.path.dirname(relative_path).replace("/", ".").strip(".")
        module_path = f"{module_base}.{module_name}"
    return importlib.import_module(module_path)

# == post-process ==
def process_data_further(da):
    ''' This function can be defined and given externally '''
    return da

# == pre-process ==
def pre_process(ds, process_request):
    var_name, dataset, time_period, t_freq, lon_area, lat_area, resolution = process_request
    
    # -- pick out variable --    
    da = ds

    # -- temporally resample --
    if t_freq == 'daily':
        da = da.resample(time='1d').mean()
    else:
        pass

    # -- put lon in range [0, 360] --
    da = da.rename({'longitude': 'lon', 'latitude': 'lat'})
    da = da.sortby("lat")
    da = da.assign_coords(lon=((da.lon + 360) % 360))
    da = da.sortby('lon')

    # -- select region of interest --
    da = da.sel(lon = slice(int(lon_area.split(':')[0]), int(lon_area.split(':')[1])), 
                lat = slice(int(lat_area.split(':')[0]), int(lat_area.split(':')[1]))
                )
    
    return da


# == get raw data ==
def get_data(process_request, process_data_further):
    var, dataset, time_period, t_freq, lon_area, lat_area, resolution = process_request

    # -- get file and open data --
    year1 = time_period.split(':')[0].split('-')[0]
    year2 = time_period.split(':')[1].split('-')[0]

    da_list = []
    for year in np.arange(int(year1), int(year2) + 1):
        # if year > 2001:
        #     continue
        print(f'loading year {year}')
        files = sorted(glob.glob(f'/Volumes/satellite1/work/data/CERES_data/{year}/*.nc'))
        times = [pd.to_datetime(re.search(r'\.(\d{8})\.nc', f).group(1), format='%Y%m%d') for f in files]
        da_year = xr.open_mfdataset(files, combine='nested', concat_dim='time', preprocess=lambda d: d[[var]])[var]
        da_year = da_year.assign_coords(time = times)
        da_year = da_year.load()
        da_list.append(da_year)
    da = xr.concat(da_list, dim="time")    

    # -- pre-process --
    da = pre_process(da, process_request)
    
    # -- post-process --
    da = process_data_further(da)
    return da


if __name__ == '__main__':
    # path = '/Volumes/satellite1/work/data/CERES_data/2001/CER_SYN1deg-Day_Terra-Aqua-NOAA20_Edition4B_401412.20010101.nc'
    # ds = xr.open_dataset(path)
    # print(ds['obs_all_toa_net'])
    # exit()

    # [print(f) for f in ds.data_vars]
    # print(ds['irwin_cdr'])

    # == specify data and data process ==
    var =           'obs_all_toa_net'
    dataset =       'CERES'
    time_period =   '2001-01:2021-12'
    t_freq =        '3hrly'
    lon_area =      '100:149'
    lat_area =      '-10:10'
    resolution =    0.07

    # == specify data process ==
    process_request = [var, dataset, time_period, t_freq, lon_area, lat_area, resolution]
    da = get_data(process_request, process_data_further)
    print(da)
    exit()



