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
'10-KENO': 'KENO',
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
}

d0 = None
ds = {}
rdf = 'DATA.json'
for dname, dpath in datasets.items():
    print(f'{dpath}/{rdf}')
    with open(f'{dpath}/{rdf}') as f:
        data = json.load(f)
    ds[dname] = data
    if dname == d0name:
        d0 = data
if d0 == None:
    raise ValueError('Base data {d0name} not found.')
print(ds)

# write data sets
def fitf(x, a, b) -> float:
    return a*x + b

for intrusion in intrusions:
    ds_k = {}
    ds_kerr = {}
    d0_k     = dict(zip(d0['T'], d0[f'{intrusion:05.02f}']['k']))
    d0_kerr  = dict(zip(d0['T'], d0[f'{intrusion:05.02f}']['kerr']))
    for dname, desc in plotdata.items():
        print(dname, desc)
        ds_k[dname]    = {}
        ds_kerr[dname] = {}
        if not f'{intrusion:05.02f}' in ds[dname].keys():
            continue
#        print(dname, desc)
        ds_k[dname]    = dict(zip(ds[dname]['T'], ds[dname][f'{intrusion:05.02f}']['k']))
        ds_kerr[dname] = dict(zip(ds[dname]['T'], ds[dname][f'{intrusion:05.02f}']['kerr']))

    fout = open(f'data_I-{intrusion:05.02f}.dat','w')
    fout.write("#      ")
    for dname, desc in plotdata.items():
        fout.write(f' {desc:-20s} |')
    fout.write("\n#      ")
    for dname, desc in plotdata.items():
        fout.write("     keff sigma(keff)  ")
    fout.write("\n")
    for T in d0['T']:
        fout.write(f'{T:-6.01f} ')
        for dname, desc in plotdata.items():
            if T in ds_k[dname].keys():
                fout.write(f'{ds_k[dname][T]:-10.8f} {ds_kerr[dname][T]:-10.08f}  ')
            else:
                fout.write('    NaN         NaN    ')
        fout.write("\n")
    fout.close()


