'''
# -----------------
#  Submit_as_job
# -----------------

'''

# == Imports ==
# -- Packages --
import os
import sys
import importlib
from pathlib import Path
import numpy as np

# -- util- and local scripts --
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
        relative_path = file_path.replace(os.getcwd(), "").lstrip("/")
        module_base = os.path.dirname(relative_path).replace("/", ".").strip(".")
        module_path = f"{module_base}.{module_name}"
    return importlib.import_module(module_path)
mS = import_relative_module('user_specs',                   'utils')


# == Set specs ==
def set_specs():
    datasets = (                                                                                                                    # Models ordered by change in temperature with warming    
        'GRIDSAT',                                                                                                                  # 1
        )                                                                                                                           #
    t_freqs = (                                                                                                                     #
        '3hrly',                                                                                                                    # 
        )                                                                                                                           #
    lon_areas = (                                                                                                                   # set lon extent
        '0:360',                                                                                                                    # Full domain                                         
        # '0:49',                                                                                                                   # Africa
        # '50:99',                                                                                                                  # Indian Ocean
        # '100:149',                                                                                                                # Maritime Continent                                    
        # '150:204',                                                                                                                # West / central Pacific    (55 degrees, 5 degrees wider)
        # '205:259',                                                                                                                # East Pacific              (55 degrees, 5 degrees wider)
        # '260:309',                                                                                                                # Amazon
        # '310:359',                                                                                                                # Atlantic
        )                                                                                                                           #
    lat_areas = (                                                                                                                   # set lat extent (can be looped)
        # '-90:90',                                                                                                                 #
        '-30:30',                                                                                                                 # Tropics
        # '-20:20',                                                                                                                 # Central tropics
        # '-13:13',                                                                                                                   # 
        # '-10:10',                                                                                                                 # Equator
        )                                                                                                                           #
    resolutions = (                                                                                                                 #
        0.07,                                                                                                                       #        
        )                                                                                                                           #
    time_periods = (                                                                                                                # time_periods for metric (can be looped)
        '2001-01:2023-12',                                                                                                          #
        )                                                                                                                           #
    return datasets, t_freqs, lon_areas, lat_areas, resolutions, time_periods

def get_timesections(n_jobs, time_period):
    year1, month1 = map(int, time_period.split(':')[0].split('-'))                                                                  #
    year2, month2 = map(int, time_period.split(':')[1].split('-'))                                                                  #
    timesteps = [(year, month) for year in range(int(year1), int(year2) + 1) for month in range(1, 13)                              # year, month pair
                 if not (year == year1 and month < month1) and not (year == year2 and month > month2)]                              # clipping months of first and last year
    time_sections = np.array_split(timesteps, n_jobs)                                                                               #
    return time_sections

def get_path(dataset, t_freq, lon_area, lat_area, resolution, time_period):
    folder_0 = Path(__file__).resolve().parents[3].name                                                                             # ex: models
    folder_1 = Path(__file__).resolve().parents[2].name                                                                             # ex: cmip
    folder_2 = Path(__file__).resolve().parents[1].name                                                                             # ex: metric_group
    folder_3 = Path(__file__).resolve().parents[0].name                                                                             # ex: metric
    folder_4 = dataset                                                                                                              # ex: dataset
    # [print(f) for f in [t_folder, mg_folder, dg_folder, m_folder]]                                                                #
    # exit()                                                                                                                        #
    r_folder        = f'{folder_0}/{folder_1}/{folder_2}/{folder_3}/{folder_4}'                                                     # result_folder dir
    r_filename      = (                                                                                                             # base result_filename
                      f'{folder_3}'                                                                                                 #
                      f'_{dataset}'                                                                                                 #
                      f'_{t_freq}'                                                                                                  #
                      f'_{lon_area.split(":")[0]}-{lon_area.split(":")[1]}'                                                         #
                      f'_{lat_area.split(":")[0]}-{lat_area.split(":")[1]}'                                                         #
                      f'_{int(360/resolution)}x{int(180/resolution)}'                                                               #
                      f'_{time_period.split(":")[0]}_{time_period.split(":")[1]}'                                                   #
                      )                                                                                                             #
    return r_folder, r_filename

