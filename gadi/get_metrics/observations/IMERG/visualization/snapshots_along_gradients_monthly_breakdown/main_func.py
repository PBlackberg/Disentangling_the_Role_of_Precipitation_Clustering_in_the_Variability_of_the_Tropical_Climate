'''
# -----------------
#    Main_func
# -----------------

'''

# == imports ==
# -- Packages --
import importlib
import itertools
from distutils.util import strtobool  
import xarray as xr
import calendar
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

# -- util- and local scripts --
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
mS = import_relative_module('user_specs',                                           'utils')
jS = import_relative_module('submit_as_job',                                        __file__)
mC = import_relative_module('calc_metric',                                          __file__)
gD = import_relative_module('util_obs.get_imerg_data',                              'utils')
cW = import_relative_module('util_calc.area_weighting.globe_area_weight',           'utils')
pf_scatter = import_relative_module('helper_funcs.scatter_plot',                    __file__)
pf2_scatter = import_relative_module('helper_funcs.scatter_plot2_2',                    __file__)

# == process data ==
def post_process_data(da):
    ''
    return da

# == get metric ==
def get_saved_metric(data_type_group, data_type, dataset, resolution, time_period,
                t_freq, metric_group, metric_name, metric_var, lat_area, lon_area,
                single_value = True, 
                ):
    folder_work, folder_scratch, SU_project, storage_project, data_projects = mS.get_user_specs(show = False)                        # user settings
    # -- find path --
    folder = f'{folder_work}/metrics/{data_type_group}/{data_type}/{metric_group}/{metric_name}/{dataset}'
    r_filename = (
            f'{metric_name}'   
            f'_{dataset}'                                                                                                   
            f'_{t_freq}'                                                                                                    
            f'_{lon_area.split(":")[0]}-{lon_area.split(":")[1]}'                                                           
            f'_{lat_area.split(":")[0]}-{lat_area.split(":")[1]}'                                                           
            f'_{int(360/resolution)}x{int(180/resolution)}'                                                                 
            f'_{time_period.split(":")[0]}_{time_period.split(":")[1]}'                                                     
            )     
    folder_metric = f'{folder}/{r_filename}'
    year_start, year_end = time_period.split(":")[0].split('-')[0], time_period.split(":")[1].split('-')[0]
    # -- metrics saved in months or years, respectively --
    paths = []
    if metric_name in ['L_org']: # stored in months
        for year in np.arange(int(year_start), int(year_end) + 1):
            for month in np.arange(1, 13):
                path = f'{folder_metric}/{r_filename}_{year}_{month}-{year}_{month}.nc'
                paths.append(path)
    else:                       # stored in years
        for year in np.arange(int(year_start), int(year_end) + 1):
            if year > 2021:
                continue
            path = f'{folder_metric}/{r_filename}_{year}_1-{year}_12.nc'
            paths.append(path)
    ds = xr.open_mfdataset(paths, combine='by_coords').load()

    # -- calculate single value metric (per timestep) --
    if single_value:
        if metric_name == 'i_org':
            metric = np.trapezoid(ds['i_org_obs_thres_pr_percentiles_95'], ds['i_org_random_thres_pr_percentiles_95'])
            metric = xr.DataArray(metric, coords={"time": ds.time}, dims=["time"])
        elif metric_name == 'L_org':
            metric = ds #
            # L_random = ds['L_org_random_thres_pr_percentiles_95']
            # r_bin_edges = ds['r_bin_edges']
            # metric = np.trapz(L_obs - L_random, x = r_bin_edges)
            # metric = xr.DataArray(metric, coords={"time": ds.time}, dims=["time"])
        else:
            metric = ds[metric_var]
    else:
        metric = ds[metric_var]
    return metric

# def remove_season_from_daily(da):
#     da = da.resample(time='1D').mean()                                                                      # remove diurnal variability
#     da_smooth = da.rolling(time=7, center=True, min_periods=1).mean()                                       # smooth timescale of weather patterns
#     anomalies = da_smooth.groupby("time.dayofyear") - da_smooth.groupby("time.dayofyear").mean("time")      # remove seasonal cycle
#     return anomalies

def detrend_data(da):
    fit = da.polyfit(dim="time", deg=1, skipna=True)
    trend = xr.polyval(da["time"], fit.polyfit_coefficients)
    da_detrended = da - trend
    return da_detrended

def remove_season_daily(da):
    da_smooth = da.rolling(time=7, center=True, min_periods=1).mean()                                       # smooth timescale of weather patterns (7 days here)
    anomalies = da_smooth.groupby("time.dayofyear") - da_smooth.groupby("time.dayofyear").mean("time")      # remove seasonal cycle
    return anomalies

