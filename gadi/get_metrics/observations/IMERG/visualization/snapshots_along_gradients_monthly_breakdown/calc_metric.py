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
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import warnings
warnings.filterwarnings("ignore", category=FutureWarning)

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
mS = import_relative_module('user_specs',                               'utils')
doc = import_relative_module('util_calc.doc_metrics.I_org.I_org_calc',  'utils')
pf_trop = import_relative_module('helper_funcs.tropical_domain_plot',    __file__)
pf_sub = import_relative_module('helper_funcs.subdomain_plot',          __file__)
pf_small = import_relative_module('helper_funcs.small_domain_plot',     __file__)


# == metric funcs ==
def get_metric(da, time_period, metric_var = 'pr_percentiles_95'):
    ''' convective threshold '''
    folder_work, folder_scratch, SU_project, storage_project, data_projects = mS.get_user_specs(show = False)                        # user settings
    # -- specify metric --
    data_tyoe_group =   'observations'
    data_type =         'IMERG'
    metric_group =      'precip'
    metric_name =       'pr_percentiles'
    dataset =           'IMERG'
    # t_freq =            'hrly'
    t_freq =            '3hrly'
    lon_area =          '0:360'
    lat_area =          '-30:30'
    resolution =        0.1
    # -- find path --
    folder = f'{folder_work}/metrics/{data_tyoe_group}/{data_type}/{metric_group}/{metric_name}/{dataset}'
    r_filename = (
            f'{metric_name}'   
            f'_{dataset}'                                                                                                   
            f'_{t_freq}'                                                                                                    
            f'_{lon_area.split(":")[0]}-{lon_area.split(":")[1]}'                                                           
            f'_{lat_area.split(":")[0]}-{lat_area.split(":")[1]}'                                                           
            f'_{int(360/resolution)}x{int(180/resolution)}'                                                                 
            f'_{time_period.split(":")[0]}_{time_period.split(":")[1]}'                                                     
            )       
    folder_metric = f'{folder}/{r_filename}'    # fiels are stored in years here
    year_start, year_end = time_period.split(":")[0].split('-')[0], time_period.split(":")[1].split('-')[0]
    paths = []
    for year in np.arange(int(year_start), int(year_end) + 1):
        path = f'{folder_metric}/{r_filename}_{year}_1-{year}_12.nc'
        paths.append(path)
    try:
        threshold = xr.open_mfdataset(paths, combine='by_coords')[metric_var].load()
        threshold = threshold.mean(dim = 'time')
        da_threshold = threshold.broadcast_like(da.isel(lat = 0, lon = 0))                                                  #
    except:
        print(f'prob couldnt open metric file, check files with structure: {path}')
        print('try regenerating if it does not exist')
        print('exiting')
        exit()
    return da_threshold


