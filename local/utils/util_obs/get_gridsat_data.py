'''
# ---------------------
#  Get gridsat-B1 data
# ---------------------
https://www.ncei.noaa.gov/data/geostationary-ir-channel-brightness-temperature-gridsat-b1/access/2001/

'''

# == imports ==
# -- packages --
import xarray as xr
import os
import pandas as pd
import importlib

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
gD = import_relative_module('util_obs.get_gridsat_files_one',                    'utils')

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
    da = da.assign_coords(lon=((da.lon + 360) % 360))
    da = da.sortby('lon')

    # -- make coordinates (lat, lon) --
    da = da.transpose('time', 'lat', 'lon')

    # -- select region of interest --
    da = da.sel(lon = slice(int(lon_area.split(':')[0]), int(lon_area.split(':')[1])), 
                lat = slice(int(lat_area.split(':')[0]), int(lat_area.split(':')[1]))
                )
    return da


# == get raw data ==
def get_data(process_request, process_data_further):
    ''' imerg data '''
    var, dataset, time_str, t_freq, lon_area, lat_area, resolution = process_request
    # [print(f) for f in [var, dataset, time_str, t_freq, lon_area, lat_area, resolution]]
    # exit()

    # -- get file and open data --
    year, month, day = time_str.split('-')
    # folder = f'/Users/cbla0002/Desktop/work/data/GRIDSAT_data/{year}'
    folder = f'/Volumes/satellite1/work/data/GRIDSAT_data/{year}'
    ds_list = []
    for hour in ['00', '03', '06', '09', '12', '15', '18', '21']:
        # if hour == '03':
        #     filename = f'GRIDSAT-B1.{year}.{month}.{day}.{hour}.v02r01.nc'
        #     path = f'{folder}/{filename}'
        #     print(path)
        #     ds = xr.open_dataset(path)
        #     print(ds)
        #     exit()
        # print(year)
        # print(month)
        # print(day)
        # print(hour)
        # exit()
        filename = f'GRIDSAT-B1.{year}.{month}.{day}.{hour}.v02r01.nc'
        path = f'{folder}/{filename}'
        if not os.path.exists(path):
            base_url = "https://www.ncei.noaa.gov/data/geostationary-ir-channel-brightness-temperature-gridsat-b1/access"
            dest_base = "/Volumes/satellite1/work/data/GRIDSAT_data"
            gD.main(base_url, dest_base, year, month, day, hour)
        if not os.path.exists(path):
            raise FileNotFoundError(f"Still missing after download: {path}")
        try:
            ds_list.append(xr.open_dataset(path)[var].load())        
        except (OSError, IOError) as e:
            os.remove(path)
            base_url = "https://www.ncei.noaa.gov/data/geostationary-ir-channel-brightness-temperature-gridsat-b1/access"
            dest_base = "/Volumes/satellite1/work/data/GRIDSAT_data"
            gD.main(base_url, dest_base, year, month, day, hour)
            ds_list.append(xr.open_dataset(path)[var].load())     
        # print(ds_list[0])
        # exit()
    ds = xr.concat(ds_list, dim="time")    
    # print(ds)
    # exit()

    # -- pre-process --
    da = pre_process(ds, process_request)
    
    # -- post-process --
    da = process_data_further(da)
    return da


if __name__ == '__main__':
    # path = '/Users/cbla0002/Desktop/work/data/gridsat_data/2001/GRIDSAT-B1.2001.01.01.00.v02r01.nc'
    # ds = xr.open_dataset(path)
    # print(ds)
    # exit()
    # [print(f) for f in ds.data_vars]
    # print(ds['irwin_cdr'])

    # == specify data and data process ==
    var =           'irwin_cdr'
    dataset =       'GRIDSAT'
    time_str =      '2001-01-01'
    t_freq =        '3hrly'
    lon_area =      '100:149'
    lat_area =      '-10:10'
    resolution =    0.07

    # == specify data process ==
    process_request = [var, dataset, time_str, t_freq, lon_area, lat_area, resolution]
    da = get_data(process_request, process_data_further)
    print(da)
    exit()







