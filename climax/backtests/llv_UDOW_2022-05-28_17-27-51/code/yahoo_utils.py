import pandas as pd
from pathlib import Path
from datetime import datetime, timedelta
from yahoo_fin.stock_info import get_data
from AlgorithmImports import *


class YahooData(PythonData):
    def GetSource(self, config, date, isLiveMode):
        # The name of the asset is the symbol in lowercase .csv (ex. spy.csv)
        fname = config.Symbol.Value.lower() + '.csv'

        # The source folder depends on the directory initialized in lean-cli
        # https://www.quantconnect.com/docs/v2/lean-cli/tutorials/local-data/importing-custom-data
        source = Path(Globals.DataFolder)/'yahoo'/fname

        # The subscription method is LocalFile in this case
        return SubscriptionDataSource(source.as_posix(), SubscriptionTransportMedium.LocalFile)

    def Reader(self, config, line, date, isLiveMode):
        equity = YahooData()
        equity.Symbol = config.Symbol

        # Parse the Line from the Yahoo CSV
        try:
            data = line.split(',')

            # If value is zero, return None
            value = data[4]
            if value == 0:
                return None

            equity.Time = datetime.strptime(data[0], "%Y-%m-%d")
            equity.EndTime = equity.Time + timedelta(days=1)
            equity.Value = value
            equity["Open"] = float(data[1])
            equity["High"] = float(data[2])
            equity["Low"] = float(data[3])
            equity["Close"] = float(data[4])
            # equity["AdjClose"] = float(data[5])
            equity["Volume"] = float(data[6])

            # print(f'Returning --> {coin.EndTime} - {coin}')
            return equity

        except ValueError:
            # Do nothing, possible error in csv decoding
            return None


"""Retrieve the data for a given ticker if a file does not exist with the given date range."""
def get_yahoo_ticker(ticker, folder, start_date, end_date):
    # check if the ticker file exists
    fname = ticker.lower() + '.csv'
    path = Path(folder)/fname

    # get the dates if the file already exists
    if path.exists():
        # open the file and get the dates
        df = pd.read_csv(path, index_col=0)
        dates = pd.DatetimeIndex(df.index.sort_values(ascending=True))
    else:
        dates = None

    start_date = pd.to_datetime(start_date)
    end_date = pd.to_datetime(end_date)

    # if the range is not included in the file or if there is no file at all
    if dates is None or start_date < dates[0] or end_date > dates[-1]:

        # try to retrieve the data from Yahoo_fin
        try:
            delta = timedelta(days=3)
            df = get_data(ticker, start_date=start_date -
                          delta, end_date=end_date+delta)
            df.to_csv(path)
            print(f'Retrieving ticker: {ticker}')

        except BaseException as e:
            print(f'Problem getting ticker {ticker}')
            return None
    else:
        print(f'Ticker {ticker} already loaded')

    return ticker


"""Get a list of tickers from yahoo and save them in the Default LEAN data directory."""
def get_yahoo_data(tickers: list, start_date, end_date):
    # transform tickers into a list (if it is not)
    tickers = tickers if isinstance(tickers, list) else [tickers]

    # check the directory
    folder = Path(Globals.DataFolder)/'yahoo'

    if not folder.exists():
        folder.mkdir()
        print(f'Folder {str(folder)} - Created')
    else:
        print(f'Folder {str(folder)} - Ok')

    # create a list to store all loaded tickers
    loaded_tickers = []
    for ticker in tickers:
        loaded_tickers.append(get_yahoo_ticker(
            ticker, folder, start_date, end_date))

    return [ticker for ticker in loaded_tickers if ticker is not None]