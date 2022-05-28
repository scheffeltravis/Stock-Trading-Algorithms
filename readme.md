![alt tag](https://raw.githubusercontent.com/QuantConnect/Lean/master/Documentation/logo.white.small.png) 
# Algorithmic Stock Market Trading Strategies

## Introduction

This repo contains several stock trading algorithms which have been created and iterated on using the [Lean trading engine CLI](https://www.lean.io/cli/). These algorithms each attempt to use one or more of the "principles of price behavior":

- __Principle #1__: *A Trend Has a Higher Probability of Continuation than Reversal*
- __Principle #2__: *Momentum Preceeds Price*
- __Principle #3__: *Trends End in a Climax*
- __Principle #4__: *The Market Alternates between Range Expansion and Range Contraction*

Using these principles as a basis for functionality, you can see how the logic in each algorithm is constructed around detecting and executing trades based on the indicators being detected.

## Getting Started

In order to backtest and analyze these algorithms, you will need to make sure that you have followed the directions for [installing the Lean CLI](https://www.lean.io/docs/lean-cli/key-concepts/getting-started).

Once you have confirmed you have the required prerequisites and have the Lean CLI installed and running, you should be able to backtest the `example` algorithm to verify (run from project root directory):

```
lean backtest example
```

## Backtesting

We have attempted to simplify the ability to backtest multiple tickers/regimes for a given algorithm by creating a testing script `backtest.py` which will run the configured backtests in parallel. Its use and configuration can be viewed by running the simple help command:

```
python backtest.py --help
usage: backtest.py [-h] -a ALGORITHM [-r REGIME] [-t TICKER]

Script used to simplify algorithm backtesting

optional arguments:
  -h, --help            show this help message and exit
  -a ALGORITHM, --algorithm ALGORITHM
                        the algorithm to backtest
  -r REGIME, --regime REGIME
                        the specific regime used to backtest
  -t TICKER, --ticker TICKER
                        the specific stock ticker used to backtest
```

This script can take in any combination of regimes and tickers, which will ressult in a number of tests being run in parallel based on the hosts CPU count in order to distribute tasks:

```
# Executes backtests for all tickers in all regimes for the example algorithm, 24 TESTS TOTAL
python backtest.py -a example

# Executes backtests for all tickers in the downtrend-low-volitility regime for the example algorithm, 4 TESTS TOTAL
python backtest.py -a example -r dlv

# Executes backtests for the AAPL ticker in all regimes for the example algorithm, 6 TESTS TOTAL
python backtest.py -a example -t AAPL

# Executes backtests for the SPY ticker in the lateral-high-volitility regime for the example algorithm, 1 TEST TOTAL
python backtest.py -a example -r lhv -t SPY
```


## Project Structure

This project is constructed with a `data/` directory (which houses all the testing data used in our backtesting and iteration) as well as multiple `<algorithm>/` directories (see [`example`](example/)), which each follow the same basic [Lean Python project structure](https://www.lean.io/docs/lean-cli/projects/structure#02-Python-Project-Structure).

### Data

All the data used in backtesting and verification is stored within the `data/` directory in this project (if you need to define a new location for your personal testing data, you can make that change in the [`lean.json`](lean.json)). Most of our current testing data can be found in `data/yahoo/`, as this is where we have pulled the majority of our data.

Specific market regime data can be found under the `data/regimes/` directory as well, if needed.

### Algorithms

Within each algorithm directory, we have also included some extra functionality to make backtesting and gathering trading data easier. These extra methods rely on including the [Yahoo_Fin](http://theautomatic.net/yahoo_fin-documentation/) Python library (hence the `requirements.txt`). We included this as a custom Python library which can be excluded if needed using the [directions provided by Lean](https://www.lean.io/docs/lean-cli/projects/libraries/third-party-libraries#05-Custom-Python-Libraries):

- `yahoo_utils.py` - defines utilities for pulling down trading data from Yahoo Finance, storing it in a file based on the ticket key, and defining the custom data type `YahooData` we serialize the raw trading data into which Lean can then analyze and run against.
e.g. it will pull data for *TQQQ* from Yahoo Finance for a given date range and store it in a file `data/yahoo/TQQQ.csv`, which can then be reresented in the `YahooData` data type format.
- `regime_utils.py` - defines utilites for pulling down the regime data ranges used in our testing data found in `data/regimes/regimes.json` for a given ticker and regime type.
e.g. it will return the start/end dates for *AAPL* in the *downward-low-volitility* regime, given the properties set in the algorithm `config.json`:

```
parameters = {
    "regime": "dlv",
    "ticker": "AAPL"
}
```

- `requirements.txt` - includes the manifest of all custom Python libraries included/used in the encompassing algorithm

## Caveats

This is still a very much work in progress project, so there will most likely be changes and updates made which might affect any of the above information before it can also be updated. Hopefully, we can improve on the user experience and have more immediate comparisons and quick start guides for the different algorithms in question.