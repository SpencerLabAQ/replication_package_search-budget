import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
import seaborn as sns
import pandas as pd

def get_initial(reliability):
    return pd.DataFrame([[0, reliability, 0]],
                        columns=['perfQ', 'reliability', '#changes'])

def sol_scatter(ax, df, marker, markersize, color, label=''):
    return ax.scatter(df['perfQ'], df['reliability'],
            s=df['#changes']*markersize, marker=marker, label=label,
            alpha=0.5, c=color)

def labels(ax, artists, hue):
    ax.set_xlabel('PerfQ', fontsize=28)
    ax.set_ylabel('Reliability', fontsize=28)
    ax.tick_params(axis='both', which='major', labelsize=16)
    #lgnd = plt.legend(loc='lower right', handletextpad=-0.3, fontsize=16)
    fake = Rectangle((0, 0), 1, 1, fc="w", fill=False, edgecolor='none', linewidth=0)
    lgnd = plt.legend([fake] + artists,
            [hue] + [a.get_label() for a in artists],
            loc='upper center', handletextpad=-0.3, fontsize=20,
            fancybox=True, shadow=False, ncol=len(artists)+1, bbox_to_anchor=(0.5, 1.1))
    for handle in lgnd.legendHandles[1:]:
        handle.set_sizes([50])

def plot_initial(ax, sol):
    ax.scatter(sol['perfQ'], sol['reliability'], s=75, marker='X', alpha=1, c='black')
    ax.annotate("initial", fontsize=14, xy=(sol['perfQ'], sol['reliability']), xycoords='data',
                xytext=(25, -25), textcoords='offset points', ha="left", va="center",
                arrowprops=dict(arrowstyle="wedge,tail_width=.01", facecolor='black'))

def plot_pareto(experiments, hue, initial=None, save_prefix=None,
        colors=[7, 0, 2, 3], markers=['s', 'o', '^', 'D', 'p'],
        legend_title=None):
    experiments.sort(key=lambda x: getattr(x, hue))

    fig, ax = plt.subplots(figsize=[10, 8])

    # Plot
    artists = []
    for i, exp in enumerate(experiments):
        ax.set_ylim([0, 1])
        #ax.set_xlim([-0.07, 0.27])
        artists.append(sol_scatter(ax, exp.df, markers[i], 50,
            color=[plt.cm.tab10(colors[i])], label=getattr(exp, hue)))

    # Initial solution
    if initial is not None:
        plot_initial(ax, initial)

    # Labels
    if legend_title is None:
        legend_title = hue
    labels(ax, artists, legend_title)

    # Grid
    ax.set_axisbelow(True)
    ax.xaxis.grid(color='gray', linestyle='dashed')
    ax.yaxis.grid(color='gray', linestyle='dashed')

    plt.tight_layout()

    filename = '{}_2dscatter.pdf'.format(save_prefix)
    plt.savefig(filename)
    print('Saved to: {}'.format(filename))
    return filename
