from AlgorithmImports import *
from sqlalchemy import false
from yahoo_utils import *
from QuantConnect.Indicators import *


class RangeAlgorithm(QCAlgorithm):
    def Initialize(self):
        self.moving_averages_close = []
        self.moving_averages_high = []
        self.moving_averages_low = []
        self.ma_lengths = [6, 18]
        self.trade_status = [0, 0]
        self.prev_close_price = 0
        self.compare_price = 0
        # self.ticker = "^GSPC"
        # self.ticker = "TQQQ"
        self.ticker = "TNA"
        # self.ticker = "^IXIC"
        # self.ticker = "UPRO"
        # self.ticker = "SOXL"
        # self.ticker = "SPXL"
        # self.ticker = "FAS"
        # self.ticker = "SPY"
        # self.ticker = "UDOW"
        # self.ticker = "SDOW"
        # self.ticker = "AAPL"

        # get_yahoo_data(self.ticker, '1990-11-01', '2019-03-07')
        get_yahoo_data(self.ticker, '2020-01-01', '2022-05-20')
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
        self.SetStartDate(2020, 1, 1)
        # self.SetEndDate(2022, 1, 1)
        self.SetEndDate(2022, 5, 20)

        # SPY Regime Dates
        # get_yahoo_data(self.ticker, '2008-05-19', '2019-10-25')
        # Downtrend High Volitility
        # self.SetStartDate(2015, 7, 20)
        # self.SetEndDate(2016, 2, 9)
        # Downtrend Low Volitility
        # self.SetStartDate(2008, 5, 19)
        # self.SetEndDate(2009, 3, 5)
        # Lateral High Volitility
        # self.SetStartDate(2009, 9, 16)
        # self.SetEndDate(2010, 7, 19)
        # Lateral Low Volitility
        # self.SetStartDate(2019, 5, 1)
        # self.SetEndDate(2019, 10, 25)
        # Uptrend High Volitility
        # self.SetStartDate(2011, 8, 19)
        # self.SetEndDate(2012, 9, 11)
        # Uptrend Low Volitility
        # self.SetStartDate(2010, 8, 31)
        # self.SetEndDate(2011, 4, 16)

        # UDOW Regime Dates
        # get_yahoo_data(self.ticker, '2010-07-06', '2022-05-13')
        # Downtrend High Volitility
        # self.SetStartDate(2021, 11, 8)
        # self.SetEndDate(2022, 5, 13)
        # Downtrend Low Volitility
        # self.SetStartDate(2019, 11, 1)
        # self.SetEndDate(2020, 3, 19)
        # Lateral High Volitility
        # self.SetStartDate(2012, 2, 3)
        # self.SetEndDate(2012, 11, 8)
        # Lateral Low Volitility
        # self.SetStartDate(2016, 7, 12)
        # self.SetEndDate(2016, 11, 4)
        # Uptrend High Volitility
        # self.SetStartDate(2011, 8, 10)
        # self.SetEndDate(2012, 4, 26)
        # Uptrend Low Volitility
        # self.SetStartDate(2010, 7, 6)
        # self.SetEndDate(2011, 4, 28)

        # SDOW Regime Dates
        # get_yahoo_data(self.ticker, '2010-02-12', '2022-05-12')
        # Downtrend High Volitility
        # self.SetStartDate(2010, 2, 12)
        # self.SetEndDate(2011, 2, 23)
        # Downtrend Low Volitility
        # self.SetStartDate(2020, 11, 12)
        # self.SetEndDate(2021, 11, 23)
        # Lateral High Volitility
        # self.SetStartDate(2014, 12, 24)
        # self.SetEndDate(2015, 8, 14)
        # Lateral Low Volitility
        # self.SetStartDate(2012, 1, 25)
        # self.SetEndDate(2012, 7, 20)
        # Uptrend High Volitility
        # self.SetStartDate(2021, 11, 8)
        # self.SetEndDate(2022, 5, 12)
        # Uptrend Low Volitility
        # self.SetStartDate(2019, 9, 27)
        # self.SetEndDate(2020, 3, 23)

        # AAPL Regime Dates
        # get_yahoo_data(self.ticker, '2009-04-09', '2016-05-17')
        # Downtrend High Volitility
        # self.SetStartDate(2015, 7, 21)
        # self.SetEndDate(2016, 5, 17)
        # Downtrend Low Volitility
        # self.SetStartDate(2012, 9, 21)
        # self.SetEndDate(2013, 7, 18)
        # Lateral High Volitility
        # self.SetStartDate(2015, 8, 26)
        # self.SetEndDate(2016, 4, 7)
        # Lateral Low Volitility
        # self.SetStartDate(2010, 12, 7)
        # self.SetEndDate(2011, 6, 24)
        # Uptrend High Volitility
        # self.SetStartDate(2010, 1, 6)
        # self.SetEndDate(2011, 1, 13)
        # Uptrend Low Volitility
        # self.SetStartDate(2009, 4, 9)
        # self.SetEndDate(2010, 4, 23)

        self.SetCash(100000)
        self.SetWarmUp(TimeSpan.FromDays(18))

        self.symbol = self.AddData(
            YahooData, self.ticker, Resolution.Daily).Symbol

        # self.inverse_symbol = self.AddData(
        #     YahooData, self.inverse_ticker, Resolution.Daily).Symbol

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
            self.trade_status[1] = 0
            changed = True
            self.prev_close_price = data[self.ticker].Close
            # self.compare_price = data[self.ticker].Close

        # buy signal
        # shorter sma range < longer sma range indicates range contraction and trend reversal
        # shorter sma close price < longer sma close price indicates bearish price movement
        # this indicates that bearish trend will likely reverse so buy signal is issued
        if short_diff < long_diff and short_close < long_close and self.trade_status[0] == 0:
            self.trade_status[0] = 1
            self.trade_status[1] = 0
            changed = True
            self.prev_close_price = data[self.ticker].Close
            # self.compare_price = data[self.ticker].Close

        # sell signal
        # shorter sma range < longer sma range indicates range contraction and trend reversal
        # shorter sma close price > longer sma close price indicates bullish price movement
        # this indicates that bullish trend will likely reverse so sell signal is issued
        if short_diff < long_diff and short_close > long_close and self.trade_status[1] == 0:
            self.trade_status[1] = 1
            self.trade_status[0] = 0
            changed = True

        # sell signal
        # shorter sma range > longer sma range indicates range expansion and trend continuation
        # shorter sma close price < longer sma close price indicates bearish price movement
        # this indicates that bearish trend will likely continue so sell signal is issued
        if short_diff > long_diff and short_close < long_close and self.trade_status[1] == 0:
            self.trade_status[1] = 1
            self.trade_status[0] = 0
            changed = True

        # # STOP LOSS
        # # sells if the current day's close price is at least 1% less than the previous day's
        # # revert back to previous stop loss
        # # self.Debug("prev_close_price BEFORE: " + str(self.prev_close_price))
        # # self.Debug("Compare Price BEFORE: " + str(self.compare_price))
        # # self.Debug("data[self.ticker].Close BEFORE: " + str(data[self.ticker].Close))
        # self.Debug("TRADE STATUS BEFORE: " + str(self.trade_status))
        # if self.trade_status[0] == 1:
        #     self.compare_price = data[self.ticker].Close
        #     # self.compare_price = data[self.ticker].Close + \
        #     # (data[self.ticker].Close * .01)
        #     self.Debug("Compare Price UPDATED (pre cond): " +
        #                str(self.compare_price))
        #     self.Debug("prev_close_price (pre cond): " +
        #                str(self.prev_close_price))
        #     # self.Debug("Compare Price: " + str(self.compare_price))
        #     if self.prev_close_price > self.compare_price:
        #         self.Debug("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!STOP LOSS TRIGGERED")
        #         self.trade_status[1] = 1
        #         self.trade_status[0] = 0
        #         changed = True
        #     else:
        #         # updates prev_close_price to current day
        #         self.prev_close_price = data[self.ticker].Close
        #         # self.prev_close_price = self.compare_price
        #         # self.compare_price = data[self.ticker].Close

        self.Debug("prev_close_price AFTER: " + str(self.prev_close_price))
        self.Debug("Compare Price AFTER: " + str(self.compare_price))

        if changed:
            self.Debug("HOLDINGS BEFORE CHANGE: QUANTITY - " +
                       str(self.Portfolio[self.symbol].Quantity) + " VALUE - " +
                       str(self.Portfolio.TotalHoldingsValue))
            self.Debug("TRADE STATUS " + str(self.trade_status))
            if self.trade_status[0] == 1:
                # self.SetHoldings(self.inverse_symbol, 0)
                self.SetHoldings(self.symbol, 1)
                self.Debug("BUY ORDER TRIGGERED")
            if self.trade_status[1] == 1:
                self.SetHoldings(self.symbol, 0)
                # self.SetHoldings(self.inverse_symbol, 1)
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
