from AlgorithmImports import *
from QuantConnect.Indicators import *
from yahoo_utils import *
from regime_utils import *
from datetime import datetime


class ClimaxAlgorithm(QCAlgorithm):
    def Initialize(self):
        self.moving_average_volume = 0
        self.rolling_window_length = 10
        self.trade_status = [0, 0]

        # Configure necessary initialization data
        self.ticker = "SOXL"
        start_date = datetime(2010, 3, 1)
        end_date = datetime(2022, 5, 1)
        
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
        self.SetStartDate(start_date.year, start_date.month, start_date.day + 10)    # Need to start after rolling window
        self.SetEndDate(end_date.year, end_date.month, end_date.day)

        # Get the stock data from YF for the given timeframe
        get_yahoo_data(self.ticker, start_date, end_date)

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
