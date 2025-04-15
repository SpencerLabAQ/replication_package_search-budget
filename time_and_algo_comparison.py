from glob import glob
import numpy as np
import pandas as pd
import re
from os.path import basename
from scipy.stats import mannwhitneyu, rankdata
from itertools import permutations, combinations

DATA_DIR = 'data/quality_indicators'
TABLES_DIR = 'tables'

algo_names = {'nsgaii': '\\nsga', 'pesa2': '\\pesa', 'spea2': '\\spea'}
to_minimize = ['IGD', 'IGD+', 'SPREAD', 'GSPREAD']

class Experiment:
    def __init__(self, file):
        self.file = file
        self.values = np.genfromtxt(file, delimiter = '\n\n', dtype=float)
        m = re.match(r'qi__(?P<algo>[^-]+)-(?P<casestudy>.+)-bytime-(?P<time>\d+)__(?P<qi>HV|IGD|IGD\+|EP|SPREAD|GSPREAD).csv', basename(file))
        if m is not None:
            for k, v in m.groupdict().items():
                setattr(self, k, v)
        else:
            print('Cannot parse {}.'.format(file))

        self.time = '{} min'.format(int(int(self.time) / 1000 / 60))
        self.algo = algo_names[self.algo]
        
        self.mean_value = np.mean(self.values)
        self.stdv_value = np.std(self.values)
        
        if self.qi in to_minimize:
            self.values = -self.values
        

def a12(sample1, sample2):
    m = len(sample1)
    n = len(sample2)
    r1 = sum(rankdata(np.concatenate([sample1,sample2]))[:m])
    return (2 * r1 - m * (m + 1)) / (2 * n * m)

def interpret_a12(a12):
    levels = [0.147, 0.33, 0.474]
    magnitude = ["N", "S", "M", "L"]
    scaled_a12 = (a12 - 0.5) * 2
    return magnitude[np.searchsorted(levels, abs(scaled_a12))]

def compare(exps, group_by, criteria):
    group = set([getattr(e, group_by) for e in exps])
    res = []
    for g in group:
        exps_by_group = [e for e in exps if getattr(e, group_by) == g]
        pms = combinations(exps_by_group, r=2)
        for pm in pms:
            mwu = mannwhitneyu(pm[0].values, pm[1].values)
            a12_ = a12(pm[0].values, pm[1].values)
            a12_m = interpret_a12(a12_)
            res.append([g, getattr(pm[0], criteria), getattr(pm[1], criteria),
                mwu.pvalue, a12_, a12_m])
    df = pd.DataFrame(res, columns=[group_by, criteria + ' 1', criteria + ' 2',
            'MWU p', '\\vda', 'magn.'])
    df.sort_values([group_by, criteria + ' 1', criteria + ' 2'], inplace=True)
    return df

# Function to format LaTeX for each row
def format_latex(row):
    # Bold MWU p if significant (< 0.05)
    if row['MWU p'] < 0.001:
        mwu_p = f"\\textbf{{{row['MWU p']:.1e}}}"
    elif row['MWU p'] < 0.05:
        mwu_p = f"\\textbf{{{row['MWU p']:.4f}}}"
    else:
        mwu_p = f"{row['MWU p']:.4f}"
    
    # Format VDA as \ebar with magnitude
    abs_diff = abs(0.5 - row['\\vda'])
    effect_size = f"({row['magn.']}) \\ebar{{{row['\\vda']:.4f}}}{{{abs_diff:.4f}}}"
    
    # Underline algorithms based on conditions
    if row['MWU p'] < 0.05:  # Significant difference
        algo_1 = f"\\underline{{{row['algo 1']}}}" if row['\\vda'] > 0.5 else row['algo 1']
        algo_2 = f"\\underline{{{row['algo 2']}}}" if row['\\vda'] < 0.5 else row['algo 2']
    else:
        algo_1, algo_2 = row['algo 1'], row['algo 2']
    
    return row['time'], algo_1, algo_2, mwu_p, effect_size


