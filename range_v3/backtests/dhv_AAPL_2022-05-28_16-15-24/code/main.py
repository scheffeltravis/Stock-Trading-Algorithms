from AlgorithmImports import *
from sqlalchemy import false
from yahoo_utils import *
from regime_utils import *
from QuantConnect.Indicators import *


class RangeAlgorithm(QCAlgorithm):
    def Initialize(self):
        self.moving_averages_close = []
        self.moving_averages_high = []
        self.moving_averages_low = []
        self.moving_averages_close_2 = []
        self.moving_averages_high_2 = []
        self.moving_averages_low_2 = []
        self.ma_lengths = [6, 18]
        # self.ma_lengths = [5, 80]
        # self.ma_lengths_2 = [6, 18, 30, 42]
        self.ma_lengths_2 = [5, 10, 20, 62]
        # self.ma_lengths_2 = [5, 10, 20]
        self.trade_status = len(self.ma_lengths_2) * [0]
        self.prev_close_price = 0
        self.compare_price = 0

        # Configure necessary initialization data
        self.ticker = "UDOW"
        start_date = datetime(2012, 11, 15)
        end_date = datetime(2013, 5, 24)
        
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

        self.SetCash(100000)
        # self.SetWarmUp(100)
        self.SetWarmUp(TimeSpan.FromDays(62))

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

        for i in range(len(self.ma_lengths_2)):
            self.sma = self.HMA(
                self.symbol, self.ma_lengths_2[i], Resolution.Daily, Field.Close)
            self.moving_averages_close_2.append(self.sma)
            self.sma = self.HMA(
                self.symbol, self.ma_lengths_2[i], Resolution.Daily, Field.High)
            self.moving_averages_high_2.append(self.sma)
            self.sma = self.HMA(
                self.symbol, self.ma_lengths_2[i], Resolution.Daily, Field.Low)
            self.moving_averages_low_2.append(self.sma)

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

        for i in range(len(self.ma_lengths_2)):
            # buy signal
            # shorter sma range > longer sma range indicates range expansion and trend continuation
            # shorter sma close price > longer sma close price indicates bullish price movement
            # this indicates that bullish trend will likely continue so buy signal is issued
            if short_diff > long_diff and close > self.moving_averages_high_2[i].Current.Value and self.trade_status[i] == 0:
                self.trade_status[i] = 1
                changed = True
                self.prev_close_price = data[self.ticker].Close
                # self.compare_price = data[self.ticker].Close

            # buy signal
            # shorter sma range < longer sma range indicates range contraction and trend reversal
            # shorter sma close price < longer sma close price indicates bearish price movement
            # this indicates that bearish trend will likely reverse so buy signal is issued
            if short_diff < long_diff and close < self.moving_averages_low_2[i].Current.Value and self.trade_status[i] == 0:
                self.trade_status[i] = 1
                changed = True
                self.prev_close_price = data[self.ticker].Close
                # self.compare_price = data[self.ticker].Close

            # sell signal
            # shorter sma range < longer sma range indicates range contraction and trend reversal
            # shorter sma close price > longer sma close price indicates bullish price movement
            # this indicates that bullish trend will likely reverse so sell signal is issued
            if short_diff < long_diff and close > self.moving_averages_high_2[i].Current.Value and self.trade_status[i] == 0:
                self.trade_status[i] = 0
                changed = True

            # sell signal
            # shorter sma range > longer sma range indicates range expansion and trend continuation
            # shorter sma close price < longer sma close price indicates bearish price movement
            # this indicates that bearish trend will likely continue so sell signal is issued
            if short_diff > long_diff and close < self.moving_averages_low_2[i].Current.Value and self.trade_status[i] == 0:
                self.trade_status[i] = 0
                changed = True

        # tracks price after buy signal
        # sells if the current day's close price is at least 1% less than the previous day's
        # self.Debug("prev_close_price BEFORE: " + str(self.prev_close_price))
        # self.Debug("data[self.ticker].Close BEFORE: " + str(data[self.ticker].Close))
        self.Debug("TRADE STATUS BEFORE: " + str(self.trade_status))
        if sum(self.trade_status) > 0:
            self.compare_price = data[self.ticker].Close + (data[self.ticker].Close * .01)
            # + (data[self.ticker].Close * .01)
            self.Debug("Compare Price UPDATED (pre cond): " + str(self.compare_price))
            self.Debug("prev_close_price (pre cond): " + str(self.prev_close_price))
            if self.prev_close_price > self.compare_price:
                self.Debug("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!STOP LOSS TRIGGERED")
                self.trade_status = len(self.ma_lengths_2) * [0]
                changed = True
            else:
                # updates prev_close_price to current day
                # self.prev_close_price = self.compare_price
                self.compare_price = data[self.ticker].Close
                self.Debug("PRICES HAVE BEEN CHANGED")
        
        self.Debug("prev_close_price AFTER: " + str(self.prev_close_price))
        self.Debug("Compare Price AFTER: " + str(self.compare_price))


        if changed:
            self.Debug("HOLDINGS BEFORE CHANGE: QUANTITY - " +
                       str(self.Portfolio[self.symbol].Quantity) + " VALUE - " +
                       str(self.Portfolio.TotalHoldingsValue))
            self.Debug("TRADE STATUS " + str(self.trade_status))
            buy_signals = sum(self.trade_status)
            percentage = buy_signals / len(self.ma_lengths_2)
            self.SetHoldings(self.symbol, percentage)
            self.Debug("HOLDINGS AFTER CHANGE: QUANTITY - " +
                       str(self.Portfolio[self.symbol].Quantity) + " VALUE - " +
                       str(self.Portfolio.TotalHoldingsValue))
            self.Debug(
                f"{self.symbol.Value} - {self.Time}: Close={data[self.symbol].Close}")
            self.Debug(
                f"PORTFOLIO VALUE: {self.Portfolio.TotalPortfolioValue}")
            self.Debug(" ")
