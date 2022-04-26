from AlgorithmImports import *
from sqlalchemy import false
from yahoo_reader import YahooData
from yahoo_loader import *
from QuantConnect.Indicators import *


class RangeAlgorithm(QCAlgorithm):
    def __init__(self):
        self.moving_averages_close = []
        self.moving_averages_high = []
        self.moving_averages_low = []
        self.ma_lengths = [6, 18]
        self.trade_status = [0, 0]
        # self.ticker = "^GSPC"
        self.ticker = "TQQQ"
        # self.ticker = "TNA"
        # self.ticker = "^IXIC"
        # self.ticker = "UPRO"
        # self.ticker = "UDOW"
        # self.ticker = "SOXL"

    def Initialize(self):
        get_yahoo_data(self.ticker, '2015-01-01', '2022-04-23')
        # self.SetStartDate(2017, 1, 1)
        # self.SetEndDate(2018, 1, 1)
        # self.SetStartDate(2017, 1, 1)
        # self.SetEndDate(2019, 1, 1)
        # self.SetStartDate(2021, 1, 1)
        # self.SetEndDate(2022, 1, 1)
        # self.SetStartDate(2021, 4, 22)
        # self.SetEndDate(2022, 4, 22)
        # self.SetStartDate(2022, 1, 1)
        # self.SetEndDate(2022, 4, 22)
        # self.SetStartDate(2017, 1, 1)
        # self.SetEndDate(2020, 12, 30)
        # self.SetStartDate(2017, 4, 22)
        # self.SetEndDate(2022, 4, 22)
        self.SetStartDate(2017, 1, 1)
        self.SetEndDate(2022, 4, 22)

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

        changed = False
        # calculates range of shorter length sma
        short_diff = self.moving_averages_high[0].Current.Value - \
            self.moving_averages_low[0].Current.Value
        # calculates range of longer length sma
        long_diff = self.moving_averages_high[1].Current.Value - \
            self.moving_averages_low[1].Current.Value
        # gets shorter length sma close price
        short_close = self.moving_averages_close[0].Current.Value
        # gets longer length sma close price
        long_close = self.moving_averages_close[1].Current.Value

        # buy signal
        # shorter sma range > longer sma range indicates range expansion and trend continuation
        # shorter sma close price > longer sma close price indicates bullish price movement
        # this indicates that bullish trend will likely continue so buy signal is issued
        if short_diff > long_diff and short_close > long_close and self.trade_status[0] == 0:
            self.trade_status[0] = 1
            # resetting trade_status[1] since this means that range expansion has occurred and
            # range contraction needs to be reset for when it occurs again
            self.trade_status[1] = 0
            changed = True

        # buy signal
        # shorter sma range < longer sma range indicates range contraction and trend reversal
        # shorter sma close price < longer sma close price indicates bearish price movement
        # this indicates that bearish trend will likely reverse so buy signal is issued
        if short_diff < long_diff and short_close < long_close and self.trade_status[0] == 0:
            self.trade_status[0] = 1
            # resetting trade_status[1] since this means that range expansion has occurred and
            # range contraction needs to be reset for when it occurs again
            self.trade_status[1] = 0
            changed = True

        # sell signal
        # shorter sma range < longer sma range indicates range contraction and trend reversal
        # shorter sma close price > longer sma close price indicates bullish price movement
        # this indicates that bullish trend will likely reverse so sell signal is issued
        if short_diff < long_diff and short_close > long_close and self.trade_status[1] == 0:
            self.trade_status[1] = 1
            # resetting trade_status[0] since this means that range contraction has occurred and
            # so range expansion needs to be reset for when it occurs again
            self.trade_status[0] = 0
            changed = True

        # sell signal
        # shorter sma range > longer sma range indicates range expansion and trend continuation
        # shorter sma close price < longer sma close price indicates bearish price movement
        # this indicates that bearish trend will likely continue so sell signal is issued
        if short_diff > long_diff and short_close < long_close and self.trade_status[1] == 0:
            self.trade_status[1] = 1
            # resetting trade_status[0] since this means that range expansion has occurred and
            # range contraction needs to be reset for when it occurs again
            self.trade_status[0] = 0
            changed = True

        if changed:
            self.Debug("HOLDINGS BEFORE CHANGE: QUANTITY - " +
                       str(self.Portfolio[self.symbol].Quantity) + " VALUE - " +
                       str(self.Portfolio.TotalHoldingsValue))
            self.Debug("TRADE STATUS " + str(self.trade_status))
            if self.trade_status[0] == 1:
                self.SetHoldings(self.symbol, 1)
                self.Debug("BUY ORDER TRIGGERED")
            if self.trade_status[1] == 1:
                self.SetHoldings(self.symbol, 0)
                self.Debug("SELL ORDER TRIGGERED")
            self.Debug(
                f"Short Close: {short_close} Long Close: {long_close} Short Diff: {short_diff} Long Diff: {long_diff}")
            self.Debug("HOLDINGS AFTER CHANGE: QUANTITY - " +
                       str(self.Portfolio[self.symbol].Quantity) + " VALUE - " +
                       str(self.Portfolio.TotalHoldingsValue))
            self.Debug(
                f"{self.symbol.Value} - {self.Time}: Close={data[self.symbol].Close}")
            self.Debug(
                f"PORTFOLIO VALUE: {self.Portfolio.TotalPortfolioValue}")
            self.Debug(" ")
