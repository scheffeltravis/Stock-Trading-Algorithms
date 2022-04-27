from AlgorithmImports import *
from yahoo_reader import YahooData
from yahoo_loader import *
from QuantConnect.Indicators import *


class ClimaxAlgorithm(QCAlgorithm):
    def __init__(self):
        self.moving_average_volume = 0
        self.moving_average_length = 20
        self.ticker = "SOXL"

    def Initialize(self):
        # Get the stock data from YF for the given timeframe
        get_yahoo_data(self.ticker, '2018-01-01', '2022-04-26')
        self.SetStartDate(2018, 1, 1)
        self.SetEndDate(2022, 4, 25)

        # Set cash and warmup for investment tracking
        self.SetCash(100000)
        self.SetWarmUp(20)

        # Coerce stock data into Equity data for analyzing
        self.symbol = self.AddData(YahooData, self.ticker, Resolution.Daily).Symbol

        # Create SimpleMovingAverage to track previous trade volumes
        self.sma = self.SMA(self.symbol, self.moving_average_length, Resolution.Daily, Field.Volume)


    def OnData(self, data):
        # Wait for indicators to be warmed up
        if self.IsWarmingUp:
            return

        high_volume_day = False

        # Check if current volume is at least 2x moving average
        if data[self.symbol].Volume >= 2 * self.sma.Current.Value:
            high_volume_day = True
            # self.Debug(f"{self.Time}: Volume = {data[self.symbol].Volume}, MA Volume = {self.sma.Current.Value}")

        # Execute a limit order for 10% of available cash, if high volume day
        if high_volume_day:
            # self.SetHoldings(self.symbol, .1)
            buying_power = self.Portfolio.Cash * .1
            quantity = buying_power // data[self.symbol].Value
            self.LimitOrder(self.symbol, quantity, round(data[self.symbol].Value, 2))
        
            self.Debug("Holdings After Buy: Shares - " + 
                       str(self.Portfolio[self.symbol].Quantity) +
                       ", Value - " + 
                       str(self.Portfolio.TotalHoldingsValue))