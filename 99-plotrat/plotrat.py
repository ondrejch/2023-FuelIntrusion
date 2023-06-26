#!/usr/bin/python3

import os
import numpy as np
from matplotlib import pyplot as plt
from scipy.optimize import curve_fit
import json

d0name = '00-SCALE'
#d0name = '07-SHIFT-UThC-noSab'

plotdata = {    # which data sets to plot
'00-SCALE': 'SHIFT',
'01-Serpent2': 'Serpent',
'02-Serpent2-PENDF': 'Serpent, myAMPX',
'03-SHIFT-newlibs': 'SHIFT, myAMPX',
'04-S2-Carbon-noSab': 'Serpent, noSab',
'05-S2-PuC-noSaB': 'Serpent, noSab, Pu239 for U5',
'06-S2-UThC-noSab': 'Serpent, noSab, Th232 for U8',
'07-SHIFT-UThC-noSab': 'SHIFT, noSab, Th232 for U8',
'08-SHIFT-newlibs-8xxAMPX': 'SHIFT, detailed AMPX',
'09-Serpent2-blockdt': 'Serpent, blockdt',
'10-KENO': 'KENO',
'11-SHIFT-Ucold': 'SHIFT cold Upin',
'12-Serpent2-Ucold': 'Serpent cold Upin',
'13-SHIFT-DBR2': 'SHIFT DBR=2',
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
'09-Serpent2-blockdt': '../09-Serpent2-blockdt',
'10-KENO': '../10-KENO',
'11-SHIFT-Ucold': '../11-SHIFT-Ucold',
'12-Serpent2-Ucold': '../12-Serpent2-Ucold',
'13-SHIFT-DBR2': '../13-SHIFT-DBR2',
}

d0 = None; ds = {}
rdf = 'DATA.json'
for dname, dpath in datasets.items():
    print(f'{dpath}/{rdf}')
    with open(f'{dpath}/{rdf}') as f:
        data = json.load(f)
    if dname == d0name:
        d0 = data
    else:
        ds[dname] = data
if d0 == None:
    raise ValueError('Base data {d0name} not found.')
# print(ds)

# plot ratios vs. d0 dataset
plt.rcParams["figure.autolayout"] = True
plt.rcParams["figure.figsize"] = [7, 7]
plt.rcParams["xtick.labelsize"] = 16
plt.rcParams["ytick.labelsize"] = 16
aymin = 0.995
aymax = 1.005


def fitf(x, a, b) -> float:
    return a*x + b

for intrusion in intrusions:
    rs = {}
    d0_k     = dict(zip(d0['T'], d0[f'{intrusion:05.02f}']['k']))
    d0_kerr  = dict(zip(d0['T'], d0[f'{intrusion:05.02f}']['kerr']))
    for dname, desc in plotdata.items():
        print(dname, desc)
        if dname == d0name:
            continue
        if not f'{intrusion:05.02f}' in ds[dname].keys():
            continue
#        print(dname, desc)
        ds_k     = dict(zip(ds[dname]['T'], ds[dname][f'{intrusion:05.02f}']['k']))
        ds_kerr  = dict(zip(ds[dname]['T'], ds[dname][f'{intrusion:05.02f}']['kerr']))
        common_T = list(set(d0['T']).intersection(ds[dname]['T']))
        common_T.sort()
        rats  = []
        rerrs = []
        for T in common_T:
            r = ds_k[T] / d0_k[T]
            r_err = np.sqrt(ds_kerr[T]**2 + d0_kerr[T]**2)
            rats.append(r)
            rerrs.append(r_err)
            #print(T,r,r_err)
        # Linear fit
        popt, pcov = curve_fit(fitf, common_T, rats, sigma=rerrs, absolute_sigma=True, method='lm')
        perr = np.sqrt(np.diag(pcov))

        fig, ax = plt.subplots(1,1)
        ax.set_title(f"{desc}, intr.{intrusion:-5.02f}%", fontsize=20)
        ax.set_xlabel("$T [K]$", fontsize=16)
        ax.set_ylabel(f"{desc} over {plotdata[d0name]} k$_{{eff}}$", fontsize=16)
        data = ax.errorbar(common_T, rats, xerr=None, yerr=rerrs, fmt='o', color="blue", markersize=3.6)
        xfit = np.linspace(common_T[0],common_T[-1],100)
        dfit = ax.plot(xfit, fitf(xfit, popt[0], popt[1]), color="orange")
        (ymin, ymax) = ax.get_ylim()
        if ymin > aymin and ymax < aymax:
            ymin = aymin
            ymax = aymax
        plt.ylim(ymin, ymax)
        plt.grid(True, which="both")

#            label=f"{popt[0]*1e5:.2f} +- {perr[0]*1e5:.2f} pcm/K")
#        leg = ax.legend()
        #plt.show()
        fig.savefig(f"rat_{dname}--{d0name}_{intrusion:05.02f}.png", bbox_inches="tight", facecolor='white')
        plt.close()



