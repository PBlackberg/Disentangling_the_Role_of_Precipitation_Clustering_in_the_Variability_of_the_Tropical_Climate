'''
# -------------------
#  plot_small_domain
# -------------------

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

# def cbar_ax_below(fig, ax, h):
#     ax_position = ax.get_position()
#     w = 0.8
#     cbar_ax = fig.add_axes([ax_position.x0 + (ax_position.width - ax_position.width * w) / 2,                                 # left
#                             ax_position.y0 - 0.15,                                                                            # bottom
#                             ax_position.width * w,                                                                            # width
#                             ax_position.height * 0.05                                                                            # height
#                             ])      
#     cbar = fig.colorbar(h, cax = cbar_ax, orientation = 'horizontal')
#     # cbar.ax.tick_params(labelsize = 7)
#     formatter = ticker.ScalarFormatter(useMathText = True)
#     formatter.set_scientific(True)
#     formatter.set_powerlimits((-1, 1))
#     # cbar.ax.yaxis.set_major_formatter(formatter)
#     # cbar.ax.yaxis.get_offset_text().set_size(7)
#     # cbar.ax.yaxis.set_offset_position('left')
#     cbar.ax.xaxis.set_major_formatter(formatter)
#     cbar.ax.xaxis.get_offset_text().set_size(7)
#     # cbar.ax.xaxis.set_offset_position('left')
#     return cbar_ax

def cbar_ax_right(fig, ax, h):
    ax_position = ax.get_position()
    c_h = 0.8
    cbar_ax = fig.add_axes([ax_position.x1 + 0.025,                                                                              # left
                            ax_position.y0 + (ax_position.height - ax_position.height * c_h) / 2,                               # bottom
                            ax_position.width * 0.05,                                                                          # width
                            ax_position.height * c_h                                                                            # height
                            ])      
    cbar = fig.colorbar(h, cax = cbar_ax, orientation='vertical')
    return cbar_ax

# == plot ==            
def plot(da_plot, da_ontop, lon_coords, lat_coords, lines = []):
    plt.rcParams['font.size'] = 7
    # -- create figure --    
    # width, height = 6.27, 9.69                                                                                                  # max size (for 1 inch margins)
    width, height = 8, 5                                                                                                        # max: 15.9, 24.5 for 1 inch margins [cm]
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

    xticks = [130, 131.5, 133]
    yticks = [-2, -0.5, 1]
    scale_ax(ax, 1)
    move_row(ax, 0.025)     
    move_col(ax, 0)
    plot_ticks(ax, xticks, yticks)
    ax.coastlines(resolution = "110m", linewidth = 0.6)

    # -- plot data --
    vmax = 2
    vmin = -2 
    h = ax.pcolormesh(lonm, latm, da_plot, 
                        transform=ccrs.PlateCarree(), 
                        cmap = 'Greys_r', 
                        vmin = vmin, 
                        vmax = vmax
                        )
    h = ax.pcolormesh(lonm, latm, da_ontop, 
                    transform=ccrs.PlateCarree(),
                    cmap = 'Blues', 
                    vmin = 0, 
                    vmax = 10)
    ax.scatter(lon_coords, lat_coords, transform=ccrs.PlateCarree(), color = 'r', s = 1, linewidths = 0)

    # cbar_ax = cbar_ax_below(fig, ax, h)
    cbar_ax = cbar_ax_right(fig, ax, h)

    return fig, ax, cbar_ax




# # -- create figure --
# width, height = 6.27, 9.69                      # max size (for 1 inch margins)
# width, height = 1 * width, 0.4 * height         # modulate size and subplot distribution
# ncols, nrows  = 1, 1
# fig, axes = plt.subplots(nrows, ncols, figsize = (width, height))

# title = (
#     f'time:{str(timestep.data)[2:18]}    '
#     # f'{x4_label}: {x4.sel(time = timestep).data:.2e} {x4_units}\n'
#     # f'{x2_label}: {x2.sel(time = timestep).data:.2e} {x2_units}               '
#     # f'{x3_label}: {x3.sel(time = timestep).data:.2e} {x3_units}'
#     )
# da_ontop = xr.where(conv_regions!= 0, 1, np.nan)    # .drop('time') 
# fig, ax = plot_subplot(title,
#                 fig = fig,
#                 nrows = nrows,
#                 ncols = ncols,
#                 axes = axes,
#                 ds = xr.Dataset({'var': -da_plot}), 
#                 # ds_contour = xr.Dataset({'var': pr_mean}), 
#                 ds_ontop = xr.Dataset({'var': da_ontop}), 
#                 lines = [],
#                 )
# ax.scatter(lon_coords, lat_coords, transform=ccrs.PlateCarree(), color = 'r', s = 1)


# def plot_subplot(title, fig, nrows, ncols, axes, ds, ds_contour, ds_ontop, lines):
#     # print(ds)
#     # print(ds['var'])
#     # exit()

#     # -- add subplot settings --
#     xticks = [60, 120, 180, 240, 300]
#     yticks = [-20, 0, 20]
#     # print(ds)
#     ds.attrs.update({ 
#         # -- format axes --
#         'scale': 1.05, 'move_row': 0.125, 'move_col': 0.025,
#         'hide_colorbar': False, 'cbar_height': 0.035, 'cbar_pad': 0.2, 'cbar_label_pad': 0.175,   
#         'xlabel_pad': 0.15,   
#         'ylabel_pad': 0.085,
#         'axtitle_xpad': 0, 'axtitle_ypad': 0.05,

#         # -- format plot elements --
#         'vmin': -2, 'vmax': 2, 
#         'cmap': 'RdBu', 
    
#         # -- format text --
#         'cbar_label': f'std from mean [Nb]',                    'cbar_fontsize': 8, 'cbar_numsize': 6,             
#         'hide_xticks': False,   'xticks': xticks,               'xticks_fontsize': 6.5,
#         'hide_xlabel': False,   'xlabel_label': 'longitude',    'xlabel_fontsize': 6.5,
#         'hide_yticks': False,   'yticks': yticks,               'yticks_fontsize': 6,
#         'hide_ylabel': False,   'ylabel_label': 'latitude',     'ylabel_fontsize': 6.5,
#         'axtitle_label':        title,                          'axtitle_fontsize': 9,
#         'coastline_width': 0.6,
#         'line_dots_size': 0.1,
#         })
#     # print(ds)
#     # exit()
#     if ds_contour is not None:
#         ds_contour.attrs.update({
#             # -- contour --
#             'name': 'var', 
#             'threshold': [ds_contour["var"].quantile(0.5), ds_contour["var"].quantile(0.9)], 
#             'color': 'k', 
#             'linewidth': 0.5,
#             'contour_text_size': 4.5,
#             })

    # # -- plot subplot --
    # row, col = 0, 0
    # # [print(f) for f in [fig, nrows, ncols, row, col, axes, ds, ds_contour, ds_ontop, lines]]
    # # exit()

    # ax = pF.plot(fig, nrows, ncols, row, col, axes, ds, ds_contour, ds_ontop, lines)

    # return fig

# def plot_subplot(title, fig, nrows, ncols, axes, ds = None, ds_contour = None, ds_ontop = None, lines = []):
#     # print(ds)
#     # print(ds['var'])
#     # exit()

#     # -- add subplot settings --
#     xticks = [110, 120, 130, 140]
#     yticks = [-10, 0, 10]

#     # print(ds)
#     symbol = r'$\sigma$'
#     some_text = r'OLR$_{mean}$'
#     add_size = 4
#     ds.attrs.update({ 
#         # -- format axes --
#         'scale': 0.9, 'move_row': 0.12, 'move_col': 0.01,
#         'hide_colorbar': False, 'cbar_height': 0.035, 'cbar_pad': 0.12, 'cbar_label_pad': 0.1,   
#         'xlabel_pad': 0.09,   
#         'ylabel_pad': 0.085,
#         'axtitle_xpad': 0.015, 'axtitle_ypad': 0.015,

#         # -- format plot elements --
#         'vmin': -2, 'vmax': 2, 
#         # 'cmap': 'RdBu', 
#         # 'vmin': -925379.2375, 'vmax': 925379.2375, 
#         'cmap': 'GnBu',
#         # 'cmap': 'Blues',
#         # 'cmap': 'PuBu',

#         # -- format text --
#         'cbar_label': f'{symbol}(OLR) []', 'cbar_fontsize': 6 + add_size, 'cbar_numsize': 6 + add_size,             
#         'hide_xticks': False,   'xticks': xticks,               'xticks_fontsize': 6.5 + add_size,
#         'hide_xlabel': False,   'xlabel_label': 'longitude',    'xlabel_fontsize': 6.5 + add_size,
#         'hide_yticks': False,   'yticks': yticks,               'yticks_fontsize': 6 + add_size,
#         'hide_ylabel': False,   'ylabel_label': 'latitude',     'ylabel_fontsize': 6.5 + add_size,
#         'axtitle_label':        title,                          'axtitle_fontsize': 10 + add_size -1,
#         'coastline_width': 0.6,
#         'line_dots_size': 1,
#         })
#     # print(ds)
#     # exit()
#     if ds_contour is not None:
#         ds_contour.attrs.update({
#             # -- contour --
#             'name': 'var', 
#             'threshold': [ds_contour["var"].quantile(0.25)], # ds_contour["var"].quantile(0.9)], 
#             'color': 'g', 
#             'linewidth': 0.5,
#             'contour_text_size': 4.5,
#             })

#     row, col = 0, 0
#     # [print(f) for f in [fig, nrows, ncols, row, col, axes, ds, ds_contour, ds_ontop, lines]]
#     # exit()

#     ax = pF.plot(fig, nrows, ncols, row, col, axes, ds, ds_contour, ds_ontop, lines)
#     return fig, ax
