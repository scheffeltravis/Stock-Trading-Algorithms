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

## Project Structure

This project is constructed with a `data/` directory (which houses all the testing data used in our backtesting and iteration) as well as multiple `<algorithm>/` directories (see [`example`](example/)), which each follow the same basic [Lean Python project structure](https://www.lean.io/docs/lean-cli/projects/structure#02-Python-Project-Structure).

### Data

All the data used in backtesting and verification is stored within the `data/` directory in this project (if you need to define a new location for your personal testing data, you can make that change in the [`lean.json`](lean.json)). Most of our current testing data can be found in `data/yahoo/`, as this is where we have pulled the majority of our data.

Specific market regime data can be found under the `data/regimes/` directory, but changes will need to be made in the algorithm if you wish to backtest it against this data. We are hoping to improve this in the future.

### Algorithms

Within each algorithm directory, we have also included some extra functionality to make backtesting and gathering trading data easier. These extra methods rely on including the [Yahoo_Fin](http://theautomatic.net/yahoo_fin-documentation/) Python library (hence the `requirements.txt`). We included this as a custom Python library which can be excluded if needed using the [directions provided by Lean](https://www.lean.io/docs/lean-cli/projects/libraries/third-party-libraries#05-Custom-Python-Libraries):

- `yahoo_loader.py` - defines functionality for pulling down trading data from Yahoo Finance, and storing it in a file based on the ticket key, i.e. it will pull data for *TQQQ* from Yahoo Finance for a given date range and store it in a file `data/yahoo/TQQQ.csv`
- `yahoo_reader.py` - defines the custom data type `YahooData` we serialize the raw trading data into, which Lean can then analyze and run against
- `requirements.txt` - includes the manifest of all custom Python libraries included/used in the encompassing algorithm

## Caveats

This is still a very much work in progress project, so there will most likely be changes and updates made which might affect any of the above information before it can also be updated. Hopefully, we can improve on the user experience and have more immediate comparisons and quick start guides for the different algorithms in question.