import re
from glob import glob
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import sys
from statistics import mean, stdev
from math import floor

DATA_DIR = 'data'
SB_DIR = DATA_DIR + '/search_budget_stats'
QI_DIR = DATA_DIR + '/quality_indicators'
FIGS = 'figs/'

class Experiment:
    def __init__(self, file):
        self.file = file
        self.run = self.get_run()
        self.read()
        if hasattr(self, 'algorithm'):
            self.associate_qi()
    def get_run(self):
        return int(re.match(r'.+_(\d+)\.csv', self.file).group(1))
    def read(self):
        df = pd.read_csv(self.file)
        if df.shape[0] == 0:
            print('Empty file: {}'.format(self.file), file=sys.stderr)
            return
        data = df.iloc[0]
        self.algorithm = data['algorithm']
        self.iteration = data['iteration']
        self.max_iterations = data['max_iteration']
        m = re.match(r'(?P<casestudy>[^_]+)__.+sbth_(?P<time>[^_]+)_.+',
                data['problem_tag'])
        if m is not None:
            kv = m.groupdict()
            self.casestudy = kv['casestudy']
            if data['search_busget'] != 'none':
                self.time = int(kv['time'])
        else:
            print('Unable to parse: {}'.format(self.file), file=sys.stderr)
    def associate_qi(self):
        qi_glob = QI_DIR + '/qi__{}-{}{}__*.csv'\
            .format(self.algorithm.lower(), self.casestudy,
                    '-bytime-' + str(self.time) if hasattr(self, 'time') else '')
        if not hasattr(self, 'time'):
            self.time = 0
        qi_files = [f for f in glob(qi_glob)]
        if len(qi_files) != 6:
            print('Matched {} QI files!'.format(len(qi_files)), file=sys.stderr)
            print('Pattern:', qi_glob)
            for qi in qi_files:
                print(qi)
            return
        for qi in qi_files:
            qi_name = re.match(r'.+__([^\.]+)\.csv', qi).group(1)
            # using two newlines as delimiter
                    
            # qi_values = np.loadtxt(qi, delimiter = '\n\n', dtype=float)
            qi_values = np.genfromtxt(qi, delimiter = '\n\n', dtype=float)


            if len(qi_values) != 31:
                return
            setattr(self, qi_name, qi_values[self.run - 1])


def stem(x, y, ax, color):
    markerline, stemline, baseline = ax.stem(x, y, basefmt="k-")
    plt.setp(markerline, mec="k", mfc="w", zorder=3)
    plt.setp(stemline, color=color, alpha=1)
    markerline.set_ydata([0] * len(y))

def save(prefix, suffix):
    filename = '{}_{}'.format(prefix, suffix)
    plt.savefig(filename)
    print('Saved to: {}'.format(filename))

def timeline_aggregated(df, qi, save_prefix=None):
    fig, ax = plt.subplots(figsize=(12, 4), constrained_layout=True)
    colors = [7, 0, 2, 3]

    df = df[df['iter avg'] != 102]
    for i, algo in enumerate(sorted(df['algo'].unique())):
        d = df[df['algo'] == algo].sort_values(by=['time'])
        x = d['iter avg']
        y = d['qi avg']
        stem(x, y, ax, plt.cm.tab10(colors[i]))

        # Labels
        for i, p in enumerate(x):
            row = d[d['iter avg'] == p].iloc[0]
            x_offset = 3
            # ugly exception
            if df['casestudy'].iloc[0] == 'train-ticket' and algo == 'NSGAII' and i == 0:
                x_offset = -38
            ax.annotate('{}\n{} min'.format(row['algo'],
                int(int(row['time'])/1000/60)),
                textcoords='offset points', xytext=(x_offset, 0),
                xy=(p, y.iloc[i]), va='top')

        # Error
        s_x = [i for i in x for _ in range(2)]
        s_y = []
        for _, r in d.iterrows():
            s_y.append(r['qi avg'] - r['qi stdev'])
            s_y.append(r['qi avg'] + r['qi stdev'])
        ax.scatter(s_x, s_y, color='k', marker='_', alpha=0.5)

    ax.set_xticks([i for i in range(
        floor(min(df['iter avg'])), floor(max(df['iter avg'])) + 2, 2)])
    ax.set_xlim([ax.get_xlim()[0], ax.get_xlim()[1]*1.02])
    ax.grid(axis='y', linestyle='dashed', zorder=0)

    ax.set_xlabel('Average number of performed evolutions', fontsize=14)
    ax.set_ylabel('Average ' + qi, fontsize=14)

    if save_prefix is not None:
        save(save_prefix, 'timeline.pdf')
    else:
        plt.show()

case_studies = {
    'ttbs': 'train-ticket',
    'cocome': 'simplified-cocome',
}

# Read all the files
exps = [Experiment(f) for f in glob(SB_DIR + '/*.csv')]
exps = [e for e in exps if hasattr(e, 'algorithm')]
#exps = [e for e in exps if hasattr(e, 'HV')]

# Plot the timelines
qis = ['HV', 'IGD', 'IGD+', 'EP', 'SPREAD', 'GSPREAD']
cols = ['casestudy', 'algo', 'time', 'runs', 'iter avg', 'iter stdev', 'qi avg', 'qi stdev']
for qi in qis:
    exps = [e for e in exps if hasattr(e, 'HV')]
    for cs in case_studies.values():
        data = []
        exps_by_cs = [e for e in exps if e.casestudy == cs]
        for algo in set([e.algorithm for e in exps_by_cs]):
            for time in set([e.time for e in exps_by_cs]):
                exp_v = [e for e in exps_by_cs
                        if e.algorithm == algo and e.time == time]
                qi_values = [getattr(e, qi) for e in exp_v]
                iterations = [float(e.iteration) for e in exp_v]
                data.append([cs, algo, time, len(qi_values), mean(iterations),
                    stdev(iterations), mean(qi_values), stdev(qi_values)])
        df = pd.DataFrame(data, columns=cols)
        timeline_aggregated(df, qi, save_prefix='{}{}_{}'.format(FIGS, cs, qi))
        df = df.sort_values(by=['algo', 'time'])
        df['time'] = df['time'].apply(lambda x: '{} min'.format(int(x / 1000 / 60)))
        df['qi avg'] = df['qi avg'].apply(lambda x: round(x, 4))
        df['qi stdev'] = df['qi stdev'].apply(lambda x: round(x, 4))
        print(df.to_markdown(index=False))
        print()
