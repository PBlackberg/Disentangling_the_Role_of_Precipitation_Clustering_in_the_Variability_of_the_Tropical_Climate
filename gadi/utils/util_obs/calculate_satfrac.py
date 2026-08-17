#!usr/bin/env python3

"""
Column relative humidity (CRH) calculation
"""

import xarray as xr
import numpy as np
import pandas as pd
from dask.distributed import Client, LocalCluster
import warnings


R_d = 287                      # dry gas constant for earth's atmopshere
R_v = 461                      # gas cosntant for water vapour
eps = R_d/R_v                  # ratio of dry/moist gas constants


def saturation_vapour_pressure(T):
    """
    Bolton formula
    """
    return 611.2 * np.exp((17.67 * (T - 273.15)) / (T - 29.65))


def spec_hum(p, e):
    """
    converts vapour pressure to specific humidity
    """
    r = (eps * e) / (p - e)
    return r / (1 + r)


def calc_satfrac():

    for year in range(1979, 2022):
    
        print(year)
    
        # open 1 deg daily means
        q = xr.open_dataset(f'/g/data/k10/cb4968/era5_daily_means/qall/era5_q_daily_mean_{year}.nc')['q']
        T = xr.open_dataset(f'/g/data/k10/cb4968/era5_daily_means/tall/era5_t_daily_mean_{year}.nc')['t']
        
        # calculate satfrac
        es = saturation_vapour_pressure(T)
        qs = spec_hum(es.level*100, es)
        
        # sat frac = int(q) / int(qs)
        sat_frac = q.integrate('level') / qs.integrate('level')
    
        ## save outputs
        sat_frac.to_netcdf(f'/g/data/k10/cb4968/era5_daily_means/satfrac/era5_satfrac_daily_mean_{year}.nc', encoding={'satfrac': {'zlib': True, "complevel": 5}})
    
        # clear memory
        del q
        del T
    
        #break


if __name__ == "__main__":
    cluster = LocalCluster()
    client = Client(cluster)
    calc_satfrac()