def format_latex_time(row):
    # Bold MWU p if significant (< 0.05)
    if row['MWU p'] < 0.001:
        mwu_p = f"\\textbf{{{row['MWU p']:.1e}}}"
    elif row['MWU p'] < 0.05:
        mwu_p = f"\\textbf{{{row['MWU p']:.4f}}}"
    else:
        mwu_p = f"{row['MWU p']:.4f}"
    
    # Format VDA as \ebar with magnitude
    abs_diff = abs(0.5 - row['\\vda'])
    effect_size = f"({row['magn.']}) \\ebar{{{row['\\vda']:.4f}}}{{{abs_diff:.4f}}}"
    
    # Underline algorithms based on conditions
    if row['MWU p'] < 0.05:  # Significant difference
        budget_1 = f"\\underline{{{row['time 1']}}}" if row['\\vda'] > 0.5 else row['time 1']
        budget_2 = f"\\underline{{{row['time 2']}}}" if row['\\vda'] < 0.5 else row['time 2']
    else:
        budget_1, budget_2 = row['time 1'], row['time 2']
    
    return row['algo'], budget_1, budget_2, mwu_p, effect_size


# Given a list of experiments for a case study, generate a LaTeX table with mean and standard deviation values for each time budget and algorithm
def generate_latex_table_for_qi_per_cs_with_mean(exps, qi):
    mean_std_values = {}
    for exp in exps:
        key = (exp.time, exp.algo)
        if key not in mean_std_values:
            mean_std_values[key] = {'values': [], 'mean': 0, 'stdv': 0}
        mean_std_values[key]['values'].extend(exp.values)
    
    latex_rows = []
    for key, data in mean_std_values.items():
        data['mean'] = np.mean(data['values'])
        if qi in to_minimize:
            data['mean'] = -data['mean']
        data['stdv'] = np.std(data['values'])
        latex_rows.append(f"{key[1]} & {key[0]} & {data['mean']:.4f} & {data['stdv']:.4f} \\\\")
    # order by algorithm and time
    latex_rows = sorted(latex_rows, key=lambda x: (x.split('&')[0], x.split('&')[1]))
    
#    latex_header = rf"""\begin{{table}}[t]                                                                                                   
#\centering
#\begin{{tabular}}{{lccr}}
#\toprule
#%case study            & algorithms &  search budget & q indicator &     value \\
#Algor. &  Budget & {qi} avg & {qi} stdev \\
#\midrule \\
#"""
    
#    latex_footer = r"""
#\bottomrule
#\end{tabular}
#\caption{Mean and standard deviation values for each time budget and algorithm.}
#\label{tab:mean_std}
#\end{table}
#"""
    
    #latex_table = latex_header + "\n".join(latex_rows) + latex_footer
    #print(latex_table)
    return latex_rows

def tex_header(header, columns):
    return rf"""\begin{{table}}[ht] 
    \centering
    \begin{{tabular}}{{{columns}}}
    \toprule
    {header} \\
    """

def tex_footer(caption, label):
    return rf"""
    \bottomrule
    \end{{tabular}}
    \caption{{{caption}}}
    \label{{{label}}}
    \end{{table}}
    """

def save_latex_table(latex_code, file_name):
    with open(TABLES_DIR + '/'+file_name, 'w') as f:
        f.write(latex_code)    
    
qis = ['HV', 'IGD', 'IGD+', 'EP', 'SPREAD', 'GSPREAD']

def cs_multirow_latex(num_column, cs):
    combined_latex_body = "\n\midrule\n"
    combined_latex_body += rf"\multicolumn{{{num_column}}}{{c}}{{\textbf{{{cs}}}}} \\"
    combined_latex_body += "\n\midrule\n"
    return combined_latex_body

