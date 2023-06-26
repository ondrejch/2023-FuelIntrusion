import json
rdf = 'DATA.json'
DATA = {}

    # JSON DUMP
    DATA[f'{intrusion:05.02f}'] = {}
    DATA[f'{intrusion:05.02f}']['k'] = ks
    DATA[f'{intrusion:05.02f}']['kerr'] = kerrs


# JSON DUMP
DATA['T'] = Ts

with open (rdf, 'w') as fd:
    json.dump(DATA, fd)
