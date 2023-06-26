#!/usr/bin/python3
#
# Ondrej Chvala, ochvala@utexas.edu
# MIT license
#

import os
import numpy as np

#for intrusion in [0,1.0]:
for intrusion in [1.0]:
    print(f"Intrusion = {intrusion} %")
    deckpath = f'I{intrusion:05.02f}'
    if not os.path.isdir(deckpath):
        os.mkdir(deckpath)
    os.chdir(deckpath)

    for T in np.linspace(300, 990, 70):
        deckpath = f'T{T:5.03f}'
        if not os.path.isdir(deckpath):
            os.mkdir(deckpath)
#        else:
#            continue
        os.chdir(deckpath)

        grdust:str = ''
        if intrusion > 0.0:
            grdust = f'''
wtptfuel  2  18.740 2
        92000 0.700   90000 99.3
        1.0 {T}
        92235 100.0   90232 100.0  end'''
        fout = open('uglat.inp','w')
        fout.write(f'''=csas6-shift parm=(   )
Uranium-graphite lattice
ce_v7.1_endf

read comp
wtptfuel  1  18.740 2
        92000 0.700   90000 99.3
        1.0 {T}
        92235 100.0   90232 100.0  end {grdust}
carbon 2 den=1.800000 1.0 {T} end
end comp

read geometry
global unit 1
  cuboid   10 6p11.0
  cylinder 20 1.75 2p11.0
  media    1 1  20
  media    2 1  10 -20
  boundary 10
end geometry

read bounds
all=refl
end bounds

read parameters
npg=50000 gen=500 nsk=30
htm=no
end parameters

end data
end
''')
        os.system('qsub ../../runScale.sh')
        os.chdir('..')

    os.chdir('..')


