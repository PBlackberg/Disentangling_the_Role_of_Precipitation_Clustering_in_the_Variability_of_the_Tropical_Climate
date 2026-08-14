'''
# -----------------------------
#  L_org method visualization
# -----------------------------

'''

# == imports ==
# -- Packages --
import numpy as np
import xarray as xr
import cartopy.crs as ccrs
import matplotlib.pyplot as plt

# -- Imported scripts --
import os
import sys
import importlib
sys.path.insert(0, os.getcwd())
def import_relative_module(module_name, plot_path):
    ''' import module from relative path '''
    if plot_path == 'utils':
        cwd = os.getcwd()
        if not os.path.isdir(os.path.join(cwd, 'utils')):
            print('put utils folder in cwd')
            print(f'current cwd: {cwd}')
            print('exiting')
            exit()
        module_path = f"utils.{module_name}"        
    else:
        relative_path = plot_path.replace(os.getcwd(), "").lstrip("/")
        module_base = os.path.dirname(relative_path).replace("/", ".").strip(".")
        module_path = f"{module_base}.{module_name}"
    return importlib.import_module(module_path)
mS = import_relative_module('user_specs',                               'utils')
pF_M = import_relative_module('util_plot.get_subplot.map_subplot',      'utils')
doc = import_relative_module('I_org_calc',                              __file__)


def plot_scene(ds_map, lat_coords, lon_coords, filename = 'test'):
    width, height = 6.27, 9.69                      # max size (for 1 inch margins)
    width, height = 1.25 * width, 0.45 * height      # modulate size and subplot distribution
    ncols, nrows  = 1, 1
    fig, axes = plt.subplots(nrows, ncols, figsize = (width, height))
    xticks = [110, 120, 130, 140]
    yticks = [-10, 0, 10]
    ds_map.attrs.update({ 'scale': 1.2, 'move_row':-0.075, 'move_col': -0.09,                                                                    # format axes
    'name': f'var',                                                                                                                              # plot
    'vmin': 0, 'vmax': 1, 'cmap': 'Blues', 'cbar_height': 0.025, 'cbar_pad': 0.1,                                                                     # colorbar: position
    'hide_colorbar': True, 'cbar_label': f'', 'cbar_fontsize': 6.25, 'cbar_numsize': 6, 'cbar_label_pad': 0.085,                                # colorbar: label                
    'hide_xticks': True, 'xticks': xticks, 'xticks_fontsize': 6.5,                                                                                 # x-axis:   ticks
    'hide_xlabel': True, 'xlabel_label': 'longitude', 'xlabel_pad': 0.0785, 'xlabel_fontsize': 6,                                                 # x-axis:   label
    'hide_yticks': True, 'yticks': yticks, 'yticks_fontsize':  5.5,                                                                                # y-axis:   ticks
    'hide_ylabel': True, 'ylabel_label': 'latitude', 'ylabel_pad': 0.055, 'ylabel_fontsize': 5,                                                  # y-axis:   label
    'axtitle_label': f'MTC', 'axtitle_xpad': 0, 'axtitle_ypad': 0.01, 'axtitle_fontsize': 10,
    'line_dots_size': 0.1,
    'coastline_width': 0.6,
    })           
    row = 0
    col = 0
    ax = pF_M.plot(fig, nrows, ncols, row, col, ax = axes, ds = ds_map)
    ax.scatter(lon_coords, lat_coords, transform=ccrs.PlateCarree(), color = 'r', s = 2)
    folder = '/Users/cbla0002/local/utils/util_calc/doc_metrics/I_org/plots'
    path = f'{folder}/{filename}.png'
    fig.savefig(path)
    print(f'plot saved at: {path}')
    plt.close(fig)

def plot_line(x, y, y2, filename):
    fig = plt.figure(figsize=(6, 4))
    plt.plot(x, y,        label="Observed CDF", color="red",  linestyle = "--")
    plt.plot(x, y2,    label="Poisson CDF",  color='blue', linestyle = '--')
    plt.xlabel("NN Distance [km]")
    plt.ylabel("Cumulative Distribution Function (NNCDF)")
    plt.legend()
    plt.grid(True)
    plt.legend()
    # plt.xlim(0, x[y < 1].max())
    plt.xlim(0, 200)
    # plt.xlim(0, 500)
    folder = '/Users/cbla0002/local/utils/util_calc/doc_metrics/I_org/plots'
    path = f'{folder}/{filename}.png'
    fig.savefig(path)
    print(f'plot saved at: {path}')
    plt.close(fig)

def plot_line2(x, y, y2, filename):
    fig, ax = plt.subplots(figsize=(6, 6))
    ax.plot(y2, y, label="NNCDF as a function of expected from random", color="red", linestyle="-")
    ax.fill_between(y2, y, color="red", alpha=0.3, label="Area under CDF (I_org)")
    ax.plot([0, 1], [0, 1], label="1:1 Line, I_org = 0.5 means Random", color="k", linestyle="--")  # Reference line for perfect match
    ax.set_xlabel("Poisson CDF")
    ax.set_ylabel("Observed CDF")
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 2)
    ax.legend(loc="lower right")
    ax.grid(True)
    folder = '/Users/cbla0002/local/utils/util_calc/doc_metrics/I_org/plots'
    path = f'{folder}/{filename}.png'
    fig.savefig(path)
    print(f'plot saved at: {path}')
    plt.close(fig)