def get_metric(dataset, t_freq, lon_area, lat_area, resolution, time_period, years, months, r_folder, r_filename, section_range, test):    
    _, folder_scratch, _, _, _ = mS.get_user_specs()                                                                                            # for temporarily saving timestep
    
    # == get data (daily-means 1x1 degree) ==
    folder = '/g/data/k10/cb4968/era5_daily_means/satfrac'
    year1 = '2001'
    year2 = '2021'
    years = range(int(year1), int(year2)+1)
    paths = [f'{folder}/{f"era5_satfrac_daily_mean_{year}.nc"}' for year in years]
    ds = xr.open_mfdataset(paths)
    da = ds['sat_frac']
    da = da.assign_coords(lon=((da.lon + 360) % 360))
    da = da.sortby('lon')
    # print(da)
    # -- select region of interest --
    da = da.sel(lon = slice(int(lon_area.split(':')[0]), int(lon_area.split(':')[1])), 
                lat = slice(int(lat_area.split(':')[0]), int(lat_area.split(':')[1]))
                ).load()
    da_area_lat = da['lat'].sel(lat = slice(-30, 30)).load()    # for area weighting later
    da_area_lon = da['lon'].sel(lon = slice(0, 360)).load()
    da2 = da * 100
    # print(da2)
    # exit()
    # da2 = remove_season_from_daily(da)
    
    # print(da2)
    # exit()

    # == load saved metrics ==
    # -- x-metric --
    x_tfreq,    x_group,    x_name, x_var,  x_label,    x_units =   '3hrly',      'doc_metrics',    'area_fraction',            'area_fraction_thres_pr_percentiles_95',        r'A$_f$',   r''   

    # -- y-metric --
    y_tfreq,   y_group,   y_name,    y_var, y_label,   y_units =    '3hrly',      'doc_metrics',    'mean_area',                'mean_area_thres_pr_percentiles_95',            r'A$_m$',   r'km$^2$'    
    # y_tfreq,   y_group,   y_name,    y_var, y_label,   y_units =    '3hrly',      'doc_metrics',    'L_org',                    'L_org_obs_thres_pr_percentiles_95',            r'',        r''    

    # -- z-metric --
    z_tfreq,   z_group,   z_name,    z_var, z_label,   z_units =    'daily',      'satfrac',        'satfrac_timeseries',       'satfrac_timeseries',                           r'RH',      r'%'    
    
    # lon_area =      '50:99'    
    # lat_area =      '-13:13'      
    lon_area =      '0:360'    
    lat_area =      '-13:13'   
    # lat_area =      '-30:30'   
    resolution =    0.1    
    time_period =   '2001-01:2023-12'     
    data_type_group, data_type, dataset = 'observations', 'IMERG', 'IMERG'
    single_value = True
    x = get_saved_metric(data_type_group, data_type, dataset, resolution, time_period, x_tfreq, x_group, x_name, x_var, lat_area, lon_area, single_value) * 100
    y = get_saved_metric(data_type_group, data_type, dataset, resolution, time_period, y_tfreq, y_group, y_name, y_var, lat_area, lon_area, single_value) / 10000
    # print(y)
    # exit()

    # lon_area =      '50:99'                                                                                                                                                                                      
    # lat_area =      '-13:13'             
    lon_area =      '0:360'    
    lat_area =      '-13:13'                
    # lat_area =      '-30:30'                                                                                                                                                      
    resolution = 1.    
    time_period = '2001-01:2023-12'      
    data_type_group, data_type, dataset = 'observations', 'ERA5', 'ERA5'
    z = get_saved_metric(data_type_group, data_type, dataset, resolution, time_period, z_tfreq, z_group, z_name, z_var, lat_area, lon_area, single_value) * 100
    
    # -- monthly breakdown --
    months_name = ['jan', 'feb', 'mar', 'apr', 'may', 'jun', 'jul', 'aug', 'sep', 'oct', 'nov', 'dec']
    for month in np.arange(1, 13):
        if not month == 4:
            continue
        for r_bin_lim in [100]: #, 30, 40, 50, 100, 200, 500]: #, 1000, 2750]: # [50, 100, 200, 500, 1000, 2750]
            if y_name == 'mean_area':
                pass
                # da_area = cW.get_area_matrix(da_area_lat, da_area_lon)   
                # da_area = da_area.sel(lon = slice(int(lon_area.split(':')[0]), int(lon_area.split(':')[1])), 
                #                         lat = slice(int(lat_area.split(':')[0]), int(lat_area.split(':')[1]))
                #                     )
                # y = y / da_area.sum()                                                             # phrase mean area as a fraction of the domain, to keep consistent units (unitsless) in predictor terms   
                
            elif y_name == 'L_org':
                da_area = cW.get_area_matrix(da_area_lat, da_area_lon)   
                da_area = da_area.sel(lon = slice(int(lon_area.split(':')[0]), int(lon_area.split(':')[1])), 
                                        lat = slice(int(lat_area.split(':')[0]), int(lat_area.split(':')[1])))
                L_obs = ds['L_org_obs_thres_pr_percentiles_95']
                r_bin_edges = ds['r_bin_edges']
                # print(x.max().data)
                # print(x.min().data)
                # exit()
                y = np.pi * (L_obs**2 / da_area.sum()) * (x * (len(da_area['lat']) * len(da_area['lon']))) # * 100 # (frraction of points as percentage) #  # dividing by the number of "cores" (when considering all convective points). This represents the mean fraction of points within a radius

                # method 1
                y = y.sel(r_bin_edges = r_bin_lim, method='nearest')

                # method 2
                # y = y.sel(r_bin_edges = slice(0, r_bin_lim))
                # r_bin_edges = r_bin_edges.sel(r_bin_edges = slice(0, r_bin_lim))
                # y = np.trapz(y, x = r_bin_edges)        
                # y = xr.DataArray(y, coords={"time": x.time}, dims=["time"])
                # y = xr.DataArray(y, coords={"time": L_obs.time}, dims=["time"])
                # # r_max = 2750
                # r_max = r_bin_lim
                # y = y / r_max
                # print('executes') # will the integrated values show the spatial scales here? split into months after
            else:
                pass
            # print(y)
            # exit()

            xy_list = [x, y, z] # [x, y, z]

            xy_list = [da.resample(time='1D').mean() for da in xy_list]                                 # remove diurnal variability
            xy_list = [detrend_data(da) for da in xy_list]                                              # detrend
            xy_list = [remove_season_daily(da) for da in xy_list]                                       # remove seasonal cycle

            # =========================
            # Dates for example plots
            # Deep tropical [low, high] = [numpy.datetime64('2002-04-20T00:00:00.000000000'), numpy.datetime64('2020-04-02T00:00:00.000000000')]

            # Indian Ocean small    [low, high] =   [numpy.datetime64('2002-04-08T00:00:00.000000000'), numpy.datetime64('2009-04-18T00:00:00.000000000')]
            # Indian Ocean medium   [low, high] =   [numpy.datetime64('2002-04-20T00:00:00.000000000'), numpy.datetime64('2020-04-02T00:00:00.000000000')]
            # Indian Ocean large    [low, high] =   [numpy.datetime64('2003-04-30T00:00:00.000000000'), numpy.datetime64('2013-04-02T00:00:00.000000000')]
            # Indian Ocean v. large [low, high] =   []

            # print(xy_list[0])
            # exit()

            # ==========================

            # print(xy_list[0])
            # exit()
            # standard deviations
            # xy_list = [remove_season_from_daily(da) for da in xy_list]
            # xy_list = [da.sel(time = da['time.month'] == month) for da in xy_list]
            # xy_list = [da.resample(time='1D').mean() for da in xy_list]
            xy_list = [da.dropna(dim='time', how='any') for da in xy_list]
            xy_list = list(xr.align(*xy_list, join='inner'))


            # === version 1 ==
            # find times of the example snapshots
            # times = [
            #     # np.datetime64('2002-04-08T00:00:00.000000000'), np.datetime64('2009-04-18T00:00:00.000000000'),   # small
            #     np.datetime64('2002-04-20T00:00:00.000000000'), np.datetime64('2020-04-02T00:00:00.000000000'),     # medium
            #     # np.datetime64('2003-04-30T00:00:00.000000000'), np.datetime64('2013-04-02T00:00:00.000000000')    # large
            #     ]
            # times = np.array(times, dtype='datetime64[ns]')
            # idx_t = [                                                                   # find the idx of the times picked out
            #     int(np.where(xy_list[0].time.values == t)[0][0])
            #     for t in times
            # ]

            # === version 2 ==
            # find times of the example snapshots
            times = [
                # np.datetime64('2017-02-08T00:00:00.000000000'), np.datetime64('2014-07-21T00:00:00.000000000'),   # small
                np.datetime64('2002-04-20T00:00:00.000000000'), np.datetime64('2020-04-02T00:00:00.000000000'),     # medium
                # np.datetime64('2004-10-27T00:00:00.000000000'), np.datetime64('2011-11-28T00:00:00.000000000')    # large
                ]
            times = np.array(times, dtype='datetime64[ns]')
            #     # np.datetime64('2015-02-03T00:00:00.000000000'), np.datetime64('2011-12-29T00:00:00.000000000'),   # medium
            # print(idx_t)
            # exit()

            xy_list_numpy = [da.data for da in xy_list]                                       # make numpy
            xy_list_numpy = [(da - np.mean(da)) / np.std(da, ddof=1) for da in xy_list]       # standardize

            xy_list = [                                                                  # give back the original coordinates and make xarray for next operations (for bin scatter)
                xr.DataArray(arr, coords=original.coords, dims=original.dims)
                for arr, original in zip(xy_list_numpy, xy_list)
            ]
         
            # == visualize timesteps in bins ==
            # some_bins = np.arange(0, 0.30, 0.02)   
            some_bins = np.linspace(np.min(xy_list[0]), np.max(xy_list[0]), 15)  
            for ii, a_bin in enumerate(some_bins):
                # indian Ocean domain
                # if not ii == 2:     # small, binwidth = 0.1
                #     continue

                # if not ii == 6:   # med, binwidth = 0.15
                #     continue

                if not ii == 12:  # large, binwidth = 0.15
                    continue

                print(f'on af_bin: {ii}')
                lower_bound = a_bin - 0.15 # 0.75 # 0.25 #/ 5 #0.01 #0.1 #1 #0.01, 0.75
                upper_bound = a_bin + 0.15 # 0.75 # 0.25 #/ 5 #0.01 #0.1 #1 #0.01, 0.75
                # [print(f'{a} \n') for a in xy_list]
                # exit()

                # exit()
                # pf_scatter.plot_a_scatter(xy_list[0], xy_list[1], xy_list[2], ii, lower_bound, upper_bound, r_bin_lim, month)
                
                # -- create figure --    
                width, height = 5.5, 4
                width, height = [f / 2.54 for f in [width, height]] # convert to inches
                ncols, nrows  = 1, 1
                fig, ax = plt.subplots(nrows, ncols, figsize = (width, height))

                pf_scatter.plot_a_scatter(xy_list[0], xy_list[1], xy_list[2], ii, lower_bound, upper_bound, r_bin_lim, month)
                # pf2_scatter.plot_a_scatter(xy_list[0], xy_list[1], fig, ax, month, r_bin_lim, ii, idx_t=idx_t)
                # exit()
                # break
                # exit()
                # continue

                # == finding times, comment out if already times given (start here) ==
                xy_list_bin = [da.where((xy_list[0] >= lower_bound) & (xy_list[0] <= upper_bound), np.nan) for da in xy_list]
                x_bin, y_bin, z_bin = xy_list_bin[0], xy_list_bin[1], xy_list_bin[2]

                # if np.count_nonzero(~np.isnan(x_bin)) < 5:
                #     continue
                # # break

                # qs = [0., 1.]
                # # qs = [0.1, 0.9]
                # # qs = [0.2, 0.8]
                # ps = y_bin.quantile(qs, dim="time")    
                # times = []
                # for p in ps:
                #     da_diff = np.abs(y_bin - p)
                #     time_idx = da_diff.argmin() 
                #     a_time = y_bin.time.isel(time = time_idx).values
                #     times.append(a_time)

                # times = xr.concat(times, dim='time')

                # print(times)
                # print([times[0], times[-1]])
                # exit()
                # print(y_bin)
                # y_subset = y_bin.sel(time = times)
                # print(y_subset)
                # exit()
                # == finding times, comment out if already times given (until here) ==

                # == visualize timesteps ==
                count = 0    
                # for i, t in enumerate([times.data[0], times.data[-1]]):
                # for i, t in enumerate([times[0], times[-1]]):
                # for i, t in enumerate(times): 
                #     timestamp = pd.Timestamp(t)
                #     year, month, day = timestamp.year, timestamp.month, timestamp.day
                #     time_str =      f'{year}-{int(month):02d}-{int(day):02d}'
                #     t_freq = '3hrly'
                #     process_request = ['precipitation', 'IMERG', time_str, t_freq, lon_area, lat_area, 0.1]
                #     da = gD.get_data(process_request, process_data_further = post_process_data)    
                #     da2_day = da2.sel(time = time_str)
                #     # print(da)
                #     # exit()
                #     x_val, y_val, z_val = x_bin.sel(time = time_str), y_bin.sel(time = time_str), z_bin.sel(time = time_str)
                #     data_objects = [da, process_request, count, da2_day, x_val, y_val, z_val, ii, r_bin_lim, month]                                                                              
                #     mC.calculate_metric(data_objects)
                #     count += 1
                #     # exit()

                idx_t = [                                                                   # find the idx of the times picked out
                    int(np.where(xy_list[0].time.values == t)[0][0])
                    for t in times
                ]
                xy_list_numpy = [da.data for da in xy_list]                                       # make numpy
                pf2_scatter.plot_a_scatter(xy_list_numpy[0], xy_list_numpy[1], fig, ax, month, r_bin_lim, ii, idx_t=idx_t) 

                exit()
            # exit()
        # exit()

