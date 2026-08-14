'''
# -----------------
#  plot_tropdomain
# -----------------

'''

# == imports ==
# -- Packages --
import numpy as np
import xarray as xr
from pathlib import Path
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
from cartopy.mpl.ticker import LongitudeFormatter, LatitudeFormatter
import matplotlib.ticker as ticker
from matplotlib.patches import Rectangle
from matplotlib.patheffects import withStroke


# == general plot funcs ==
def scale_ax(ax, scaleby):
    ax_position = ax.get_position()
    left, bottom, _1, _2 = ax_position.bounds                                                                                       # [left, bottom, width, height]
    new_width = _1 * scaleby
    new_height = _2 * scaleby
    ax.set_position([left, bottom, new_width, new_height])

def move_col(ax, moveby):
    ax_position = ax.get_position()             
    _, bottom, width, height = ax_position.bounds                                                                                   # [left, bottom, width, height]
    new_left = _ + moveby
    ax.set_position([new_left, bottom, width, height])

def move_row(ax, moveby):
    ax_position = ax.get_position()
    left, _, width, height = ax_position.bounds                                                                                     # [left, bottom, width, height]
    new_bottom = _ + moveby
    ax.set_position([left, new_bottom, width, height])


# == specific plot funcs ==
def plot_ticks(ax, xticks, yticks):
    # x-ticks
    ax.set_xticks(xticks, crs=ccrs.PlateCarree()) 
    ax.xaxis.set_major_formatter(LongitudeFormatter())
    ax.xaxis.set_tick_params(labelsize = 7)
    ax.xaxis.set_tick_params(length = 2)
    ax.xaxis.set_tick_params(width = 1)
    # ax.xaxis.set_tick_params(labelsize=0)
    # ax.set_xticklabels('')
    # y-ticks
    ax.set_yticks(yticks, crs=ccrs.PlateCarree())
    ax.yaxis.set_major_formatter(LatitudeFormatter())
    ax.yaxis.set_tick_params(labelsize = 7) 
    ax.yaxis.set_tick_params(length = 2)
    ax.yaxis.set_tick_params(width = 1)
    # ax.yaxis.set_tick_params(labelsize=0)
    # ax.set_yticklabels('')
    # both
    ax.yaxis.set_ticks_position('both')
    ax.tick_params(right = False)

def cbar_ax_below(fig, ax, h):
    ax_position = ax.get_position()
    w = 0.6
    cbar_ax = fig.add_axes([ax_position.x0 + (ax_position.width - ax_position.width * w) / 2,                                 # left
                            ax_position.y0 - 0.25,                                                                            # bottom
                            ax_position.width * w,                                                                            # width
                            ax_position.height * 0.15                                                                            # height
                            ])      
    cbar = fig.colorbar(h, cax = cbar_ax, orientation = 'horizontal')
    # cbar.ax.tick_params(labelsize = 7)
    formatter = ticker.ScalarFormatter(useMathText = True)
    formatter.set_scientific(True)
    formatter.set_powerlimits((-1, 1))
    # cbar.ax.yaxis.set_major_formatter(formatter)
    # cbar.ax.yaxis.get_offset_text().set_size(7)
    # cbar.ax.yaxis.set_offset_position('left')
    cbar.ax.xaxis.set_major_formatter(formatter)
    cbar.ax.xaxis.get_offset_text().set_size(7)
    # cbar.ax.xaxis.set_offset_position('left')
    return cbar_ax

def add_rectangles(ax, color = 'white', label = 'meso'):
    lon_areas = (                                                                                                                   # set lon extent
        '0:49',                                                                                                                   # Africa
        '50:99',                                                                                                                  # Indian Ocean
        '100:149',                                                                                                                # Maritime Continent
        '150:204',                                                                                                                # West / central Pacific    (55 degrees, 5 degrees wider)
        '205:259',                                                                                                                # East Pacific              (55 degrees, 5 degrees wider)
        '260:309',                                                                                                                # Amazon
        '310:359',                                                                                                                # Atlantic
        )               
    labels = (
        'Africa',                                                                              
        'Indian Ocean',                                                                                          
        'MTC',                                                                               
        'West Pacific',                                                                                                   
        'East Pacific',                                                                                                          
        'Amazon',                                                                                                              
        'Atlantic',                                                                                                               
        )              
    for lon_area, label in zip(lon_areas, labels):
        lon_start = int(lon_area.split(':')[0])
        lon_end = int(lon_area.split(':')[1])
        lat_start = -13
        lat_end = 13
        rect = Rectangle((lon_start, lat_start),                                        # (left, bottom)
                        lon_end - lon_start,                                            # width
                        abs(lat_start - lat_end),                                       # height
                        linewidth = 0.5, edgecolor=color, facecolor='none', 
                        transform=ccrs.PlateCarree(),
                        path_effects=[withStroke(linewidth = 1, foreground='black')])
        ax.add_patch(rect)
        ax.text((lon_start + lon_end) / 2, 
                lat_end + 0.25, 
                label, 
                fontsize = 6, transform = ccrs.PlateCarree(), 
                color = 'w', #''lightgrey', 
                weight = 'bold', ha = 'center', va = 'bottom',
                path_effects=[withStroke(linewidth = 2, foreground = 'black')]) 

