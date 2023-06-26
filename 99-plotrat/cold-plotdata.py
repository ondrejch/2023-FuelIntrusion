#!/usr/bin/python3

import os
import numpy as np
from matplotlib import pyplot as plt
from scipy.optimize import curve_fit
import json

d0name = '00-SCALE'
#d0name = '07-SHIFT-UThC-noSab'

plotdata = {    # which data sets to plot
#'10-KENO': 'KENO',
#'00-SCALE': 'SHIFT',
#'03-SHIFT-newlibs': 'SHIFT, myAMPX',
#'08-SHIFT-newlibs-8xxAMPX': 'SHIFT, detailed AMPX',
#'01-Serpent2': 'Serpent',
#'02-Serpent2-PENDF': 'Serpent, myAMPX',
#'04-S2-Carbon-noSab': 'Serpent, noSab',
#'05-S2-PuC-noSaB': 'Serpent, noSab, Pu239 for U5',
#'06-S2-UThC-noSab': 'Serpent, noSab, Th232 for U8',
#'07-SHIFT-UThC-noSab': 'SHIFT, noSab, Th232 for U8',
'11-SHIFT-Ucold': 'SHIFT, cold Upin',
'12-Serpent2-Ucold': 'Serpent2 cold Upin',
}

plotcolors = {
'00-SCALE': 'royalblue',
'01-Serpent2': 'green',
'02-Serpent2-PENDF': 'limegreen',
'03-SHIFT-newlibs': 'steelblue',
'04-S2-Carbon-noSab': 'yellowgreen',
'05-S2-PuC-noSaB': 'darkmagenta',
'06-S2-UThC-noSab': 'firebrick',
'07-SHIFT-UThC-noSab': 'navy',
'08-SHIFT-newlibs-8xxAMPX': 'blueviolet',
'10-KENO': 'darkorange',
'11-SHIFT-Ucold': 'slateblue', #'cornflowerblue',
'12-Serpent2-Ucold': 'lightseagreen',
}

intrusions = [0,1] # which intrusion data to plot

# read data
datasets = { # for d in $(ls -1d * );do echo "'$d': '../$d'," ;done
'00-SCALE': '../00-SCALE',
'01-Serpent2': '../01-Serpent2',
'02-Serpent2-PENDF': '../02-Serpent2-PENDF',
'03-SHIFT-newlibs': '../03-SHIFT-newlibs',
'04-S2-Carbon-noSab': '../04-S2-Carbon-noSab',
'05-S2-PuC-noSaB': '../05-S2-PuC-noSaB',
'06-S2-UThC-noSab': '../06-S2-UThC-noSab',
'07-SHIFT-UThC-noSab': '../07-SHIFT-UThC-noSab',
'08-SHIFT-newlibs-8xxAMPX': '../08-SHIFT-newlibs-8xxAMPX',
'10-KENO': '../10-KENO',
'11-SHIFT-Ucold': '../11-SHIFT-Ucold',
'12-Serpent2-Ucold': '../12-Serpent2-Ucold',
}

d0 = None; ds = {}
rdf = 'DATA.json'
for dname, dpath in datasets.items():
    print(f'{dpath}/{rdf}')
    with open(f'{dpath}/{rdf}') as f:
        data = json.load(f)
    if dname == d0name:
        d0 = data
    ds[dname] = data
if d0 == None:
    raise ValueError('Base data {d0name} not found.')
# print(ds)

# plot ratios vs. d0 dataset
plt.rcParams["figure.autolayout"] = True
plt.rcParams["figure.figsize"] = [7, 7]
plt.rcParams["xtick.labelsize"] = 16
plt.rcParams["ytick.labelsize"] = 16

def fitf(x, a, b) -> float:
    return a*x + b

def autoscale_y(ax,margin=0.1):
    """This function rescales the y-axis based on the data that is visible given the current xlim of the axis.
    ax -- a matplotlib axes object
    margin -- the fraction of the total height of the y-data to pad the upper and lower ylims"""

    import numpy as np

    def get_bottom_top(line):
        xd = line.get_xdata()
        yd = line.get_ydata()
        lo,hi = ax.get_xlim()
        y_displayed = yd[((xd>lo) & (xd<hi))]
        h = np.max(y_displayed) - np.min(y_displayed)
        bot = np.min(y_displayed)-margin*h
        top = np.max(y_displayed)+margin*h
        return bot,top

    lines = ax.get_lines()
    bot,top = np.inf, -np.inf

    for line in lines:
        new_bot, new_top = get_bottom_top(line)
        if new_bot < bot: bot = new_bot
        if new_top > top: top = new_top

    ax.set_ylim(bot,top)

for intrusion in intrusions:
    rs = {}
    ds_k = {}
    ds_kerr = {}
    d0_k     = dict(zip(d0['T'], d0[f'{intrusion:05.02f}']['k']))
    d0_kerr  = dict(zip(d0['T'], d0[f'{intrusion:05.02f}']['kerr']))
    fig, ax = plt.subplots(1,1)
    ax.set_title(f"Intrusion {intrusion:-5.02f}%", fontsize=20)
    ax.set_xlabel("$T [K]$", fontsize=16)
#    ax.set_ylabel(f"{desc} over {plotdata[d0name]} k$_{{eff}}$", fontsize=16)
    ax.set_ylabel(f"k$_{{eff}}$", fontsize=16)
    aymin:float = 99.9
    aymax:float = -9.9

    data = []
    for dname, desc in plotdata.items():
        print(dname, desc)
#        if dname == d0name:
#            continue
        if not f'{intrusion:05.02f}' in ds[dname].keys():
            continue
#        print(dname, desc)
        ds_k     = dict(zip(ds[dname]['T'], ds[dname][f'{intrusion:05.02f}']['k']))
        ds_kerr  = dict(zip(ds[dname]['T'], ds[dname][f'{intrusion:05.02f}']['kerr']))
        common_T = list(set(d0['T']).intersection(ds[dname]['T']))
        common_T.sort()

        px    = ds[dname]['T']
        py    = ds[dname][f'{intrusion:05.02f}']['k']
        pyerr = ds[dname][f'{intrusion:05.02f}']['kerr']
        pc    = plotcolors[dname]
        data.append(ax.errorbar(px, py, xerr=None, yerr=pyerr, fmt='o', color=pc, markersize=3.1, label=f"{desc}"))
        #(ymin, ymax) = ax.get_ylim()
#        ymin = min(py)*0.999
#        ymax = max(py)*1.001
#        if ymin < aymin:
#            aymin = ymin
#        if ymax > aymax:
#            aymax = ymax
#        print (ymin, aymin, ymax, aymax)
    #plt.ylim(aymin, aymax)
#    plt.xlim(755, 905)
    autoscale_y(ax)
    plt.grid(True, which="both")
    leg = ax.legend()
    fig.savefig(f"cold-keff_{intrusion:05.02f}.png", bbox_inches="tight", facecolor='white')
    plt.close()