# == concatenate results ==
def concat_result(r_folder, r_filename, test):
    ''
    # # -- load collection of partial results --
    # print('finding temp files for section results')    
    # folder_work, folder_scratch, SU_project, storage_project, data_projects = mS.get_user_specs()
    # folder = f'{folder_scratch}/temp_calc/{r_folder}/{r_filename}'
    # temp_files = [f'{folder}/{f}' for f in os.listdir(folder) if f.endswith('.nc')]
    # # -- concatenate --
    # print('concatenating results')    
    # ds = xr.open_mfdataset(temp_files, combine="by_coords", engine="netcdf4", parallel=True).load()
    # print(ds)
    # if not test:
    #     # -- save result --
    #     folder = f'{folder_work}/metrics/{r_folder}'
    #     filename = f'{r_filename}.nc'
    #     path = f'{folder}/{filename}'
    #     os.makedirs(os.path.dirname(path), exist_ok=True)
    #     ds.to_netcdf(path, mode="w")
    #     print('saved result')    

    #     # -- remove tempfiles --
    #     print('removing temp files')    
    #     [os.remove(path_temp) for path_temp in temp_files]


# == main ==
def main(switch, dataset, t_freq, lon_area, lat_area, resolution, time_period, years, months, r_folder, r_filename, section_range, test = False):
    if switch.get('calc'):
        get_metric(dataset, t_freq, lon_area, lat_area, resolution, time_period, years, months, r_folder, r_filename, section_range, test)
    if switch.get('concat'):
        concat_result(r_folder, r_filename, test)
    print('finished')        
    if os.environ.get('PBS_SCRIPT'):
        print(f'removing resource script')
        os.remove(os.environ.get('PBS_SCRIPT'))


