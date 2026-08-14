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
doc = import_relative_module('util_calc.doc_metrics.area_fraction.area_fraction',           'utils')
doc2 = import_relative_module('util_calc.doc_metrics.I_org.I_org_calc',                     'utils')
cW = import_relative_module('util_calc.area_weighting.globe_area_weight',                   'utils')


# == calculate metric ==
def calculate_metric(data_objects):
    # -- create empty metric --
    metric_name = f'{Path(__file__).resolve().parents[0].name}'
    ds = xr.Dataset()

    # == create metric ==
    # -- check data --
    da, process_requestd, count = data_objects    

    # -- for area weighting --
    da_area = cW.get_area_matrix(da.lat, da.lon)   

    # -- threshold variations --
    quantile_thresholds = [0.95] #, 0.97, 0.99] #0.9, 
    for quant in quantile_thresholds:
        quant_str = f'percentile_{int(quant * 100)}'
        threshold = 240

        # --loop through timesteps --
        metric_calc = []
        for i, timestep in enumerate(da.time):
            da_timestep = da.isel(time = i)

            # -- calculate metric --
            smoothing, kernel_size, decay_distance =        True,   10,     1           # for smoothing (10 because 0.07 resolution)
            da_smooth = doc2.apply_smoothing(da_timestep, kernel_size, decay_distance)
            conv_regions = (da_smooth > 0) & (da_smooth < threshold) * 1
            metric_timestep = doc.area_fraction(conv_regions, da_area)

            # -- put timestep xarray data arrays in list --
            metric_timestep = xr.DataArray(metric_timestep)
            metric_timestep = metric_timestep.expand_dims(dim = 'time')
            metric_timestep = metric_timestep.assign_coords(time=[timestep.values])
            metric_calc.append(metric_timestep)

        # -- concatenate timesteps --
        metric_calc = xr.concat(metric_calc, dim = 'time')

        # -- fill xr.dataset with metric --
        ds[f'{metric_name}_thres_{quant_str}'] = metric_calc

    # print(ds)
    # exit()
    return ds

