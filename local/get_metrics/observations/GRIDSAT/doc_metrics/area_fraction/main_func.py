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
import calendar

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
gD = import_relative_module('util_obs.get_gridsat_data',    'utils')


# == process data ==
def post_process_data(da):
    ''
    return da

# == get metric ==
def get_metric(dataset, t_freq, lon_area, lat_area, resolution, time_period, years, months, r_folder, r_filename, section_range, test):    
    folder_work, folder_scratch, _, _, _ = mS.get_user_specs()
    count = 0                                                                                                                                               # for labelling snapshots
    current_year = None                                                                                                                                     # 
    metric = []                                                                                                                                             # initialize metric for year
    for i, (year, month) in enumerate(zip(years, months)):                                                                                                  #
        if year != current_year:                                                                                                                            # When finished one year, save
            if current_year is not None and metric:
                folder = f'{folder_work}/metrics/{r_folder}/{r_filename}'
                filename = f'{r_filename}_{current_year}_1-{current_year}_12.nc'
                path_result = f'{folder}/{filename}' 
                ds = xr.concat(metric, dim='time')
                print('concatenated section results')
                # -- save result from section --
                print(f'saving section results from: {dataset}')
                os.makedirs(os.path.dirname(path_result), exist_ok=True)
                ds.to_netcdf(path_result, mode="w")
                print('saved section result')
                metric = []                                                                                                                                 # reset metric 
            current_year = int(year)                                                                                                                        # start new year
        _, num_days = calendar.monthrange(int(year), int(month))
        days = list(range(1, num_days + 1))
        for day in days:
            # -- get data --      
            time_str =      f'{year}-{int(month):02d}-{int(day):02d}'
            process_request = ['irwin_cdr', 'GRIDSAT', time_str, t_freq, lon_area, lat_area, resolution]
            da = gD.get_data(process_request, process_data_further = post_process_data)               
            # -- get metric --     
            data_objects = [da, process_request, count]                                                                              
            metric.append(mC.calculate_metric(data_objects))
            print(f'finished year: {year} month: {month} day: {day}')
            count += 1
    if current_year is not None and metric:                                                                                                                 # save final year results
        folder = f'{folder_work}/metrics/{r_folder}/{r_filename}'
        filename = f'{r_filename}_{current_year}_1-{current_year}_12.nc'
        path_result = f'{folder}/{filename}' 
        ds = xr.concat(metric, dim='time')
        print('concatenated section results')
        # -- save result from final section --
        print(f'saving section results from: {dataset}')
        os.makedirs(os.path.dirname(path_result), exist_ok=True)
        ds.to_netcdf(path_result, mode="w")
        print('saved section result')


# == main ==
def main(switch, dataset, t_freq, lon_area, lat_area, resolution, time_period, years, months, r_folder, r_filename, section_range, test = False):
    if switch.get('calc'):
        get_metric(dataset, t_freq, lon_area, lat_area, resolution, time_period, years, months, r_folder, r_filename, section_range, test)
    print('finished')        


# == when this script is ran / submitted ==
if __name__ == '__main__':
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

