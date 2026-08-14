'''
# -------------
#  data test
# -------------

'''

# == imports ==
# -- packages --
import xarray as xr
import os
import pandas as pd
import calendar

# -- imported scripts --
import os
import sys
sys.path.insert(0, os.getcwd())
import utils.util_obs.conserv_interp       as cI


# == post-process ==
def process_data_further(da):
    ''' This function can be defined and given externally '''
    return da

# == pre-process ==
def pre_process(ds, process_request, day):
    var_name, dataset, time_period, t_freq, lon_area, lat_area, resolution = process_request
    
    # -- pick out variable --    
    da = ds[var_name].load()

    # -- chunk in space before resampling --
    # da = da.chunk({"time": -1, "lat": 256, "lon": 256}) 

    # -- temporally resample (originally in mm/hr)--
    if t_freq == 'hrly':
        da = da.resample(time='1h').mean()
    elif t_freq == '3hrly_max':
        da = da.resample(time='3h').max()
    elif t_freq == '3hrly':
        da = da.resample(time='3h').mean()
    elif t_freq == 'daily':
        da = da.resample(time='1d').mean()
    else:
        pass

    # print(da)
    # print(da.load())
    # exit()

    # -- execute the resampling --
    # da = da.load()

    # -- put lon in range [0, 360] --
    da = da.assign_coords(lon=((da.lon + 360) % 360))
    da = da.sortby('lon')

    # -- make coordinates (lat, lon) --
    da = da.transpose('time', 'lat', 'lon')


    # -- select region of interest --
    da = da.sel(lon = slice(int(lon_area.split(':')[0]), int(lon_area.split(':')[1])), 
                lat = slice(int(lat_area.split(':')[0]), int(lat_area.split(':')[1]))
                )


    # -- regrid, if needed --
    # if resolution > 0.1:
    #     da = cI.conservatively_interpolate(da_in =              da, 
    #                                         res =               resolution, 
    #                                         switch_area =       None,           # regrids the whole globe for the moment 
    #                                         simulation_id =     dataset
    #                                         )
        

    return da


# == get raw data ==
def find_daily_file(folder, year, month, day, return_file = False):
    if int(year) == 2020 and int(month) == 12 and int(day) == 23:                                     # day is missing, give previous days value
        filename = f'3B-HHR.MS.MRG.3IMERG.{year}{month}22.V07A.nc'
        if return_file:
            return filename
        ds = xr.open_dataset(f'{folder}/{filename}', decode_timedelta = False)
        ds['time'] = ds['time'] + pd.Timedelta(days=1)
    elif int(year) == 2020 and int(month) == 12 and int(day) == 24:                                   # day is missing, give previous days value
        filename = f'3B-HHR.MS.MRG.3IMERG.{year}{month}25.V07A.nc'
        if return_file:
            return filename
        ds = xr.open_dataset(f'{folder}/{filename}', decode_timedelta = False)
        ds['time'] = ds['time'] - pd.Timedelta(days=1)
    else:
        filename = f'3B-HHR.MS.MRG.3IMERG.{year}{month}{day}.V07A.nc'
        if return_file:
            return filename
        ds = xr.open_dataset(f'{folder}/{filename}', decode_timedelta = False)
    return ds


def get_data(process_request, process_data_further):
    ''' imerg data '''
    var, dataset, time_str, t_freq, lon_area, lat_area, resolution = process_request
    # [print(f) for f in [var, dataset, time_str, t_freq, lon_area, lat_area, resolution]]
    # exit()

    # -- get file and open data --
    year, month, day = time_str.split('-')
    folder = f'/g/data/ia39/aus-ref-clim-data-nci/gpm/data/V07/{year}'

    if day == "":
        # print('executes')
        n_days = calendar.monthrange(int(year), int(month))[1]
        paths = [f'{folder}/{find_daily_file(folder,year, month, f"{i:02d}", return_file = True)}' for i in range(1, n_days + 1)]                         # take the whole month in this case
        # print(paths[0])
        # print(len(paths))
        # exit()
        ds = xr.open_mfdataset(paths, combine="by_coords", decode_timedelta=False)
        # print(ds)
    else:
        ds = find_daily_file(folder, year, month, f'{int(day):02d}')
    # exit()

    # -- pre-process --
    da = pre_process(ds, process_request, day)
    
    # -- post-process --
    da = process_data_further(da)
    return da


if __name__ == '__main__':
    # path = f'/g/data/ia39/aus-ref-clim-data-nci/gpm/data/V07/2020/3B-HHR.MS.MRG.3IMERG.20201225.V07A.nc'
    # da = xr.open_dataset(path)['precipitation']
    # print(da)
    # print(da)
    # exit()

    # == specify data and data process ==
    var =           'precipitation'
    dataset =       'IMERG'
    time_str =      '2001-06-06'
    t_freq =        ''
    lon_area =      '100:149'
    lat_area =      '-10:10'
    resolution =    0.1


    time_str =      '2001-06-'

    # == specify data process ==
    process_request = [var, dataset, time_str, t_freq, lon_area, lat_area, resolution]
    da = get_data(process_request, process_data_further)
    print(da)
    exit()





