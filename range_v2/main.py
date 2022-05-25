from AlgorithmImports import *
from sqlalchemy import false
from yahoo_utils import *
from QuantConnect.Indicators import *


class RangeAlgorithm(QCAlgorithm):
    def Initialize(self):
        self.moving_averages_close = []
        self.moving_averages_high = []
        self.moving_averages_low = []
        # self.ma_lengths = [6, 18]
        # self.ma_lengths = [5, 60]
        # self.ma_lengths = [5, 70]
        self.ma_lengths = [5, 80]
        self.trade_status = [0, 0]
        # self.ticker = "^GSPC"
        # self.ticker = "TQQQ"
        # self.ticker = "TNA"
        # self.ticker = "^IXIC"
        # self.ticker = "UPRO"
        self.ticker = "UDOW"
        # self.ticker = "SOXL"
        # self.ticker = "AAPL"
        # self.ticker = "SPY"

        # get_yahoo_data(self.ticker, '1990-11-01', '2019-03-07')
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
        # self.SetStartDate(2017, 4, 27)
        # self.SetEndDate(2022, 4, 27)

        # AAPL Regime Dates
        # get_yahoo_data(self.ticker, '1990-11-01', '2019-03-07')
        # Downtrend High Volitility
        # self.SetStartDate(2015, 6, 1)
        # self.SetEndDate(2016, 2, 26)
        # Downtrend Low Volitility
        # self.SetStartDate(2012, 9, 4)
        # self.SetEndDate(2013, 6, 28)
        # Lateral High Volitility
        # self.SetStartDate(1996, 8, 1)
        # self.SetEndDate(1996, 12, 30)
        # Lateral Low Volitility
        # self.SetStartDate(2019, 2, 4)
        # self.SetEndDate(2019, 3, 7)
        # Uptrend High Volitility
        # self.SetStartDate(2012, 2, 1)
        # self.SetEndDate(2012, 9, 28)
        # Uptrend Low Volitility
        # self.SetStartDate(1990, 11, 1)
        # self.SetEndDate(1991, 2, 27)

        # SPY Regime Dates
        # get_yahoo_data(self.ticker, '1998-10-08', '2014-05-19')
        # Downtrend High Volitility
        # self.SetStartDate(2010, 4, 23)
        # self.SetEndDate(2010, 8, 30)
        # Downtrend Low Volitility
        # self.SetStartDate(2008, 5, 15)
        # self.SetEndDate(2008, 9, 26)
        # Lateral High Volitility
        # self.SetStartDate(2004, 1, 8)
        # self.SetEndDate(2004, 9, 13)
        # Lateral Low Volitility
        # self.SetStartDate(2014, 2, 24)
        # self.SetEndDate(2014, 5, 19)
        # Uptrend High Volitility
        # self.SetStartDate(1998, 10, 8)
        # self.SetEndDate(1999, 11, 17)
        # Uptrend Low Volitility
        # self.SetStartDate(2006, 7, 14)
        # self.SetEndDate(2007, 2, 16)

        # UDOW Regime Dates
        get_yahoo_data(self.ticker, '2011-08-04', '2018-12-21')
        # Downtrend High Volitility
        # self.SetStartDate(2018, 9, 21)
        # self.SetEndDate(2018, 12, 21)
        # Downtrend Low Volitility
        # self.SetStartDate(2012, 5, 1)
        # self.SetEndDate(2012, 6, 1)
        # Lateral High Volitility
        # self.SetStartDate(2011, 8, 4)
        # self.SetEndDate(2011, 10, 19)
        # Lateral Low Volitility
        # self.SetStartDate(2016, 9, 9)
        # self.SetEndDate(2016, 11, 3)
        # Uptrend High Volitility
        # self.SetStartDate(2014, 2, 3)
        # self.SetEndDate(2014, 9, 18)
        # Uptrend Low Volitility
        self.SetStartDate(2012, 11, 15)
        self.SetEndDate(2013, 5, 24)

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
        close = data[self.ticker].Close
        short_sma_high = self.moving_averages_high[0].Current.Value
        short_sma_low = self.moving_averages_low[0].Current.Value
        long_sma_high = self.moving_averages_high[1].Current.Value
        long_sma_low = self.moving_averages_low[1].Current.Value

        # buy signal
        # shorter sma range > longer sma range indicates range expansion and trend continuation
        # current close price > longer sma close price indicates bullish price movement
        # this indicates that bullish trend will likely continue so buy signal is issued
        if short_diff > long_diff and close > short_sma_high and self.trade_status[0] == 0:
            self.trade_status[0] = 1
            # resetting trade_status[1] since this means that range expansion has occurred and
            # range contraction needs to be reset for when it occurs again
            self.trade_status[1] = 0
            changed = True

        # buy signal
        # shorter sma range < longer sma range indicates range contraction and trend reversal
        # current close price < longer sma close price indicates bearish price movement
        # this indicates that bearish trend will likely reverse so buy signal is issued
        if short_diff < long_diff and close < short_sma_low and self.trade_status[0] == 0:
            self.trade_status[0] = 1
            # resetting trade_status[1] since this means that range contraction has occurred and
            # range contraction needs to be reset for when it occurs again
            self.trade_status[1] = 0
            changed = True

        # # sell signal
        # # shorter sma range < longer sma range indicates range contraction and trend reversal
        # # current close price > longer sma close price indicates bullish price movement
        # # this indicates that bullish trend will likely reverse so sell signal is issued
        # if short_diff < long_diff and close > short_sma_high and self.trade_status[1] == 0:
        #     self.trade_status[1] = 1
        #     # resetting trade_status[0] since this means that range contraction has occurred and
        #     # so range expansion needs to be reset for when it occurs again
        #     self.trade_status[0] = 0
        #     changed = True

        # sell signal
        # shorter sma range > longer sma range indicates range expansion and trend continuation
        # current close price < longer sma close price indicates bearish price movement
        # this indicates that bearish trend will likely continue so sell signal is issued
        if short_diff > long_diff and close < short_sma_low and self.trade_status[1] == 0:
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
#                f"Short Close: {short_close} Long Close: {long_close} Short Diff: {short_diff} Long Diff: {long_diff}")
            self.Debug("HOLDINGS AFTER CHANGE: QUANTITY - " +
                       str(self.Portfolio[self.symbol].Quantity) + " VALUE - " +
                       str(self.Portfolio.TotalHoldingsValue))
            self.Debug(
                f"{self.symbol.Value} - {self.Time}: Close={data[self.symbol].Close}")
            self.Debug(
                f"PORTFOLIO VALUE: {self.Portfolio.TotalPortfolioValue}")
            self.Debug(" ")
