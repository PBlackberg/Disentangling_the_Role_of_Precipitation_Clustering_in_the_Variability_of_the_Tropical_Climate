'''
# -----------------
#   Calc_metric
# -----------------

'''

# == imports ==
import xarray as xr
import numpy as np
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
cW = import_relative_module('util_calc.area_weighting.globe_area_weight',                   'utils')


# == calculate metric ==
def calculate_metric(data_objects):
    # -- fill xr.Dataset --
    metric_name = Path(__file__).resolve().parents[0].name
    ds = xr.Dataset()

    # -- check data --
    da, process_request = data_objects
    # print(da)
    # exit()

    # -- timeseries --
    da_area = cW.get_area_matrix(da.lat, da.lon)
    ds[f'{metric_name}_high_mean'] = (da.sel(cloud_layer = 1) * da_area).sum(dim = ('lat', 'lon')) / da_area.sum()
    ds[f'{metric_name}_uppermid_mean'] = (da.sel(cloud_layer = 2) * da_area).sum(dim = ('lat', 'lon')) / da_area.sum()
    ds[f'{metric_name}_lowermid_mean'] = (da.sel(cloud_layer = 3) * da_area).sum(dim = ('lat', 'lon')) / da_area.sum()
    ds[f'{metric_name}_low_mean'] = (da.sel(cloud_layer = 4) * da_area).sum(dim = ('lat', 'lon')) / da_area.sum()
    ds[f'{metric_name}_total_mean'] = (da.sel(cloud_layer = 5) * da_area).sum(dim = ('lat', 'lon')) / da_area.sum()

    # print(ds)
    # exit()
    return ds
