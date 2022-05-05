from AlgorithmImports import *
from QuantConnect.Indicators import *
from yahoo_reader import YahooData
from yahoo_loader import *
from QuantConnect.Indicators import *



class SMA_ROC_RSI(QCAlgorithm):  
    def __init__(self):
        self.moving_averages_close = []
        self.moving_averages_high = []
        self.moving_averages_low = []
        self.ma_lengths = [5, 10, 20, 62]
        self.trade_status = len(self.ma_lengths) * [0]
        # self.ticker = "^GSPC"
        # self.ticker = "TQQQ"
        # self.ticker = "TNA"
        # self.ticker = "^IXIC"
        # self.ticker = "UPRO"
        # self.ticker = "UDOW"
        # self.ticker = "SOXL"
        self.ticker = "AAPL"

    def Initialize(self):
        get_yahoo_data(self.ticker, '1990-11-01', '2019-03-07')
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
        self.SetStartDate(2012, 2, 1)
        self.SetEndDate(2012, 9, 28)
       
        # Uptrend Low Volitility
        # self.SetStartDate(1990, 11, 1)
        # self.SetEndDate(1991, 2, 27)
        
        
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
        
        if not self.rsi.IsReady: 
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
                    self.Debug("RSI indicator enabled")                    
                    #  RSI indication of oversold stock and ROC is slow (0.1-5%), then need to BUY   
                    if (self.roc_since_open >= abs(0.1) and self.roc_since_open <= abs(5)):   
                        self.trade_status[i] = 1
                      # self.SetHoldings(self, 1) #allocation 100% cash 
                        changed = True
                        self.Debug(f"{self.Time}: **BUY based off RSI-ROC-SMA, Close={self.close_price}, MOM:{self.mom_rounded }, ROC = {self.roc_rounded}, RSI = {self.rsi}")
                        self.Debug(f"MOM:{self.mom_rounded }, ROC: {self.roc_rounded }%  :  potentially where Momentum STARTS") 
                        
                    # RSI indication of oversold stock and ROC is more than +5%
                    elif self.roc_since_open > abs(5):   
                        self.trade_status[i] = 1
                      # self.SetHoldings(self, 0.90) #allocation 90% cash
                        changed = True
                        self.Debug(f"{self.Time}: **BUY based off RSI-ROC-SMA, Close={self.close_price}, MOM:{self.mom_rounded }, ROC = {self.roc_rounded}, RSI = {self.rsi}")
                        self.Debug(f"MOM:{self.mom_rounded }, ROC: {self.roc_rounded }%  :  Momentum trending positive")
                    
                # I did not comment out this SMA option b/c I need to force the algo to buy even if RSI is not enabled
                # RSI lower bound not reached, so cannot use RSI indicator (only SMA)
                else:
                    self.trade_status[i] = 1
                  #  self.SetHoldings(self.ticker, 0.75) #allocation 75% cash if only using SMA indicator
                    changed = True
                    self.Debug(f"{self.Time}: **BUY based off only SMA (NOT confirmed by RSI),  Close={self.close_price}, MOM:{self.mom_rounded }, ROC = {self.roc_rounded}, RSI = {self.rsi}")
                 
            # if cross over the SMA low, confirm with RSI before selling
            if data[self.ticker].Close < self.moving_averages_low[i].Current.Value and self.trade_status[i] == 1:                       
            # RSI check
                if self.rsi.Current.Value >= 70:
                    self.Debug("RSI indicator enabled")
                    # RSI indication of overbought stock and ROC slowing down
                    if (self.roc_since_open >= abs(0.1) and self.roc_since_open <= abs(5)):
                        self.Debug(f"MOM:{self.mom_rounded }, ROC: {self.roc_rounded }%  :  Momentum maybe slowing down")
                        self.trade_status[i] = 0  #I need to find out what method allocates portions to sell (sell at 80%)
                        changed = True
                        self.Debug(f"{self.Time}: **SELL based off RSI-ROC-SMA, Close={self.close_price}, MOM:{self.mom_rounded }, ROC = {self.roc_rounded}, RSI = {self.rsi}")                         
                    
                    # RSI indication of overbought stock and ROC now trending negative
                    elif self.roc_since_open < 0:
                        self.Debug(f"MOM:{self.mom_rounded }, ROC: {self.roc_rounded }%  :  Momentum trending negative") 
                        self.trade_status[i] = 0  #I need to find out what method allocates portions to sell at (100%)
                        changed = True
                        self.Debug(f"{self.Time}: **SELL based off RSI-ROC-SMA, Close={self.close_price}, MOM:{self.mom_rounded }, ROC = {self.roc_rounded}, RSI = {self.rsi}")  
                          
                 
                # I commented this out b/c I want to force the algo to wait and only sell if SMA is confirmed by RSI, because if I let it choose only SMA, then its not improving the Chester algo       
                #  # RSI upper bound not reached, so cannot use RSI indicator with SMA (only SMA)
                # else:
                #     self.trade_status[i] = 0 #I need to find out what method allocates portions to sell at (75%)
                #     changed = True
                #     self.Debug(f"{self.Time}: **SELL based off only SMA,  Close={self.close_price}, MOM:{self.mom_rounded }, ROC = {self.roc_rounded}, RSI = {self.rsi}")
             
   
                                 
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









        
     