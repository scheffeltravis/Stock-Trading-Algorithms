import json
from pathlib import Path
from AlgorithmImports import *


"""Returns the start/end dates for a given ticker under a particular regime."""
def get_regime_data(regime, ticker):
    fname = 'regimes.json'
    path = Path(Globals.DataFolder)/'regimes'/fname

    if path.exists():
        f = open(path, "r")
        data = json.loads(f.read())
    else:
        print(f'Problem getting ticker {ticker} for regime {regime}')
        return None
    
    if data:
        return data[regime][ticker]

    return None