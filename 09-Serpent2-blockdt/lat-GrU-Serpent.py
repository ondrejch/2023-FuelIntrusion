#!/usr/bin/python3
#
# 3D MSRR core in Serpent, salt instrusion using SCALE atom densitites from SHIFT's HDF5 output
#
# Ondrej Chvala, ochvala@utexas.edu
# MIT license
#

import os
import numpy as np
import h5py

def s2comp(h5file:str="") -> str:
    ''' Reads HDF5 SHIFT file and returns material deck for Serpent.
    Only the relevant ones are parsed: fuel salt and moderator graphite.
    '''
    out:str = ''
    Shift2SerpentComps = {
    1 : ['uranium'],
    2 : ['graphite'],
    }
    f = h5py.File(h5file)
    comp = f['comp']['compositions']

    for i in range(1, comp.len()):
        if not i in Shift2SerpentComps.keys():
            continue
        c = comp[i]
        T = c[2]
        dens = c[3]
        isos = c[4]
        s2isomat:str = ''
        #print(f"*** {i}, temp {T} K, rho {dens} cc")
        grmassfrac:float = 0;
        for iso in isos:            # Loop over isotopes in mixture and make Serpent-like entries
            if iso[1] <= 0.0:
                continue
            if int(iso[0]) > 3006000:   # Special treatment for graphite
                grmassfrac += float(iso[1])
                continue
            isomat = f"{iso[0]:-7d}.{xlib} -{iso[1]:021.19f}"
            #print(isomat)
            s2isomat = s2isomat + f"{isomat}\n"
        if grmassfrac > 0.0:        # There was graphite!
            isomat = f"{6000:-7d}.{xlib} -{grmassfrac:021.19f}"
            #print(isomat)
            s2isomat = s2isomat + f"{isomat}\n"
        for m in Shift2SerpentComps[i]:  # Loop ever Serpent materials to generate
            #print(m)
            s2mathead:str = ''
            if grmassfrac > 0.0:        # There was graphite!
                s2mathead = f"mat {m}  -{dens} tmp {T} moder grph 6000"
            else:
                s2mathead = f"mat {m}  -{dens} tmp {T}"
            out = out + f"{s2mathead}\n{s2isomat}\n"
    return out

# --------------- main program -----------------


for intrusion in [0,1.0]:
    print(f"Intrusion = {intrusion} %")
    deckpath1 = f'I{intrusion:05.02f}'
    if not os.path.isdir(deckpath1):
        os.mkdir(deckpath1)
    os.chdir(deckpath1)

    for T in np.linspace(300, 990, 70):
        deckpath2 = f'T{T:5.03f}'
        if not os.path.isdir(deckpath2):
            os.mkdir(deckpath2)
        else:
            continue
        os.chdir(deckpath2)

        xlib = '81c'
        if T < 600:
            xlib = '80c'

        Tgr = T # Sab library selection based on graphite T
        grlib0 = '16t'
        grlib1 = '17t'
        if Tgr<=1000.0:
            grlib0 = '15t'
            grlib1 = '16t'
        if Tgr<=800.0:
            grlib0 = '14t'
            grlib1 = '15t'
        if Tgr<=700.0:
            grlib0 = '13t'
            grlib1 = '14t'
        if Tgr<=600.0:
            grlib0 = '12t'
            grlib1 = '13t'
        if Tgr<=500.0:
            grlib0 = '11t'
            grlib1 = '12t'
        if Tgr<=400.0:
            grlib0 = '10t'
            grlib1 = '11t'

        s2matdeck:str = s2comp(f'../../../00-SCALE/{deckpath1}/{deckpath2}/uglat.shift-output.h5')
        fout = open('lats2','w')
        fout.write(f'''
set title "Uranium - Graphite lattice"

surf  10 cube  0.0 0.0 0.0   11.0
surf  20 cyl   0.0 0.0 1.75 -11.0 11.0

cell  10 0 graphite -10 20
cell  20 0 uranium  -20
cell  99 0 outside   10

% boundary conditions
set bc reflective

% Cross section library file path:
set acelib "/opt/MCNP6.2/MCNP_DATA/xsdir_mcnp6.2_msr783k.sss"

% Materials
{s2matdeck}

% Thermal scattering data
therm grph {Tgr} "grph.{grlib0}" "grph.{grlib1}" % Graphite at {Tgr} K

% Explicitly defined source
src source sx -1.5 1.5 sy -1.5 1.5 sz -11.0 11.0

set blockdt graphite uranium

% k eigenvalue cycles
set pop 50000 500 30

''')
        os.system('qsub ../../run.sh')
        os.chdir('..')

    os.chdir('..')
