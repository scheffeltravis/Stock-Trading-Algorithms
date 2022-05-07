![alt tag](https://raw.githubusercontent.com/QuantConnect/Lean/master/Documentation/logo.white.small.png) 
## Market Regimes Data

### Introduction

Being able to reliably backtest against known and identifiable market regimes, allows both us and our users to compare the different trading algorithms in this repository. The trading data in this directory represents the 6 different market regimes:

- Uptrend, with high volitility
- Uptrend, with low volitility
- Lateral, with high volitility
- Lateral, with low volitility
- Downtrend, with high volitility
- Downtrend, with low volitility

This data was all sourced from various historial trading data, over varying time frames*.

\*This is because attempting to find all six regimes in real world data will most likely not all adhere to the same time frames. We did attempt to generate this data to allow for more continuity between the different data sets, but this proved more time consuming then manually finding them in the wild so to speak.

### Folder Structure

Within this directory, we have included the raw historical trading data in CSV format, as well as accompanying visual representations of the data to note the volitility and trend direction. The different data sets and visual representations are labelled both using the regime data found above:

- Uptrend, with high volitility: `data/regimes/uptrend-high-volitility/`
- Lateral, with high volitility: `data/regimes/lateral-high-volitility/`
- Downtrend, with high volitility: `data/regimes/downtrend-high-volitility/`
