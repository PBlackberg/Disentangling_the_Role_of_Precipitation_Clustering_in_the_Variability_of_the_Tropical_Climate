'''
# ------------
#  util_calc
# ------------

'''

# == imports ==
import xarray as xr
import numpy as np


# == calc ==
# -- mean_area --
def get_mean_area(labels):
    counts = np.bincount(labels.ravel())[1:]         # skip background 0
    return counts.mean()
    

# == when this script is ran ==
if __name__ == '__main__':
    print('executes')