# == calculate metric ==
def calculate_metric(data_objects):
    # -- create empty metric --
    metric_name = Path(__file__).resolve().parents[0].name
    ds = xr.Dataset()

    # == create metric ==
    # -- check data --
    da, process_request, count, da2, x_val, y_val, z_val, ii, r_bin_lim, month = data_objects # , da2

    # print(da)
    # print(da2)
    # exit()

    # == get other metrics to help plot ==
    quant = 0.95
    quant_str = f'pr_percentiles_{int(quant * 100)}'
    threshold = get_metric(da, time_period = '2001-01:2023-12', metric_var = quant_str).mean(dim = 'time').data

    # --loop through timesteps --
    for i, timestep in enumerate(da.time):
        da_timestep = da.isel(time = i)
        da2_timestep = da2.isel(time = 0)
        conv_regions = (da_timestep > threshold) * 1

        # -- cores pr --
        smoothing, kernel_size, decay_distance =        True,   6,    1           # for pre-process
        exceed_threshold, local_extrema_flag, window =  True, 'max',  3           # for cores
        da_smooth = doc.apply_smoothing(da_timestep, kernel_size, decay_distance)
        # lat_coords, lon_coords = doc.find_conv_cores(da_smooth, threshold, exceed_threshold, local_extrema_flag, window)

        # -- visualize --
        plot = True
        if plot:
            # -- data for plot --
            da_plot = da_timestep
            spatial_mean = da_plot.mean(dim = ('lat', 'lon'))
            # da_plot = ((da_plot - spatial_mean))                                        # anomalies from the spatial-mean
            # da_plot =  da_plot / da_plot.std()                                          # standard deviation of anomalies
            # da_ontop = da_smooth.where(da_smooth > threshold, np.nan)
            da_ontop = xr.where(conv_regions!= 0, 1, np.nan)    # .drop('time') 

            # # == tropical domain ==
            # # -- plot --
            # fig, ax, cbar_ax = pf_trop.plot(da_plot, da_ontop, lon_coords, lat_coords)
            # # -- labels --
            # title = f'time:{str(timestep.data)[2:18]}'
            # ax_position = ax.get_position()
            # ax.text(ax_position.x0,                                                                                              # x-start
            #         ax_position.y1 + 0.025,                                                                                              # y-start
            #         title,                        
            #         fontsize = 7,  
            #         transform = fig.transFigure,
            #         )
            # # -- save figure --
            # folder = '/scratch/k10/cb4968/temp_plots/imerg_tropical'
            # filename = f'snapshot_{count * len(da.time) + i}.png'
            # path = f'{folder}/{filename}'
            # os.makedirs(os.path.dirname(path), exist_ok = True)
            # os.remove(path) if os.path.exists(path) else None
            # fig.savefig(path, dpi = 600)  
            # print(f'plot saved at: {path}')
            # plt.close(fig)

            # == sub-domain ==
            # da_plot = da_plot.sel(lon = slice(100, 149), lat = slice(-13, 13))
            # da_ontop = da_ontop.sel(lon = slice(100, 149), lat = slice(-13, 13))

            da_plot = da_plot.sel(lon = slice(50, 99), lat = slice(-13, 13))
            da_ontop = da_ontop.sel(lon = slice(50, 99), lat = slice(-13, 13))

            # da_plot = da_plot.sel(lon = slice(0, 360), lat = slice(-13, 13))
            # da_ontop = da_ontop.sel(lon = slice(0, 360), lat = slice(-13, 13))

            # da_plot = da_plot.sel(lon = slice(0, 360), lat = slice(-30, 30))
            # da_ontop = da_ontop.sel(lon = slice(0, 360), lat = slice(-30, 30))

            # -- plot --
            fig, ax, cbar_ax = pf_sub.plot(da_plot, da_ontop) #, lon_coords, lat_coords)
            
            # fig, ax, cbar_ax = pf_trop.plot(da_plot, da_ontop) #, lon_coords, lat_coords)


            # -- labels --
            # title = f'time:{str(timestep.data)[0:13]}, Af:{x_val:.1e},  Am:{y_val:.1e},  CRH:{z_val:.1e}'
            # title = f'time: {str(timestep.data)[0:13]}, radius limit: {r_bin_lim}km \nN_connect: {y_val:.2g}, Af: {x_val:.2g} \nCRH: {z_val:.2g}'
            # ax_position = ax.get_position()
            # ax.text(ax_position.x0 - 0.115,                                                                                              # x-start
            #         ax_position.y1 + 0.05,                                                                                              # y-start
            #         title,                        
            #         fontsize = 6,  
            #         transform = fig.transFigure,
            #         )
            # -- save figure --
            folder = f'/scratch/k10/cb4968/temp_plots/imerg_subdomain_month_{month}_r_bin_lim_{r_bin_lim}/x_bin_{ii}/day_{count}'
            filename = f'snapshot_{i}.png'
            path = f'{folder}/{filename}'
            os.makedirs(os.path.dirname(path), exist_ok = True)
            os.remove(path) if os.path.exists(path) else None
            fig.savefig(path, dpi = 500, transparent=True)  
            print(f'plot saved at: {path}')

            # folder = f'/scratch/k10/cb4968/temp_plots/imerg_subdomain_month_{month}_r_bin_lim_{r_bin_lim}/x_bin_{ii}/day_{count}' # these are too big to save nicely
            # filename = f'snapshot_{i}.svg'
            # path = f'{folder}/{filename}'
            # os.makedirs(os.path.dirname(path), exist_ok = True)
            # os.remove(path) if os.path.exists(path) else None
            # fig.savefig(path, dpi = 500, transparent=True)  
            # print(f'plot saved at: {path}')

            plt.close(fig)
            # exit()
        break
            # # == small domain ==
            # # -- plot --
            # da_plot = da_plot.sel(lon = slice(129, 134), lat = slice(-3, 2))
            # da_ontop = da_ontop.sel(lon = slice(129, 134), lat = slice(-3, 2))
            # fig, ax, cbar_ax = pf_small.plot(da_plot, da_ontop, lon_coords, lat_coords)
            # # -- labels --
            # title = f'time:{str(timestep.data)[2:18]}'
            # ax_position = ax.get_position()
            # ax.text(ax_position.x0,                                                                                              # x-start
            #         ax_position.y1 + 0.015,                                                                                              # y-start
            #         title,                        
            #         fontsize = 7,  
            #         transform = fig.transFigure,
            #         )
            # # -- save figure --
            # folder = '/scratch/k10/cb4968/temp_plots/imerg_small_domain'
            # filename = f'snapshot_{count * len(da.time) + i}.png'
            # path = f'{folder}/{filename}'
            # os.makedirs(os.path.dirname(path), exist_ok = True)
            # os.remove(path) if os.path.exists(path) else None
            # fig.savefig(path, dpi = 600)  
            # print(f'plot saved at: {path}')
            # plt.close(fig)
    #         exit()
    #     exit()
    # exit()
    return ds


