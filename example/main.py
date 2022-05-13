from AlgorithmImports import *
from yahoo_utils import *
from regime_utils import *
from datetime import datetime


class FirstAlgorithm(QCAlgorithm):
    def Initialize(self):
        # Configure necessary initialization data
        self.ticker = "TQQQ"
        start_date = datetime(2021, 1, 1)
        end_date = datetime(2022, 1, 1)
        
        # Check if we are configured to test against regime data
        regime = self.GetParameter("regime")
        ticker = self.GetParameter("ticker")

        # Configure the algorithm with regime test data
        if regime and ticker:
            data = get_regime_data(regime, ticker)

            self.ticker = ticker
            start_date = datetime.strptime(data["start_date"], "%Y-%m-%d")
            end_date = datetime.strptime(data["end_date"], "%Y-%m-%d")

        # Set start/end dates based on configured data above
        self.SetStartDate(start_date.year, start_date.month, start_date.day)
        self.SetEndDate(end_date.year, end_date.month, end_date.day)

        # Get the stock data from YF for the given timeframe
        get_yahoo_data(self.ticker, start_date, end_date)

        # Set strategy cash
        self.SetCash(100000)

        self.symbol = self.AddData(YahooData, self.ticker, Resolution.Daily).Symbol

    def OnData(self, data):
        """OnData event is the primary entry point for your algorithm. Each new data point will be pumped in here.
            Arguments:
                data: Slice object keyed by symbol containing the stock data
        """
        if not self.Portfolio.Invested:
            self.SetHoldings("TQQQ", 1)
            self.Debug("Purchased Stock")

        # Keep track of the values
        self.Debug(f"{self.symbol.Value} - {self.Time}: Close={data[self.symbol].Close}")