def add_rectangles2(ax, color = 'white', label = 'meso'):
    # lon_start = 129
    # lon_end = 134
    lon_start = 115
    lon_end = 120
    lat_start = -3
    lat_end = 2
    rect = Rectangle((lon_start, lat_start),                                        # (left, bottom)
                    lon_end - lon_start,                                            # width
                    abs(lat_start - lat_end),                                       # height
                    linewidth = 0.25, edgecolor=color, facecolor='none', 
                    transform=ccrs.PlateCarree(),
                    path_effects=[withStroke(linewidth = 0.75, foreground='black')])
    ax.add_patch(rect)
    ax.text((lon_start + lon_end) / 2, 
             lat_end + 0.75, 
             label, 
             fontsize = 2.5, transform = ccrs.PlateCarree(), 
             color = 'w', #'lightgrey', 
             weight = 'bold', ha = 'center', va = 'bottom',
            path_effects=[withStroke(linewidth = 1, foreground = 'black')]) 


# == plot ==            
def plot(da_plot, da_ontop = None, lon_coords = [], lat_coords = [], lines = []):
    plt.rcParams['font.size'] = 7
    # -- create figure --    
    # width, height = 6.27, 9.69                                                                                                  # max size (for 1 inch margins)
    width, height = 15, 5                                                                                                        # max: 15.9, 24.5 for 1 inch margins [cm]
    width, height = [f / 2.54 for f in [width, height]]                                                                         # function takes inches
    ncols, nrows  = 1, 1
    fig, ax = plt.subplots(nrows, ncols, figsize = (width, height))
    ax.remove()
    projection = ccrs.PlateCarree(central_longitude = 180)
    ax = fig.add_subplot(nrows, ncols, 1, projection=projection)

    # -- format ax --
    lat, lon = da_plot.lat, da_plot.lon
    lonm,latm = np.meshgrid(lon, lat)
    ax.set_extent([lon[0], lon[-1], lat[0], lat[-1]], crs=ccrs.PlateCarree())
    xticks = [60, 120, 180, 240, 300]
    yticks = [-10, 0, 10]
    scale_ax(ax, 1.2)
    move_row(ax, 0.1)     
    move_col(ax, -0.069)
    plot_ticks(ax, xticks, yticks)
    ax.coastlines(resolution = "110m", linewidth = 0.6)

    # -- plot data --
    vmax = 2
    vmin = -2 
    h = ax.pcolormesh(lonm, latm, da_plot, 
                        transform=ccrs.PlateCarree(), 
                        # cmap = 'RdBu_r', 
                        cmap = "Greys_r", 
                        vmin = vmin, 
                        vmax = vmax
                        )
    
    lat, lon = da_ontop.lat, da_ontop.lon
    lonm,latm = np.meshgrid(lon, lat)
    h = ax.pcolormesh(lonm, latm, da_ontop, 
                    transform=ccrs.PlateCarree(),
                    cmap = 'Blues', 
                    vmin = 0, 
                    vmax = 10)
    ax.scatter(lon_coords, lat_coords, transform=ccrs.PlateCarree(), color = 'r', s = 0.75, marker='.', linewidths = 0)

    cbar_ax = cbar_ax_below(fig, ax, h)

    # add_rectangles(ax)
    # add_rectangles2(ax)

    # ax.contour(lonm, latm,      da_c, 
    #             transform =     ccrs.PlateCarree(),
    #             levels =        [da_c.quantile(0.50, dim=('lat', 'lon')).data],
    #             colors =        'k', 
    #             linewidths =    0.35)

    return fig, ax, cbar_ax








