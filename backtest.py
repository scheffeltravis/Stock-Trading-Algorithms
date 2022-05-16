import sys
import argparse
import json
import multiprocessing as mp
from pathlib import Path
from subprocess import run, PIPE
from datetime import datetime


"""Executes multiple backtests with provided configuration, and prints the total execution time."""
def main():
    # Initialize parser
    parser = argparse.ArgumentParser(description = "Script used to simplify algorithm backtesting")
    
    # Add expected arguments
    parser.add_argument("-a", "--algorithm", required = True, 
                        help = "the algorithm to backtest")
    parser.add_argument("-r", "--regime", 
                        help = "the specific regime used to backtest")
    parser.add_argument("-t", "--ticker", 
                        help = "the specific stock ticker used to backtest")
    
    # Read arguments from command line
    args = parser.parse_args()

    # Get start time of execution for reporting
    start_time = datetime.now()

    # Run backtests based on given arguments
    backtest_algorithm(args.algorithm, args.regime, args.ticker)

    # Print the total time for all backtests executed
    total_time = datetime.now() - start_time
    print("Total Execution Time: " + str(total_time.total_seconds()))


"""Performs a set of backtests based on the provided configuration."""
def backtest_algorithm(algorithm, regime, ticker):
    pool = mp.Pool(mp.cpu_count())

    # Get regimes.json file for given algorithm
    path = Path("data")/"regimes"/"regimes.json"

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

    # Create lists of regimes and tickers
    regimes = []
    tickers = []

    # Check what combination of regimes and tickers we need to backtest
    if regime and ticker:
        regimes.append(regime)
        tickers.append(ticker)
    elif regime:
        regimes.append(regime)
        tickers = list(data[regime])
    elif ticker:
        regimes = list(data)
        tickers.append(ticker)
    else:
        regimes = list(data)
        tickers = list(data[regimes[0]])

    # Backtest all combinations of regimes/tickers for given algorithm
    for regime in regimes:
        for ticker in tickers:
            # Create directory for backtest results
            backtest = "{}_{}_{}".format(regime, ticker, datetime.now().strftime("%Y-%m-%d_%H-%M-%S"))
            path = Path(algorithm)/"backtests"/backtest

            # Set parameters for testing in config.json
            configure_backtest(algorithm, regime, ticker)
            
            # Create subprocesses to run backtests
            pool.apply_async(execute_backtest, (algorithm, path))

    # Close any remaining thread pools
    pool.close()
    pool.join()

    # Clear parameters from config.json
    configure_backtest(algorithm)

"""Creates a subprocess which runs a specific backtest."""
def execute_backtest(algorithm, output):
    run(
        ["lean", "backtest", algorithm, "--output", output],
        stdout = PIPE, 
        stderr = PIPE
    )

"""Configures the appropriate config.json for automated backtesting."""
def configure_backtest(algorithm, regime = None, ticker = None):
    # Create parameters object
    parameters = {}
    
    # Set parameters if present
    if regime and ticker:
        parameters = {
            "regime": regime,
            "ticker": ticker
        }

    # Get config.json file for given algorithm
    path = Path()/algorithm/"config.json"

    try:
        f = open(path, "r+")
        data = json.loads(f.read())
    except FileNotFoundError:
        print(f"No config.json file found in algorithm directory: {algorithm}")
        sys.exit(1)
    except Exception as e:
        print(f"Unexpected error opening {path}:", repr(e))
        sys.exit(1)

    # Insert parameter object into config data
    data["parameters"] = parameters

    # Overwrite config.json with new data
    f.seek(0)
    json.dump(data, f, indent = 4)
    f.truncate()
    f.close()


if __name__ == "__main__":
    main()