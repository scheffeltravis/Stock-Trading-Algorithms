from AlgorithmImports import *
from sqlalchemy import false
from yahoo_reader import YahooData
from yahoo_loader import *
from QuantConnect.Indicators import *


class FirstAlgorithm(QCAlgorithm):

    def __init__(self):
        self.moving_averages_close = []
        self.moving_averages_high = []
        self.moving_averages_low = []
        self.ma_lengths = [5, 10, 20, 62]
        self.trade_status = len(self.ma_lengths) * [0]

    def Initialize(self):

        # get_yahoo_data('TQQQ', '2017-01-01', '2020-12-30')
        get_yahoo_data('TQQQ', '2017-01-01', '2018-01-01')

        self.SetStartDate(2017, 1, 1)
        self.SetEndDate(2018, 1, 1)
        self.SetCash(100000)
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

        # could not get data from data.bars but data['TQQQ'].Close appears to be working
        # bar = data.Bars[self.symbol]
        # bar = data.Bars['TQQQ']

        changed = False
        for i in range(len(self.ma_lengths)):
            # self.Debug("CLOSING PRICE " + str(data['TQQQ'].Close))
            # self.Debug("TRADE STATUS " + str(self.trade_status))
            # self.Debug("M.A. HIGH CUR VALUE " +
            #            str(self.moving_averages_high[i].Current.Value))
            # self.Debug("M.A. LOW CUR VALUE " +
            #            str(self.moving_averages_low[i].Current.Value))
            # self.Debug(str(changed))
            if data['TQQQ'].Close > self.moving_averages_high[i].Current.Value and self.trade_status[i] == 0:
                self.trade_status[i] = 1
                changed = True

            if data['TQQQ'].Close < self.moving_averages_low[i].Current.Value and self.trade_status[i] == 1:
                self.trade_status[i] = 0
                changed = True

        if changed:
            self.Debug("TRADE STATUS " + str(self.trade_status))
            self.Debug("HOLDINGS BEFORE CHANGE: QUANTITY - " +
                       str(self.Portfolio[self.symbol].Quantity) + " VALUE - " +
                       str(self.Portfolio.TotalHoldingsValue))
            buy_signals = sum(self.trade_status)
            # self.Debug(str(buy_signals))
            percentage = buy_signals / len(self.ma_lengths)
            self.Debug("PERCENTAGE IS " + str(percentage))
            self.SetHoldings(self.symbol, percentage)
            # self.Debug("HOLDINGS WERE CHANGED")
            self.Debug("HOLDINGS AFTER CHANGE: QUANTITY - " +
                       str(self.Portfolio[self.symbol].Quantity) + " VALUE - " +
                       str(self.Portfolio.TotalHoldingsValue))
            self.Debug(
                f"{self.symbol.Value} - {self.Time}: Close={data[self.symbol].Close}")
            self.Debug(
                f"PORTFOLIO VALUE: {self.Portfolio.TotalPortfolioValue}")