for qi in qis:
    exps = [Experiment(f) for f in glob('{}/qi__*-*-*-[0-9]*__{}.csv'.format(DATA_DIR, qi))]

    print('-----', qi)
    
    combined_latex_body = ""
    
    latex_header = tex_header(f"Algor. &  Budget & {qi} Avg & {qi} Stdev", "lccr")
    latex_footer = tex_footer(f"Average {qi} quality indicator and its standard deviation over \\independentRun runs, listed by algorithm and search budget.", f"tab:{qi}_mean_std")

    for cs in set([e.casestudy for e in exps]):
        exps_by_cs = [e for e in exps if e.casestudy == cs]
        print('-----', cs)

        # Add a multicolumn row for the case study
        if cs == 'train-ticket': 
            cs = '\\ttbs'
        else: 
            cs = '\\ccm'

        combined_latex_body += cs_multirow_latex(4, cs)
    
        latex_row = generate_latex_table_for_qi_per_cs_with_mean(exps_by_cs, qi)
        for row in latex_row:
            combined_latex_body += row + "\n"
        
        filename = f"{qi}_mean_std.tex"
        #combined_latex_body += "\n\midrule\n"
        #combined_latex_body += rf"\multicolumn{{6}}{{c}}{{\textbf{{{cs}}}}} \\"
        #combined_latex_body += "\n\midrule\n"
        #combined_latex_body += cs_multirow_latex(6, cs)
        

        # Compare time
        df = compare(exps_by_cs, 'algo', 'time')
#        print(df.to_markdown(index=False))

        # Apply formatting
        #formatted_data = df.apply(format_latex_time, axis=1).tolist()
        #formatted_df = pd.DataFrame(formatted_data, columns=["Algor", "Budget 1", "Budget 2", "MWU p", "Effect Size"])
        #print()
        ### Add rows for this case study
        #combined_latex_body += "\n".join(
        #    f"{row['Algor']} & {row['Budget 1']} & {row['Budget 2']} & {row['MWU p']} & {row['Effect Size']} \\\\"
        #    for _, row in formatted_df.iterrows()
        #)
       # file_name = f"{qi}_test_time.tex"
       # header = "Algor & Budget 1 & Budget 2 & MWU p & \multicolumn{2}{c}{Effect Size} \\\\"
       # caption = f"\\mwu test and \\vda effect sizes comparing the {qi} achieved with different time budgets in \\independentRun runs. Magnitude interpretation: negligible (N), small (S), medium (M), large (L). The magnitude of the effect size is also represented by bars."
       # label = f"tab:{qi}_test_time"

        # Compare algorithms
        #df = compare(exps_by_cs, 'time', 'algo')
        #print(df.to_markdown(index=False))
        #print()
        # Apply formatting
#        formatted_data = df.apply(format_latex, axis=1).tolist()
#        formatted_df = pd.DataFrame(formatted_data, columns=["Budget", "Algor. 1", "Algor. 2", "MWU p", "Effect Size"])

        # Generate LaTeX rows
        ### Add rows for this case study
#        combined_latex_body += "\n".join(
#            f"{row['Budget']} & {row['Algor. 1']} & {row['Algor. 2']} & {row['MWU p']} & {row['Effect Size']} \\\\"
#            for _, row in formatted_df.iterrows()
#        )
#        file_name = f"{qi}_test_algo.tex"
        #header = "Budget & Algor. 1 & Algor. 2 & MWU p & \multicolumn{2}{c}{Effect Size} \\"
        #caption = f"\\mwu test and \\vda effect sizes comparing the {qi} achieved by different algorithms in \\independentRun runs. Magnitude interpretation: negligible (N), small (S), medium (M), large (L). The magnitude of the effect size is also represented by bars."
        #label = f"tab:{qi}_test_algo"

        # LaTeX Header with a Double-Column
        #latex_header = rf"""
        #\begin{{table}}[t]
        #\centering
        #\begin{{tabular}}{{llllll}}
        #\toprule
        #{header}
        #"""
        # LaTeX Footer
        #latex_footer = f"""
        #\\bottomrule
        #\\end{{tabular}}
        #\\caption{{{caption}}}
        #\\label{{{label}}}
        #\\end{{table}}
        #""" 

    # Combine all LaTeX components
    #latex_code = latex_header + combined_latex_body + "\n" + latex_footer

    # Print or save to a file
    #print(latex_code_qi)
    print(latex_header + combined_latex_body + latex_footer)

    save_latex_table(latex_header + combined_latex_body + latex_footer, filename)
#    with open(TABLES_DIR + '/'+file_name, 'w') as f:
#       f.write(latex_code)
#
    print()

