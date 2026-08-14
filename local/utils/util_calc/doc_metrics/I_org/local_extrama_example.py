

# == imports ==
# -- Packages --
import importlib
import itertools
import xarray as xr
import calendar
import numpy as np
import matplotlib.pyplot as plt
from scipy.ndimage import maximum_filter, minimum_filter

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
mS = import_relative_module('user_specs',                                   'utils')
gD = import_relative_module('util_obs.get_gridsat_data',                    'utils')
doc = import_relative_module('util_calc.doc_metrics.I_org.I_org_calc',      'utils')
pf_trop = import_relative_module('helper_funcs.tropical_domain_plot',       __file__)
pf_sub = import_relative_module('helper_funcs.subdomain_plot',              __file__)
pf_small = import_relative_module('helper_funcs.small_domain_plot',         __file__)


def main():
    # Create sample data
    lon = np.linspace(100, 149, 1000)
    lat = np.linspace(-13, 13, 500)
    lon2d, lat2d = np.meshgrid(lon, lat)
    data = np.sin(lon2d) * np.cos(lat2d) + 1e-6 * (lat2d + lon2d) # avoid repeated values
    data = data + 3
    # data = np.where(data < 2, data, 5)
    # print(np.min(data))
    # print(np.max(data))
    # exit()
    
    # -- single minima --
    data[20, 20] = 1
    
    # # -- minima in big object --
    # data[10, 30] = 1

    # data[10, 31] = 1.1
    # data[10, 32] = 1.2

    # data[11, 30] = 1.1
    # data[12, 30] = 1.2
    
    # data[9, 30] = 1.1
    # data[8, 30] = 1.2
    
    # data[10, 29] = 1.1
    # data[10, 28] = 1.2

    da = xr.DataArray(data, coords=[("lat", lat), ("lon", lon)])

    # -- find local minima --
    lat_coords, lon_coords = doc.find_conv_cores(da, threshold = 5, local_extrema_flag='min')
    fig, ax, cbar_ax = pf_sub.plot(da, da_ontop = None, lon_coords = lon_coords, lat_coords = lat_coords)

    # threshold = 240
    # smoothing, kernel_size, decay_distance =        True,   10,    1                                                                # for pre-process
    # exceed_threshold, local_extrema_flag, window =  True, 'min',  3                                                                 # core settings
    # da_smooth = doc.apply_smoothing(da, kernel_size, decay_distance)                                                                # remove single values
    # lat_coords, lon_coords = doc.find_conv_cores(da_smooth, threshold = 5, local_extrema_flag='min')
    # fig, ax, cbar_ax = pf_sub.plot(da_smooth, da_ontop = None, lon_coords = lon_coords, lat_coords = lat_coords)

    # print(lat_coords, lon_coords)
    # exit()

    # -- save figure --
    folder = '/Users/cbla0002/Desktop/scratch'
    filename = f'example.png'
    path = f'{folder}/{filename}'
    os.makedirs(os.path.dirname(path), exist_ok = True)
    os.remove(path) if os.path.exists(path) else None
    fig.savefig(path, dpi = 600)  
    print(f'plot saved at: {path}')
    plt.close(fig)
    # exit()


if __name__ == '__main__':
    main()
