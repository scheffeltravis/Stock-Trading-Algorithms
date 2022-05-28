import sys
import json
from pathlib import Path
from AlgorithmImports import *


"""Returns the start/end dates for a given ticker under a particular regime."""
def get_regime_data(regime, ticker):
    fname = 'regimes.json'
    path = Path(Globals.DataFolder)/'regimes'/fname

    try:
        f = open(path, "r")
        data = json.loads(f.read())
        f.close()
    except FileNotFoundError:
        print(f"No regimes.json file found in data directory")
        sys.exit(1)
    except Exception as e:
        print(f"Unexpected error opening {path}:", repr(e))
        sys.exit(1)
    
    if data:
        return data[regime][ticker]

    return None