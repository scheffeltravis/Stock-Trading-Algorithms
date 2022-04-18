from AlgorithmImports import *
from sqlalchemy import false
from yahoo_reader import YahooData
from yahoo_loader import *
from QuantConnect.Indicators import *


class SMAAlgorithm(QCAlgorithm):
    def __init__(self):
        self.moving_averages_close = []
        self.moving_averages_high = []
        self.moving_averages_low = []
        # self.ma_lengths = [5, 10, 20, 62]
        self.ma_lengths = [62]
        self.trade_status = len(self.ma_lengths) * [0]
        self.ticker = "UDOW"

    def Initialize(self):
        get_yahoo_data(self.ticker, '2021-04-17', '2022-04-17')

        self.SetStartDate(2021, 4, 17)
        self.SetEndDate(2022, 4, 17)
        self.SetCash(100000)
        self.SetWarmUp(100)

        self.symbol = self.AddData(
            YahooData, self.ticker, Resolution.Daily).Symbol

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
        if self.IsWarmingUp:
            return

        # could not get data from data.bars but data[self.ticker].Close appears to be working
        # bar = data.Bars[self.symbol]
        # bar = data.Bars[self.ticker]

        changed = False
        for i in range(len(self.ma_lengths)):
            # self.Debug("CLOSING PRICE " + str(data[self.ticker].Close))
            # self.Debug("TRADE STATUS " + str(self.trade_status))
            # self.Debug("M.A. HIGH CUR VALUE " +
            #            str(self.moving_averages_high[i].Current.Value))
            # self.Debug("M.A. LOW CUR VALUE " +
            #            str(self.moving_averages_low[i].Current.Value))
            # self.Debug(str(changed))
            if data[self.ticker].Close > self.moving_averages_high[i].Current.Value and self.trade_status[i] == 0:
                self.trade_status[i] = 1
                changed = True

            if data[self.ticker].Close < self.moving_averages_low[i].Current.Value and self.trade_status[i] == 1:
                self.trade_status[i] = 0
                changed = True

        if changed:
            self.Debug("HOLDINGS BEFORE CHANGE: QUANTITY - " +
                       str(self.Portfolio[self.symbol].Quantity) + " VALUE - " +
                       str(self.Portfolio.TotalHoldingsValue))
            buy_signals = sum(self.trade_status)
            # self.Debug(str(buy_signals))
            self.Debug("TRADE STATUS " + str(self.trade_status))
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
            self.Debug(" ")
