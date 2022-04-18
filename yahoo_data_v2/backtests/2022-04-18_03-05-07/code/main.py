from AlgorithmImports import *
from sqlalchemy import false
from yahoo_reader import YahooData

from yahoo_loader import *

# make sure this is right
# from QuantConnect.Indicators import SimpleMovingAverage as SMA
from QuantConnect.Indicators import *
# from QuantConnect.Data.Market import TradeBar
# from System import *
# from QuantConnect import *
# from QuantConnect.Algorithm import *


class FirstAlgorithm(QCAlgorithm):

    def __init__(self):
        # self.symbol = "TQQQ"
        # self.symbol = self.AddEquity("TQQQ").Symbol
        self.moving_averages_close = []
        self.moving_averages_high = []
        self.moving_averages_low = []
        self.ma_lengths = [5, 10, 20, 62]
        self.trade_status = len(self.ma_lengths) * [0]
        # self.sma = None

    def Initialize(self):

        get_yahoo_data('TQQQ', '2017-01-01', '2020-12-30')

        self.SetStartDate(2017, 1, 1)  # Set Start Date
        self.SetEndDate(2020, 12, 30)  # Set End Date
        self.SetCash(100000)  # Set Strategy Cash
        self.SetWarmUp(100)

        self.symbol = self.AddData(YahooData, "TQQQ", Resolution.Daily).Symbol

        for i in range(len(self.ma_lengths)):
            self.sma = self.SMA(
                self.symbol, self.ma_lengths[i], Resolution.Daily, Field.Close)
            self.moving_averages_close.append(self.sma)
            self.sma = self.SMA(
                self.symbol, self.ma_lengths[i], Resolution.Daily, Field.High)
            self.moving_averages_high.append(self.sma)
            self.sma = self.SMA(
                self.symbol, self.ma_lengths[i], Resolution.Daily, Field.Low)
            self.moving_averages_low.append(self.sma)

    def OnData(self, data):
        """OnData event is the primary entry point for your algorithm. Each new data point will be pumped in here.
            Arguments:
                data: Slice object keyed by symbol containing the stock data
        """
        if self.IsWarmingUp:
            return

        holdings = self.Portfolio[self.symbol].Quantity

        #
        # THE PROGRAM NEVER GETS PAST THIS LINE
        # was getting no data error without this, not sure if this is necessary
        # if not data.Bars.ContainsKey(self.symbol):
        #     return

        # could not get data from data.bars but data['TQQQ'].Close appears to be working
        # bar = data.Bars[self.symbol]
        # bar = data.Bars['TQQQ']

        changed = False
        for i in range(len(self.ma_lengths)):
            self.Debug("CLOSING PRICE " + str(data['TQQQ'].Close))
            self.Debug("TRADE STATUS " + str(self.trade_status))
            self.Debug("M.A. HIGH CUR VALUE " +
                       str(self.moving_averages_high[i].Current.Value))
            self.Debug("M.A. HIGH CUR VALUE INT " +
                       str(int(self.moving_averages_low[i].Current.Value)))
            # self.Debug(str(changed))
            if data['TQQQ'].Close > self.moving_averages_high[i].Current.Value and self.trade_status[i] == 0:
                self.trade_status[i] = 1
                changed = True

            if data['TQQQ'].Close < self.moving_averages_low[i].Current.Value and self.trade_status[i] == 1:
                self.trade_status[i] = 0
                changed = True

        if changed:
            buy_signals = sum(self.trade_status)
            self.Debug(str(buy_signals))
            percentage = buy_signals / len(self.ma_lengths)
            self.Debug("PERCENTAGE IS " + str(percentage))
            self.SetHoldings(self.symbol, percentage)
            self.Debug("Purchased Stock")

        # Keep track of the values
        self.Debug(
            f"{self.symbol.Value} - {self.Time}: Close={data[self.symbol].Close}")

        # close = self.Securities["UDOW"].Close
        # self.StopMarketOrder("UDOW", 10, round((close * .90), 2))
        # self.Debug(f"{self.Portfolio.TotalPortfolioValue}")
