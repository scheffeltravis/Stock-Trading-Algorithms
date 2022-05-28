import os
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
    timestamp = backtest_algorithm(args.algorithm, args.regime, args.ticker)

    # Print the total time for all backtests executed
    total_time = datetime.now() - start_time
    print("Backtest Execution Time: " + str(total_time.total_seconds()))

    # Get start time of execution for reporting
    start_time = datetime.now()

    # Generate reports based on given arguments
    generate_reports(args.algorithm, timestamp)

    # Print the total time for all reports generated
    total_time = datetime.now() - start_time
    print("Reports Generation Time: " + str(total_time.total_seconds()))


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

    # Set datetime in order to properly label backtest restults
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

    # Backtest all combinations of regimes/tickers for given algorithm
    for regime in regimes:
        for ticker in tickers:
            # Create directory for backtest results
            backtest = "{}_{}_{}".format(regime, ticker, timestamp)
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

    return timestamp

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

"""Generates a set of reports based on the provided configuration."""
def generate_reports(algorithm, timestamp):
    pool = mp.Pool(mp.cpu_count())

    # Get recent backtest folders for given algorithm
    path = Path(algorithm)/"backtests"
    backtests = [Path(f.path) for f in os.scandir(path) if timestamp in f.path]
    os.scandir()

    # Generate reports for all recent backtests
    for folder in backtests:
        # Get backtest config file
        path = folder/"config"

        try:
            f = open(path, "r")
            data = json.loads(f.read())
            f.close()
        except FileNotFoundError:
            print(f"No config.json file found in {algorithm} directory")
            sys.exit(1)
        except Exception as e:
            print(f"Unexpected error opening {path}:", repr(e))
            sys.exit(1)

        # Set paths for executing report
        report_path = folder/"report.html"
        results_path = folder/str(data["id"])

        # Create subprocesses to generate backtest report
        pool.apply_async(execute_report, (algorithm, report_path, results_path.with_suffix(".json")))

    # Close any remaining thread pools
    pool.close()
    pool.join()


"""Creates a subprocess which executes a report for a specific backtest."""
def execute_report(algorithm, report_path, results_path):
    run(
        ["lean", "report", "--report-destination", report_path, "--backtest-results", results_path],
        stdout = PIPE, 
        stderr = PIPE
    )


if __name__ == "__main__":
    main()