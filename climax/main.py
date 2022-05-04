from AlgorithmImports import *
from yahoo_reader import YahooData
from yahoo_loader import *
from QuantConnect.Indicators import *


class ClimaxAlgorithm(QCAlgorithm):
    def Initialize(self):
        self.moving_average_volume = 0
        self.rolling_window_length = 10
        self.trade_status = [0, 0]
        self.ticker = "SOXL"
        # self.ticker = "AAPL"

        # Get the stock data from YF for the given timeframe
        get_yahoo_data(self.ticker, '1990-11-01', '2022-05-04')
        self.SetStartDate(2018, 1, 10)    # Need to start after rolling window
        self.SetEndDate(2022, 5, 4)

        # AAPL Regime Dates
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
        # self.SetStartDate(1990, 11, 10)
        # self.SetEndDate(1991, 2, 27)

        # Set cash and warmup for investment tracking
        self.SetCash(100000)
        self.SetWarmUp(10)

        # Coerce stock data into Equity data for analyzing
        self.symbol = self.AddData(YahooData, self.ticker, Resolution.Daily).Symbol

        # Create a RollingWindow to track the most recent price movements/slopes
        self.slopeWindow = RollingWindow[float](self.rolling_window_length)

        # Create SimpleMovingAverage to track previous trade volumes
        self.sma = self.SMA(self.symbol, self.rolling_window_length, Resolution.Daily, Field.Volume)

    def OnData(self, data):
        # Wait for indicators to be warmed up
        if self.IsWarmingUp:
            return

        changed = False

        # Calculate price movement/slope
        slope = data[self.symbol].High - data[self.symbol].Low

        # Check if current volume is at least 2x moving average
        if data[self.symbol].Volume >= 2 * self.sma.Current.Value:

            # If movement is larger than average of rolling window
            if slope > sum(self.slopeWindow) / self.rolling_window_length:

                # Get current movement direction
                direction = data[self.symbol].Close - data[self.symbol].Open

                # Buy signal
                # Coming out of bear market cycle, we should execute a buy order
                if direction < 0:
                    self.trade_status[0] = 1
                    # Reset trade_status[1] since we are closing a bear market cycle and
                    # we must wait for the next cycle close for it to occur again
                    self.trade_status[1] = 0
                    changed = True
                
                # Sell signal
                # Coming out of bull market cycle, we should execute a sell order
                elif direction > 0:
                    self.trade_status[1] = 1
                    # Reset trade_status[0] since we are closing a bull market cycle and
                    # we must wait for the next cycle close for it to occur again
                    self.trade_status[0] = 0
                    changed = True

        if changed:
            self.Debug("HOLDINGS BEFORE CHANGE: QUANTITY - " +
                       str(self.Portfolio[self.symbol].Quantity) + " VALUE - " +
                       str(self.Portfolio.TotalHoldingsValue))

            if self.trade_status[0] == 1:
                self.SetHoldings(self.symbol, 1)
                self.Debug("BUY ORDER TRIGGERED")

            if self.trade_status[1] == 1:
                self.SetHoldings(self.symbol, 0)
                self.Debug("SELL ORDER TRIGGERED")

            self.Debug("HOLDINGS AFTER CHANGE: QUANTITY - " +
                       str(self.Portfolio[self.symbol].Quantity) + " VALUE - " +
                       str(self.Portfolio.TotalHoldingsValue))
            self.Debug(
                f"{self.symbol.Value} - {self.Time}: Close={data[self.symbol].Close}")
            self.Debug(
                f"PORTFOLIO VALUE: {self.Portfolio.TotalPortfolioValue}")
            self.Debug(" ")

        # Add price slope to rolling window at end of trading day
        self.slopeWindow.Add(slope)