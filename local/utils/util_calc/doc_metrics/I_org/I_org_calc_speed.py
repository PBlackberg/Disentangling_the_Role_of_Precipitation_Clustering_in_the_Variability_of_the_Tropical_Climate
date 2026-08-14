''' 
# -----------------
#     I_org
# -----------------
paper: https://agupubs.onlinelibrary.wiley.com/doi/full/10.1002/2016ms000802

'''

# == imports ==
# -- packages --
import numpy as np
import xarray as xr
from scipy.ndimage import convolve
from scipy.ndimage import maximum_filter, minimum_filter
from numba import njit, prange
from numba import get_num_threads, set_num_threads


# == finding cores ==
# -- smoothing: distance decay --
def apply_smoothing(da_in, kernel_size, decay_distance):
    x, y = np.meshgrid(np.arange(kernel_size), np.arange(kernel_size))                          # window to smooth over
    dist = np.sqrt((x - kernel_size//2)**2 + (y - kernel_size//2)**2)                           # 
    kernel = np.exp(-dist / decay_distance)                                                     # rate of decay
    kernel /= kernel.sum()                                                                      #
    da_out = convolve(da_in, kernel, mode='nearest')                                            # returns numpy, so put in xarray again later
    da_out = xr.DataArray(data = da_out, dims=["lat", "lon"], coords={"lat": da_in.lat, "lon": da_in.lon},)
    return da_out

# -- local extrema --
def find_conv_cores(da, threshold, exceed_threshold = True, local_extrema_flag = 'max', window = 3):
    if local_extrema_flag == 'max':
        local_extrema = maximum_filter(da, size = window)
    elif local_extrema_flag == 'min':
        local_extrema = minimum_filter(da, size = window)
    else:
        local_extrema = da
    local_extrema = (da == local_extrema) * 1
    if exceed_threshold:
        if local_extrema_flag == 'max':
            local_extrema = (local_extrema * da) > threshold
        else:
            local_extrema = (local_extrema * da > 0) & (local_extrema * da < threshold)
    latitudes, longitudes = np.where(local_extrema)
    lat_coords = local_extrema.lat.values[latitudes]
    lon_coords = local_extrema.lon.values[longitudes]
    return lat_coords, lon_coords


# == distance calc ==
@njit(fastmath=True)
def haversine_h(c, k, sin_phi, cos_phi, sin_lam, cos_lam):
    '''Great circle distance (from Haversine formula): https://en.wikipedia.org/wiki/Haversine_formula
    input: 
    lon range: [-180, 180] doesnt actually matter
    lat range: [-90, 90]
    (Takes vectorized input) 

    Formula:
    h = sin^2((phi_1 - phi_2)/2) + (cos(phi_1)cos(phi_2))sin^2((lambda_1 - lambda_2)/2)
    (1) h = sin(theta/2)^2
    (2) theta = d_{great circle} / R    (central angle, theta)
    (1) in (2) and rearrange for d gives
    d = R * sin^-1(sqrt(h))*2 
    where 
    phi -latitutde
    lambda - longitude
    '''
    h = 0.5 * (1 - (cos_phi[c] * cos_phi[k] + sin_phi[c] * sin_phi[k])) + cos_phi[c] * cos_phi[k] * 0.5 * (1 - (cos_lam[c] * cos_lam[k] + sin_lam[c] * sin_lam[k])) # Haversine formula
    if h < 0.0:
        h = 0.0
    elif h > 1.0:
        h = 1.0
    return h

@njit(fastmath=True)
def find_h_min(c, sin_phi, cos_phi, sin_lam, cos_lam, h_bin_edges):
    c_h_min = 1.0
    for k in range(sin_phi.size):
        if k == c: 
            continue
        c_h = haversine_h(c, k, sin_phi, cos_phi, sin_lam, cos_lam)
        if c_h == 0:
            continue

        if c_h < h_bin_edges[1]: # in smallest bin
            c_h_min = c_h
            break

        if c_h < c_h_min:
            c_h_min = c_h
    return c_h_min

@njit(parallel=True, fastmath=True)
def core_NN_loop(h_bin_edges, sin_phi, cos_phi, sin_lam, cos_lam):
    NN_h = np.zeros(sin_phi.size, np.float64)                                                                                                                                          
    for c in prange(sin_phi.size):
        c_h_min = find_h_min(c, sin_phi, cos_phi, sin_lam, cos_lam, h_bin_edges)
        NN_h[c] = c_h_min
    return NN_h


# == main ==
def main(subdomain_area, r_bin_edges, h_bin_edges, sin_phi, cos_phi, sin_lam, cos_lam, count):
    # -- density of cores --
    lamda = sin_phi.size / subdomain_area                                                                                                                           # normalization factor (density of cores)

    # -- random cdf --
    random_cdf = 1 - np.exp(-lamda * np.pi * (r_bin_edges)**2)  

    # -- obs cdf --
    if sin_phi.size < 2:                                                                                                                                            # only calculate with enough cores
        obs_cdf = np.ones_like(random_cdf) * np.nan
        i_org = np.nan
    else:
        # -- numba loop --
        if count == 0:
            _ = core_NN_loop(h_bin_edges, sin_phi[:1], cos_phi[:1], sin_lam[:1], cos_lam[:1])                                                                       # warm-up
        NN_h = core_NN_loop(h_bin_edges, sin_phi, cos_phi, sin_lam, cos_lam)
        
        # -- cdf --
        s = np.sort(NN_h)
        obs_cdf = np.searchsorted(s, h_bin_edges, side="right") / s.size
        # -- metric --
        i_org = np.trapz(obs_cdf, random_cdf)                                                                                                                       # metric is area under obs cdf as a function of random cdf
    return i_org

 