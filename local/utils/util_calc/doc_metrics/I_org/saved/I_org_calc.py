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


# == finding cores ==
# -- smoothing: distance decay --
def apply_smoothing(da_in, kernel_size, decay_distance):
    x, y = np.meshgrid(np.arange(kernel_size), np.arange(kernel_size))                                                          # window to smooth over
    dist = np.sqrt((x - kernel_size//2)**2 + (y - kernel_size//2)**2)                                                           #
    kernel = np.exp(-dist / decay_distance)                                                                                     # rate of decay
    kernel /= kernel.sum()                                                                                                      #
    da_out = convolve(da_in, kernel, mode='nearest')                                                                            # returns numpy, so put in xarray again later
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


# == observed cdf of NND ==
def haversine_dist(lat1, lon1, lat2, lon2):
    '''Great circle distance (from Haversine formula)
    input: 
    lon range: [-180, 180]
    lat range: [-90, 90]
    (Takes vectorized input) 

    Formula:
    h = sin^2(phi_1 - phi_2) + (cos(phi_1)cos(phi_2))sin^2(lambda_1 - lambda_2)
    (1) h = sin(theta/2)^2
    (2) theta = d_{great circle} / R    (central angle, theta)
    (1) in (2) and rearrange for d gives
    d = R * sin^-1(sqrt(h))*2 
    where 
    phi -latitutde
    lambda - longitude
    '''
    R = 6371                                                                                    # radius of earth in km
    lat1 = np.deg2rad(lat1)                                                                     # function requires degrees in radians 
    lon1 = np.deg2rad(lon1-180)                                                                 # and lon in range [-180, 180]
    lat2 = np.deg2rad(lat2)                                                                     #
    lon2 = np.deg2rad(lon2-180)                                                                 #
    h = np.sin((lat2 - lat1)/2)**2 + np.cos(lat1)*np.cos(lat2) * np.sin((lon2 - lon1)/2)**2     # Haversine formula
    h = np.clip(h, 0, 1)                                                                        # float point precision sometimes give error
    result =  2 * R * np.arcsin(np.sqrt(h))                                                     # formula rearranged for spherical distance
    return result

def get_observed_cdf(N_c, lat_coords, lon_coords, r_bin_edges):
    NN_distances = []
    for c in np.arange(0, N_c):
        pair_distances = haversine_dist(np.array([lat_coords[c]] * N_c), 
                                        np.array([lon_coords[c]] * N_c), 
                                        lat_coords, 
                                        lon_coords)                                             # distance to other convective points
        NN_distances.append(np.min(pair_distances[pair_distances > 0]))                         # distance to closest other convective gridbox
    NN_distances = np.array(NN_distances)                                                       # minimum distance of touching points is about 270 km
    sorted_NN_distances = np.sort(NN_distances)
    cumulative_sum = np.zeros_like(r_bin_edges)
    for i, val in enumerate(r_bin_edges):
        cumulative_sum[i] = np.sum(sorted_NN_distances <= val)
    obs_cdf = cumulative_sum / len(sorted_NN_distances)
    return obs_cdf, NN_distances


# == cdf of NND expected from random distribution ==
def get_area_matrix(lat, lon):
    ''' # area of domain: cos(lat) * (dlon * dlat) R^2 (area of gridbox decrease towards the pole as gridlines converge) '''
    lonm, latm = np.meshgrid(lon, lat)
    dlat = lat.diff(dim='lat').data[0]
    dlon = lon.diff(dim='lon').data[0]
    R = 6371     # km
    area =  np.cos(np.deg2rad(latm))*np.float64(dlon * dlat * R**2*(np.pi/180)**2) 
    da_area = xr.DataArray(data = area, dims = ["lat", "lon"], coords = {"lat": lat, "lon": lon}, name = "area")
    return da_area

def get_poisson_cdf(lamda, r_bin_edges, dx):
    ''' Expected cdf from random poisson process '''
    random_cdf = 1 - np.exp(-lamda * np.pi * (r_bin_edges)**2)                                       # cdf of random distribution
    return random_cdf

# == main ==
def main(da, lat_coords, lon_coords):
    # -- density of cores, and max NND --
    N_c = len(lat_coords)                                                                       # number of convective cores
    lamda = N_c / get_area_matrix(da.lat, da.lon).sum().data                                    # normalization factor (density of cores)
    lat = da.lat.data
    lon = da.lon.data
    dx_domain = haversine_dist(np.array([lat[int(len(lat)/2)]]), np.array([lon[0]]),               
                                   np.array([lat[int(len(lat)/2)]]), np.array([lon[int(len(lon)/2)]]))  # / 2 # if r exceeds half of the domain, the distance from the core will exceed the lon boundary (periodic)
    dy_domain = haversine_dist(np.array([lat[0]]),               np.array([lon[int(len(lon)/2)]]), 
                                   np.array([lat[-1]]),              np.array([lon[int(len(lon)/2)]]))    
    r_max = (dx_domain**2 + dy_domain**2)**(1/2)                                                        # theoretically maximum minimum distance

    dx = haversine_dist(np.array([lat[0]]), np.array([lon[0]]), np.array([lat[0]]), np.array([lon[1]])) * 4 # local mimima in 3x3 window, smallest step is 3 gridbox dist   
    r_bin_edges = np.arange(0, r_max, dx)

    # -- cdfs --
    random_cdf = get_poisson_cdf(lamda, r_bin_edges, dx)
    obs_cdf, NN_distances = get_observed_cdf(N_c, lat_coords, lon_coords, r_bin_edges)
    # print()
    # -- metric --
    i_org = np.trapz(obs_cdf, random_cdf)
    return i_org, obs_cdf, random_cdf, r_bin_edges


