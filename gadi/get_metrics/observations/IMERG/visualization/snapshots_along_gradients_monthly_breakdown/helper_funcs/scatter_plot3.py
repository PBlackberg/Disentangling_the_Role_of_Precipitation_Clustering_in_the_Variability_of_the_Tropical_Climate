# == imports ==
# -- Packages --
import os
import numpy as np
import matplotlib.pyplot as plt


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

def cbar_ax_right(fig, ax, h):
    ax_position = ax.get_position()
    c_h = 0.9
    cbar_ax = fig.add_axes([ax_position.x1 + 0.025,                                                                              # left
                            ax_position.y0 + (ax_position.height - ax_position.height * c_h) / 2,                               # bottom
                            ax_position.width * 0.05,                                                                          # width
                            ax_position.height * c_h                                                                            # height
                            ])      
    cbar_ax.tick_params(labelsize=5)
    cbar = fig.colorbar(h, cax = cbar_ax, orientation='vertical')
    cbar.ax.yaxis.set_major_formatter('{:.2f}'.format)
    return cbar_ax


def plot_a_scatter(x, y, fig, ax, month, r_bin_lim, ii, idx_t):
    fig.text(0.5, 0.85, r'KDE [$\sigma^{-2}$]', 
        transform=fig.transFigure,
        fontsize=5
        )

    scale_ax(ax, 0.8)
    scale_ax_x(ax, 0.9)
    move_row(ax, 0.09)     
    move_col(ax, 0.075)

    # density of datapoints
    import seaborn as sns
    h = sns.kdeplot(x=x, y=y, fill=True, levels=50, cmap='RdBu_r', ax=ax)

    # print(x)
    # print(y)
    # exit()
    # fig, ax = plt.subplots()
    ax.tick_params(axis='both', labelsize=5)

    text_sigma = r'$\sigma$'
    # -- plot scatter --
    # plt.scatter(x, y, s=2, alpha=0.4, edgecolors='none') #, color = 'b')
    plt.xlabel(f'At [{text_sigma}]', fontsize = 5)
    plt.ylabel(f'Am [{text_sigma}]', fontsize = 5)

    # -- add linear area fraction change --
    m, b = np.polyfit(x, y, 1)
    x_line = np.linspace(x.min(), x.max(), 100)
    y_line = m * x_line + b
    ax.plot(x_line, y_line, color = 'k', lw=1, label = 'Coverage')

    # -- add residual direction vector --
    y_hat = m * x + b
    res = y - y_hat
    L = np.std(res)
    x0, y0 = x.mean(), y.mean()
    ax.plot([x0, x0], [y0 - L, y0 + L], color='grey', lw=1, label = 'Proximity')


    # ax.annotate('', xy=(x0, y0 + L), xytext=(x0, y0 - L),
    #             arrowprops=dict(arrowstyle='->', color='grey', lw=1))

    # # -- covariance + eigenvectors --
    # cov = np.cov(np.vstack([x, y]))
    # eigvals, eigvecs = np.linalg.eigh(cov)
    # idx = np.argsort(eigvals)[::-1]
    # eigvals = eigvals[idx]
    # eigvecs = eigvecs[:, idx]
    # x0 = x.mean()
    # y0 = y.mean()
    # # PC1
    # t1 = np.linspace(-2*np.sqrt(eigvals[0]), 2*np.sqrt(eigvals[0]), 100)
    # x_pca1 = x0 + t1 * eigvecs[0, 0]
    # y_pca1 = y0 + t1 * eigvecs[1, 0]
    # ax.plot(x_pca1, y_pca1, color='black', lw=0.5, label = 'PC1-2')
    # # PC2
    # t2 = np.linspace(-2*np.sqrt(eigvals[1]), 2*np.sqrt(eigvals[1]), 100)
    # x_pca2 = x0 + t2 * eigvecs[0, 1]
    # y_pca2 = y0 + t2 * eigvecs[1, 1]
    # ax.plot(x_pca2, y_pca2, color='black', lw=0.5)

    # -- other format --
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    cbar = ''
    # ax.set_title('Mean area vs area_fraction scatter', fontsize = 5, pad=2)
    ax.legend(loc='upper left', fontsize=3, frameon=False)
    
    # add colorbar
    mappable = ax.collections[0]   # or h.collections[0]
    cbar_ax = cbar_ax_right(fig, ax, mappable)


    if idx_t is not None:
        for n, idx in enumerate(idx_t):
            ax.text(
                x[idx], y[idx], str(n),
                color='green',
                fontsize=5,
                ha='center',
                va='center',
                zorder=10
            )


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

    return fig, ax, cbar



