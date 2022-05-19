from AlgorithmImports import *
from QuantConnect.Indicators import *
from yahoo_utils import *
from regime_utils import *
from datetime import datetime


class SMA_ROC_RSI(QCAlgorithm):   
    def Initialize(self):        
        self.moving_averages_close = []
        self.moving_averages_high = []
        self.moving_averages_low = []
        self.ma_lengths = [5, 10, 20, 62]
        self.trade_status = len(self.ma_lengths) * [0]
      #  self.percent = 1.0
       
        # Configure necessary initialization data
        self.ticker = "AAPL"
        start_date = datetime(2015, 7, 21)
        end_date = datetime(2016, 5, 17)
        
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
        
        #Relative Strength index method - adjust period as needed
        self.rsi = self.RSI(self.symbol, 14) 

        
    def OnData(self, data):
        if self.IsWarmingUp:
            return

        if not self.rsi.IsReady: #making sure indicator is ready to be use
            return

        #define open and close prices
        self.open_price = round((data[self.symbol].Open), 2)
        self.close_price = round((data[self.symbol].Close), 2)

        #Rate of change calculated
        self.roc_since_open = ((self.close_price - self.open_price) / self.open_price) * 100
        self.roc_rounded = round(self.roc_since_open, 1)

        #Momentum calculated
        self.mom = (self.close_price - self.open_price) * 100
        self.mom_rounded = round(self.mom, 1)

        changed = False
        for i in range(len(self.ma_lengths)):
            #if cross under the SMA high, confirm with RSI before buying
            if data[self.ticker].Close > self.moving_averages_high[i].Current.Value and self.trade_status[i] == 0:
                
                #RSI check
                if self.rsi.Current.Value <= 30:
                    self.Debug("RSI Used")
                   
                    #  RSI indication of oversold stock and ROC is slow (0.1-5%), then need to BUY
                    if (self.roc_since_open >= abs(0.1) and self.roc_since_open <= abs(5)):
                        self.Debug(f"MOM:{self.mom_rounded }, ROC: {self.roc_rounded }%  :  potentially where Momentum STARTS")
                        self.trade_status[i] = 1
                        changed = True
                      # self.percent = 1.0  # percent cash allocation                            
                        self.Debug(f"{self.Time}: **BUY based off RSI-ROC-SMA, Close={self.close_price}, MOM:{self.mom_rounded }, ROC = {self.roc_rounded}, RSI = {self.rsi}")

                    # RSI indication of oversold stock and ROC is more than +5%
                    elif self.roc_since_open > abs(5):
                        self.Debug(f"MOM:{self.mom_rounded }, ROC: {self.roc_rounded }%  :  Momentum trending positive")
                        self.trade_status[i] = 1
                        changed = True
                    #   self.percent = 0.95  # percent cash allocation
                        self.Debug(f"{self.Time}: **BUY based off RSI-ROC-SMA, Close={self.close_price}, MOM:{self.mom_rounded }, ROC = {self.roc_rounded}, RSI = {self.rsi}")

                # I did not comment out this SMA option b/c I need to force the algo to buy something even if RSI is not use
                # RSI lower bound not reached
                else:
                    self.Debug("RSI lower bound not reached")
                    self.trade_status[i] = 1
                    changed = True
                   # self.percent = 0.95 # percent cash allocation
                    self.Debug(f"{self.Time}: **BUY based off only SMA,  Close={self.close_price}, MOM:{self.mom_rounded }, ROC = {self.roc_rounded}, RSI = {self.rsi}")

            # if cross over the SMA low, confirm with RSI before selling
            if data[self.ticker].Close < self.moving_averages_low[i].Current.Value and self.trade_status[i] == 1:
           
            # RSI check
                if self.rsi.Current.Value >= 70:
                    self.Debug("RSI Used")
                   
                    # RSI indication of overbought stock and ROC slowing down
                    if (self.roc_since_open >= abs(0.1) and self.roc_since_open <= abs(5)):
                        self.Debug(f"MOM:{self.mom_rounded }, ROC: {self.roc_rounded }%  :  Momentum maybe slowing down")
                        self.trade_status[i] = 0
                        changed = True
                     #  self.percent = 0.95 #  percent cash allocation  
                        self.Debug(f"{self.Time}: **SELL based off RSI-ROC-SMA, Close={self.close_price}, MOM:{self.mom_rounded }, ROC = {self.roc_rounded}, RSI = {self.rsi}")

                    # RSI indication of overbought stock and ROC now trending negative
                    elif self.roc_since_open < 0:
                        self.Debug(f"MOM:{self.mom_rounded }, ROC: {self.roc_rounded }%  :  Momentum trending negative")
                        self.trade_status[i] = 0
                        changed = True
                      #  self.percent = 1.0  #  percent cash allocation
                        self.Debug(f"{self.Time}: **SELL based off RSI-ROC-SMA, Close={self.close_price}, MOM:{self.mom_rounded }, ROC = {self.roc_rounded}, RSI = {self.rsi}")

                # Code block commented out b/c I want to force sell only if RSI >= 70
                 #   RSI upper bound not reached
                # else:
                #     self.Debug("RSI upper bound not reached")
                #     self.trade_status[i] = 0 
                #     changed = True
                    
                # RSI not enabled but ROC has slowed alot when SMA crosses over SMA low
                if (self.roc_since_open >= abs(0.1) and self.roc_since_open <= abs(5)):
                    self.Debug("RSI upper bound not reached but ROC is slowing down")
                    self.trade_status[i] = 0 
                    changed = True
                 #  self.percent = 0.9  # percent cash allocation
                    self.Debug(f"{self.Time}: **SELL based off SMA-ROC,  Close={self.close_price}, MOM:{self.mom_rounded }, ROC = {self.roc_rounded}, RSI = {self.rsi}")

       # print
        self.Debug(f"{self.Time}: , Close={self.close_price}, MOM:{self.mom_rounded }, ROC = {self.roc_rounded}, RSI = {self.rsi}")


       
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
