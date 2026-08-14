'''
# -----------------
#   Calc_metric
# -----------------

'''

# == imports ==
# -- Packages --
import numpy as np
import xarray as xr
from pathlib import Path

# -- util- and local scripts --
import os
import sys
import importlib
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
mS = import_relative_module('user_specs',                                                   'utils')
cW = import_relative_module('util_calc.area_weighting.globe_area_weight',                   'utils')
doc = import_relative_module('util_calc.doc_metrics.I_org.I_org_calc',                      'utils')


# == calculate metric ==
def calculate_metric(data_objects):
    # -- create empty metric --
    metric_name = f'{Path(__file__).resolve().parents[0].name}_obs'
    metric_name2 = f'{Path(__file__).resolve().parents[0].name}_random'
    ds = xr.Dataset()

    # == create metric ==
    # -- check data --
    da, process_requestd, count = data_objects    
    # print(da)
    # exit()

    # -- metrics settings --
    r_max = 1000
    dx = 10
    r_bin_edges = np.arange(0, r_max + dx, dx)

    # -- threshold variations --
    quantile_thresholds = [0.95] #, 0.97, 0.99] #0.9, 
    for quant in quantile_thresholds:
        quant_str = f'percentile_{int(quant * 100)}'
        threshold = 240

        # --loop through timesteps --
        metric_calc = []
        metric_calc2 = []
        for i, timestep in enumerate(da.time):
            da_timestep = da.isel(time = i)
            smoothing, kernel_size, decay_distance =        True,   10,     1                                                   # smoothing settings (10 because 0.07 resolution)
            exceed_threshold, local_extrema_flag, window =  True,   'min',  3                                                   # core setttings
            da_smooth = doc.apply_smoothing(da_timestep, kernel_size, decay_distance)                                           # smoothed field
            lat_coords, lon_coords = doc.find_conv_cores(da_smooth, threshold, exceed_threshold, local_extrema_flag, window)    # cores

            # -- calculate metric --
            i_org, obs_cdf, random_cdf, cumulative_sum, N_c = doc.main(da_timestep, lat_coords, lon_coords, r_bin_edges, dx)

            metric_timestep = obs_cdf
            metric_timestep = xr.DataArray(metric_timestep, dims = ['r_bin_edges'], coords = {'r_bin_edges': r_bin_edges})
            metric_timestep = metric_timestep.expand_dims(dim = 'time')
            metric_timestep = metric_timestep.assign_coords(time=[timestep.values])            
            metric_calc.append(metric_timestep)

            metric_timestep = random_cdf
            metric_timestep = xr.DataArray(metric_timestep, dims = ['r_bin_edges'], coords = {'r_bin_edges': r_bin_edges})
            metric_timestep = metric_timestep.expand_dims(dim = 'time')
            metric_timestep = metric_timestep.assign_coords(time=[timestep.values])            
            metric_calc2.append(metric_timestep)

        # -- concatenate timesteps --
        metric_calc = xr.concat(metric_calc, dim = 'time')
        metric_calc2 = xr.concat(metric_calc2, dim = 'time')

        # -- fill xr.dataset with metric --
        ds[f'{metric_name}_thres_{quant_str}'] = metric_calc
        ds[f'{metric_name2}_thres_{quant_str}'] = metric_calc2

    # print(ds)
    # exit()
    return ds

