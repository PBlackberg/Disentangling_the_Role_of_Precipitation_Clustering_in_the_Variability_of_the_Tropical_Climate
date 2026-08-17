

# == imports ==
# -- Packages --
import numpy as np
import xarray as xr
from pathlib import Path
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
from cartopy.mpl.ticker import LongitudeFormatter, LatitudeFormatter
import matplotlib.ticker as ticker
from scipy.stats import pearsonr

# -- Imported scripts --
import os
import sys
import importlib


def scale_ax(ax, scaleby):
    ax_position = ax.get_position()
    left, bottom, _1, _2 = ax_position.bounds                                                                                       # [left, bottom, width, height]
    new_width = _1 * scaleby
    new_height = _2 * scaleby
    ax.set_position([left, bottom, new_width, new_height])

def scale_ax_x(ax, scaleby):
    ax_position = ax.get_position()
    left, bottom, _1, _2 = ax_position.bounds
    new_width = _1 * scaleby
    new_height = _2
    ax.set_position([left, bottom, new_width, new_height])

def scale_ax_y(ax, scaleby):
    ax_position = ax.get_position()
    left, bottom, _1, _2 = ax_position.bounds
    new_width = _1 
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




def format_xticks(ax, xmin, xmax):
    ax.set_xlim([xmin, xmax])
    # formatter_x = ticker.ScalarFormatter(useMathText=True)
    # formatter_x.set_scientific(True)
    # formatter_x.set_powerlimits((-1, 1))
    # ax.xaxis.set_major_formatter(formatter_x)
    ax.tick_params(axis='both', which='major', labelsize = 8)
    # ax.xaxis.get_offset_text().set_size(8)
    # ax.get_xaxis().get_offset_text().set_ha('right')

def format_yticks(ax, ymin, ymax):
    ax.set_ylim([ymin, ymax])
    # formatter_y = ticker.ScalarFormatter(useMathText=True)
    # formatter_y.set_scientific(True)
    # formatter_y.set_powerlimits((-1, 1))
    # ax.yaxis.set_major_formatter(formatter_y)
    ax.tick_params(axis='both', which='major', labelsize = 8)
    # ax.yaxis.get_offset_text().set_size(8)
    # ax.get_yaxis().get_offset_text().set_ha('right')

def cbar_ax_below(fig, ax, h):
    ax_position = ax.get_position()
    w = 0.5
    cbar_ax = fig.add_axes([ax_position.x0 + (ax_position.width - ax_position.width * w) / 2,                                   # left
                            ax_position.y0 - 0.25,                                                                              # bottom
                            ax_position.width * w,                                                                              # width
                            ax_position.height * 0.1 / 2                                                                        # height
                            ])      
    cbar = fig.colorbar(h, cax = cbar_ax, orientation = 'horizontal')
    # ticks = cbar.ax.get_yticks()    
    # try:
    #     ticklabels = [f'{int(t)}' for t in ticks]
    #     cbar.set_ticks(ticks)
    #     cbar.set_ticklabels(ticklabels)
    # except:
    #     pass
    cbar.ax.tick_params(labelsize = 8)
    # formatter = ticker.ScalarFormatter(useMathText = True)
    # formatter.set_scientific(True)
    # formatter.set_powerlimits((-1, 1))
    # cbar.ax.xaxis.set_major_formatter(formatter)
    # cbar.ax.xaxis.get_offset_text().set_size(8)
    # cbar.ax.xaxis.set_offset_position('left')
    return cbar_ax


def plot_xlabel(fig, ax, text):
    ax_position = ax.get_position()
    ax.text(ax_position.x0 + (ax_position.x1 - ax_position.x0) / 2, # + 0.05, # + (ax_position.x1 - ax_position.x0) / 2, 
            ax_position.y0 - 0.15, 
            text, 
            ha = 'center', 
            fontsize = 7, 
            transform = fig.transFigure
            )
    
def plot_ylabel(fig, ax, text):
    ax_position = ax.get_position()
    ax.text(ax_position.x0 - 0.185 - 0.05, 
            ax_position.y0 + (ax_position.y1 - ax_position.y0) / 2, 
            text, 
            va = 'center', 
            rotation = 'vertical', 
            fontsize = 7, 
            transform = fig.transFigure
            )

def plot_cbar_label(fig, ax, text):
    ax_position = ax.get_position()
    ax.text(ax_position.x0 + (ax_position.width * 0.5), 
            ax_position.y0 - 0.15, 
            text, 
            ha = 'center', 
            fontsize = 7, 
            transform = fig.transFigure
            )
    


def plot_a_scatter(x, y, z, ii, lower_bound, upper_bound, r_bin_lim, month = None):
    # -- create figure --    
    width, height = 5, 5.25
    width, height = [f / 2.54 for f in [width, height]] # convert to inches
    ncols, nrows  = 1, 1
    fig, ax = plt.subplots(nrows, ncols, figsize = (width, height))

    # -- format ax --
    scale_ax_x(ax, 0.8)
    scale_ax_y(ax, 0.6)
    move_row(ax, 0.35)     
    move_col(ax, 0.15)
    ax.spines['right'].set_visible(False)
    ax.spines['top'].set_visible(False)

    xmax = None
    xmin = None
    ymax = None
    ymin = None
    vmax = None #45 #None #75 #None #7.5e-2
    vmin = None #85 #None #25 #-vmax

    h = ax.scatter(x, y, c = z, cmap = 'RdBu', s = 10, vmin = vmin, vmax = vmax)

    cbar_ax = cbar_ax_below(fig, ax, h)
    format_xticks(ax, xmin, xmax)
    format_yticks(ax, ymin, ymax)

    # show bin
    ax.axvline(lower_bound, color="k", linestyle="--")
    ax.axvline(upper_bound, color="k", linestyle="--")
    ax.axvspan(lower_bound, upper_bound, color="purple", alpha=0.3)

    text = 'Af [%]'
    plot_xlabel(fig, ax, text)
    text = f'Am' #N_connect_{r_bin_lim}km [Nb]'
    plot_ylabel(fig, ax, text)
    text = rf'CRH [%]' 
    plot_cbar_label(fig, cbar_ax, text)

    # -- save figure --
    # folder = f'/scratch/k10/cb4968/temp_plots/imerg_gradient_scatter_r_bin_lim_{r_bin_lim}'
    folder = f'/scratch/k10/cb4968/temp_plots/imerg_gradient_scatter_month_{month}_r_bin_lim_{r_bin_lim}'

    if month == None:
        filename = f'snapshot_bin_{ii}.png'
    else:
        filename = f'snapshot_month_{month}_bin_{ii}.png'
    path = f'{folder}/{filename}'
    os.makedirs(os.path.dirname(path), exist_ok = True)
    os.remove(path) if os.path.exists(path) else None
    fig.savefig(path, dpi = 500)  
    print(f'plot saved at: {path}')
    plt.close(fig)
    # exit()






