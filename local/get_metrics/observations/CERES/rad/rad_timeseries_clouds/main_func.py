'''
# -----------------
#    Main_func
# -----------------

'''

# == imports ==
# -- Packages --
import importlib
import itertools
import xarray as xr

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
mS = import_relative_module('user_specs',                   'utils')
jS = import_relative_module('submit_as_job',                __file__)
mC = import_relative_module('calc_metric',                  __file__)
gD = import_relative_module('util_obs.get_ceres_data',      'utils')


# == process data ==
def post_process_data(da):
    ''
    # da = da.fillna(0)
    return da

# == get metric ==
def get_metric(dataset, t_freq, lon_area, lat_area, resolution, time_period, years, months, r_folder, r_filename, section_range, test):    
    folder_work, folder_scratch, _, _, _ = mS.get_user_specs()
    # print(r_folder)
    # print(r_filename)
    # exit()

    # -- get data --      
    vars_all = ['obs_cld_amount']
    vars_clr = ['obs_clr_toa_net']
    for var, var_clr in zip(vars_all, vars_clr):
        # -- all sky --  
        process_request = [var, dataset, time_period, t_freq, lon_area, lat_area, resolution]
        da = gD.get_data(process_request, process_data_further = post_process_data)        
        # print(da)
        data_objects = [da, process_request]                                                                              
        ds = mC.calculate_metric(data_objects)
        folder = f'{folder_work}/metrics/{r_folder}'
        filename = f'{r_filename}_{var}.nc'
        path = f'{folder}/{filename}'
        os.makedirs(os.path.dirname(path), exist_ok=True)
        ds.to_netcdf(path, mode="w")
        print(f'saved: {var}')

        # # -- clearsky --  
        # process_request_clr = [var_clr, dataset, time_period, t_freq, lon_area, lat_area, resolution]
        # da_clr = gD.get_data(process_request_clr, process_data_further = post_process_data)  
        # # print(da_clr)
        # data_objects = [da_clr, process_request]                                                                              
        # ds = mC.calculate_metric(data_objects)
        # folder = f'{folder_work}/metrics/{r_folder}'
        # filename = f'{r_filename}_{var}_clr.nc'
        # path = f'{folder}/{filename}'
        # os.makedirs(os.path.dirname(path), exist_ok=True)
        # ds.to_netcdf(path, mode="w")
        # print(f'saved: {var_clr}')

        # # -- all - clearsky --    
        # da_diff = da - da_clr
        # data_objects = [da_diff, process_request]                                                                              
        # ds = mC.calculate_metric(data_objects)
        # folder = f'{folder_work}/metrics/{r_folder}'
        # filename = f'{r_filename}_{var}-{var_clr}.nc'
        # path = f'{folder}/{filename}'
        # os.makedirs(os.path.dirname(path), exist_ok=True)
        # ds.to_netcdf(path, mode="w")
        # print(f'saved: {var}-{var_clr}')

# == main ==
def main(switch, dataset, t_freq, lon_area, lat_area, resolution, time_period, years, months, r_folder, r_filename, section_range, test = False):
    if switch.get('calc'):
        get_metric(dataset, t_freq, lon_area, lat_area, resolution, time_period, years, months, r_folder, r_filename, section_range, test)
    print('finished')        


# == when this script is ran / submitted ==
if __name__ == '__main__':
    # ds = xr.open_dataset('/Users/cbla0002/Desktop/work/metrics/observations/IMERG/doc_metrics/area_fraction/IMERG/area_fraction_IMERG_3hrly_0-360_-30-30_3600x1800_2001-01_2023-12/area_fraction_IMERG_3hrly_0-360_-30-30_3600x1800_2001-01_2023-12_2001_1-2001_12.nc')
    # print(ds)
    # x_var1 = '__xarray_dataarray_variable__'
    # da = ds[x_var1]
    # print(da)
    # exit()
    datasets, t_freqs, lon_areas, lat_areas, resolutions, time_periods = jS.set_specs()                                                                     # all specs
    for i, (t, lat, lon, r, d, p) in enumerate(itertools.product(t_freqs,                                                                                   #
                                                                lat_areas,                                                                                  #
                                                                lon_areas,                                                                                  #
                                                                resolutions,                                                                                #
                                                                datasets, time_periods)):                                                                   # loops over all specs (looped in input order)
        r_folder, r_filename = jS.get_path(d, t, lon, lat, r, p)
        print(f'Running metric for:')
        print(f'folder:     {r_folder}')
        print(f'filename:   {r_filename}')
        time_section = jS.get_timesections(n_jobs = 1, time_period = p)[0] 
        years_section, months_section = zip(*time_section)     
        year1_section, month1_section = time_section[0]
        year2_section, month2_section = time_section[-1]
        section_range =  f'{year1_section}_{month1_section}-{year2_section}_{month2_section}'   
        main(switch =              {'calc': True},
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
                test =             False,
                )
        # exit()



