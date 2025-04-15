from plots import *
import pandas as pd
from os.path import basename
from glob import glob
import re

DATA_DIR = 'data/reference_paretos'
FIGS = 'figs/'

initials = {
    'ttbs':   get_initial(0.657925),
    'cocome': get_initial(0.7630625563279512),
}
initials['train-ticket'] = initials['ttbs']
initials['simplified-cocome'] = initials['cocome']

class Pareto:

    def __init__(self, file):
        self.file = file
        self.parse_filename()
        self.read_rf()

    def parse_filename(self):
        m = re.match(r'(?P<algo>[^-]+)-(?P<usecase>.+)-bytime-(?P<time>\d+).rf',
                basename(self.file))
        if m is not None:
            for k, v in m.groupdict().items():
                setattr(self, k, v)
        self.algo = self.algo.upper()

    def read_rf(self):
        df = pd.read_csv(self.file, header=0,
                names=['perfQ', '#changes', '#PAs', 'reliability'])
        self.df = Pareto.fix_perfq_rel(df)
        return self.df

    @staticmethod
    def fix_perfq_rel(df):
        if 'perfQ' in df:
            df['perfQ'] = df['perfQ'] * -1
        if 'reliability' in df:
            df['reliability'] = df['reliability'] * -1
        return df

experiments = [Pareto(f) for f in glob(DATA_DIR + '/*-bytime-[0-9]*.rf')]

for cs in set([p.usecase for p in experiments]):
    for time in set([p.time for p in experiments]):
        exp = [p for p in experiments if p.usecase == cs and p.time == time]
        plot_pareto(exp, 'algo', initial=initials[cs],
            save_prefix='{}{}_{}'.format(FIGS, cs, time),
            legend_title='Algorithm')