# == when this script is ran / submitted ==
if __name__ == '__main__':
    if not os.environ.get("PBS_SCRIPT"):                                                                                                # when run interactively (test)
        datasets, t_freqs, lon_areas, lat_areas, resolutions, time_periods = jS.set_specs()                                             # all specs
        for i, (t, lat, lon, r, d, p) in enumerate(itertools.product(t_freqs,                                                           #
                                                                    lat_areas,                                                          #
                                                                    lon_areas,                                                          #
                                                                    resolutions,                                                        #
                                                                    datasets, time_periods)):                                           # loops over all specs (looped in input order)
            r_folder, r_filename = jS.get_path(d, t, lon, lat, r, p)
            print(f'Running metric for:')
            print(f'folder:     {r_folder}')
            print(f'filename:   {r_filename}')
            time_section = jS.get_timesections(n_jobs = 1, time_period = p)[0] 
            years_section, months_section = zip(*time_section)     
            year1_section, month1_section = time_section[0]
            year2_section, month2_section = time_section[-1]
            section_range =  f'{year1_section}_{month1_section}-{year2_section}_{month2_section}'   
            main(switch =           {'calc': True, 
                                     'concat': False},
                 dataset =          d,
                 t_freq =           t,
                 lon_area =         lon,
                 lat_area =         lat,
                 resolution =       r,
                 time_period =      p,
                 years =            years_section,
                 months =           months_section,
                 r_folder =         r_folder,
                 r_filename =       r_filename,
                 section_range =    section_range,
                 test =             True,
                 )
            exit()
    else:                                                                                                                               # when submitted (save)
            main(switch =           {'calc': strtobool(os.environ.get("SWITCH_CALC")), 
                                    'concat': strtobool(os.environ.get("SWITCH_CONCAT"))},
                 dataset =          os.environ.get('DATASET'),
                 t_freq =           os.environ.get('T_FREQ'),
                 lon_area =         os.environ.get('LON_AREA'),
                 lat_area =         os.environ.get('LAT_AREA'),
                 resolution =       float(os.environ.get('RESOLUTION')),
                 time_period =      os.environ.get('TIME_PERIOD'),
                 years =            os.environ.get("YEAR").split(':'),
                 months =           os.environ.get("MONTH").split(':'),
                 r_folder =         os.environ.get('R_FOLDER'),
                 r_filename =       os.environ.get('R_FILENAME'),
                 section_range =    os.environ.get('SECTION_RANGE'),
                 )