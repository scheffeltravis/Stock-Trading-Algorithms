from AlgorithmImports import *
from QuantConnect.Indicators import *
from sqlalchemy import false
from yahoo_utils import *
from regime_utils import *
from datetime import datetime


class RangeAlgorithm(QCAlgorithm):
    def Initialize(self):
        self.moving_averages_close = []
        self.moving_averages_high = []
        self.moving_averages_low = []
        self.ma_lengths = [6, 18]
        self.trade_status = [0, 0]
        
        # Configure necessary initialization data
        self.ticker = "AAPL"
        start_date = datetime(1990, 11, 1)
        end_date = datetime(1991, 2, 27)
        
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
            # resetting trade_status[1] since this means that range contraction has occurred and
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
