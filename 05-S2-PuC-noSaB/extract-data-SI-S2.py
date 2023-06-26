#!/usr/bin/env python3
#
# Serpent2, \alpha_T
#
# Ondrej Chvala, ochvala@utexas.edu
# MIT license
#

import serpentTools
import os
import numpy as np
import re
from scipy.optimize import curve_fit
from matplotlib import pyplot as plt
import json
import json

def fitf(x, a, b) -> float:
    return a*x + b

T0=300.0
rdf = 'DATA.json'
DATA = {}

rdf = 'DATA.json'
DATA = {}
fout = open("kdata-saltintrusion.dat","w")
dout = open("datafit-saltintrusion.dat","w")
dout.write("# keff and ITC [pcm/K] as a function of fuel salt graphite instrusion %\n")
dout.write("# FSGI[%]   keff  sigma(k)    ITC    sigma(ITC)")
dout.write("    eta     sig(eta)    f     sig(f)       p     sig(p)    epsilon  sig(eps)\n")

for intrusion in [0,1.0]:
    print(f"Intrusion = {intrusion} %")
    deckpath:str = f'I{intrusion:05.02f}'

    Ts = []
    ks = [] ; kerrs = []
    k0:float = -1.0
    k0err:float = -1.0
    fout.write(f'{intrusion:-5.02f}  ')
    for T in np.linspace(300, 990, 70):
        deckpath2:str = f'T{T:5.03f}'
        res = serpentTools.read(f'{deckpath}/{deckpath2}/lats2_res.m')
        k:float    = float(res.resdata['absKeff'][0])
        kerr:float = float(res.resdata['absKeff'][1])*k
        fout.write(f'   {k:7.5f} {kerr:7.5f}')
        if (T == T0):
            k0 = k
            k0err = kerr
            sixFfEpsilon:float    = float(res.resdata['sixFfEpsilon'][0])
            sixFfEpsilonerr:float = float(res.resdata['sixFfEpsilon'][1])
            sixFfF:float    = float(res.resdata['sixFfF'][0])
            sixFfFerr:float = float(res.resdata['sixFfF'][1])
            sixFfP:float    = float(res.resdata['sixFfP'][0])
            sixFfPerr:float = float(res.resdata['sixFfP'][1])
            sixFfEta:float    = float(res.resdata['sixFfEta'][0])
            sixFfEtaerr:float = float(res.resdata['sixFfEta'][1])
        Ts.append(T)
        ks.append(k) ; kerrs.append(kerr)
    fout.write('\n')

#    popt, pcov = curve_fit(fitf, Ts[1:3], ks[1:3], sigma=kerrs[1:3], absolute_sigma=True, method='lm')
    popt, pcov = curve_fit(fitf, Ts, ks, sigma=kerrs, absolute_sigma=True, method='lm')
    perr = np.sqrt(np.diag(pcov))
    # JSON DUMP
    DATA[f'{intrusion:05.02f}'] = {}
    DATA[f'{intrusion:05.02f}']['k'] = ks
    DATA[f'{intrusion:05.02f}']['kerr'] = kerrs

    dout.write(f'{intrusion:-7.01f}  {k0:8.6f} {k0err:8.6f} {popt[0]*1e5:+11.6f} {perr[0]*1e5:8.6f}')
    dout.write(f'  {sixFfEta:8.6f} {sixFfEtaerr:8.6f}  {sixFfF:8.6f} {sixFfFerr:8.6f}  {sixFfP:8.6f} {sixFfPerr:8.6f}  {sixFfEpsilon:8.6f} {sixFfEpsilonerr:8.6f}\n')

    # JSON DUMP
    DATA[f'{intrusion:05.02f}'] = {}
    DATA[f'{intrusion:05.02f}']['k'] = ks
    DATA[f'{intrusion:05.02f}']['kerr'] = kerrs

    # Plot
    #if intrusion > 0:
    #    continue
    plt.rcParams["figure.autolayout"] = True
    plt.rcParams["figure.figsize"] = [7, 7]
    plt.rcParams["xtick.labelsize"] = 16
    plt.rcParams["ytick.labelsize"] = 16

    fig, ax = plt.subplots(1,1)
    ax.set_title(f"Serpent2, Pu-U-C, noSab, uranium dust intrusion {intrusion:-5.02f}%", fontsize=20)
    ax.set_xlabel("$T [K]$", fontsize=16)
    ax.set_ylabel("k$_{eff}$", fontsize=16)
    data = ax.errorbar(Ts, ks, xerr=None, yerr=kerrs, fmt='o', color='red', markersize=3.6)
    xfit = np.linspace(Ts[0],Ts[-1],100)
    dfit = ax.plot(xfit, fitf(xfit, popt[0], popt[1]), color="green",
            label=f"{popt[0]*1e5:.2f} +- {perr[0]*1e5:.2f} pcm/K")
    leg = ax.legend()
    #plt.show()
    fig.savefig(f"intrfit_{intrusion:05.02f}.png", bbox_inches="tight", facecolor='white')
    plt.close()

# JSON DUMP
DATA['T'] = Ts

with open (rdf, 'w') as fd:
    json.dump(DATA, fd)