if __name__ == '__main__':
    # == settings ==
    switch = {
        'random':   False,
        'custom':   True,
        'real':     False
        }
    switch_plot = {
        'scene':    True,
        'metric':   True,
        }

    smoothing, kernel_size, decay_distance =            True,   6,      0.5         # for pre-process
    threshold, quantile, local_extrema_flag, window =   True,  0.95,   'max',  3   # for cores
    periodic_lon =                                      False

    ds = xr.open_dataset('/Users/cbla0002/local/utils/util_calc/doc_metrics/L_org/precip_icon_d3hp003_3hrly_0-360_-30-30_3600x1800_2020-04_2021-03_2020_4_1.nc')
    da = ds['var'].isel(time = 0)
    lon_area = '100:149'
    lat_area = '-13:13'  
    da = da.sel(lon = slice(int(lon_area.split(':')[0]), int(lon_area.split(':')[1])), 
                lat = slice(int(lat_area.split(':')[0]), int(lat_area.split(':')[1]))
                )
    lat = da.lat.data
    lon = da.lon.data
    dx_domain = doc.haversine_dist(np.array([lat[int(len(lat)/2)]]), np.array([lon[0]]),               np.array([lat[int(len(lat)/2)]]), np.array([lon[-1]])) # / 2 # if r exceeds half of the domain, the distance from the core will exceed the lon boundary (periodic)
    dy_domain = doc.haversine_dist(np.array([lat[0]]),               np.array([lon[int(len(lon)/2)]]), np.array([lat[-1]]),              np.array([lon[int(len(lon)/2)]]))    
    r_max = (dx_domain**2 + dy_domain**2)**(1/2)/2  # 3000 km
    r_bin_edges = np.arange(0, r_max, 10)

    # == get data ==
    # -- real data --
    da_orig = da.fillna(0)
    # -- random --
    if switch.get('random'):
        random_noise = np.random.normal(loc = 0.0, scale = 0.01, size = (len(da_orig.lat), len(da_orig.lon)))
        da = xr.DataArray(data = random_noise, dims=["lat", "lon"], coords={"lat": da_orig.lat, "lon": da_orig.lon})
    # -- custom --
    if switch.get('custom'):
        clustered_field = np.zeros_like(da_orig)
        radius = 20
        # cluster_centers = [
        #     (int(0.75 * da_orig.lat.size), int(0.25 * da_orig.lon.size)),
        #     (int(0.75 * da_orig.lat.size), int(0.75 * da_orig.lon.size)),

        #     (int(0.25 * da_orig.lat.size), int(0.25 * da_orig.lon.size)),
        #     (int(0.25 * da_orig.lat.size), int(0.75 * da_orig.lon.size)),
        #     ]
        
        cluster_centers = [
            (int(0.65 * da_orig.lat.size), int(0.4 * da_orig.lon.size)),
            (int(0.65 * da_orig.lat.size), int(0.6 * da_orig.lon.size)),

            (int(0.35 * da_orig.lat.size), int(0.4 * da_orig.lon.size)),
            (int(0.35 * da_orig.lat.size), int(0.6 * da_orig.lon.size)),
            ]

        for center in cluster_centers:
            x, y = center
            for i in range(x - radius, x + radius):
                for j in range(y - radius, y + radius):
                    if 0 <= i < 260 and 0 <= j < 490:
                        clustered_field[i, j] = np.random.uniform(0, 2)
        da = clustered_field # + random_noise
        da = xr.DataArray(data = da, dims=["lat", "lon"], coords={"lat": da_orig.lat, "lon": da_orig.lon})
    # -- real --
    if switch.get('real'):
        da = da_orig

    # == find cores ==
    if threshold:
        exceed_threshold = True
        threshold = da.quantile(quantile).values
    else:
        exceed_threshold = False
        threshold = 0
    if smoothing:
        da = doc.apply_smoothing(da, kernel_size, decay_distance)
    lat_coords, lon_coords = doc.find_conv_cores(da, threshold, exceed_threshold, local_extrema_flag, window)

    # == plot scene ==
    if switch_plot.get('scene'):
        ds_map = xr.Dataset({'var': da})
        plot_scene(ds_map, lat_coords, lon_coords, filename = 'scene')

    # == plot metric ==
    if switch_plot.get('metric'):
        i_org, obs_cdf, random_cdf, r = doc.main(da, lat_coords, lon_coords)

        # print(len(obs_cdf))
        # print(len(random_cdf))
        # exit()

        plot_line(x = r, 
                y = obs_cdf, 
                y2 = random_cdf, 
                filename = 'metric')

        plot_line2(x = r, 
                y = obs_cdf, 
                y2 = random_cdf, 
                filename = 'metric2')




