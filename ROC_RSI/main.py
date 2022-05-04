from AlgorithmImports import *
from QuantConnect.Indicators import *
from yahoo_reader import YahooData
from yahoo_loader import *
from QuantConnect.Indicators import *



class SMA_ROC_RSI(QCAlgorithm):  
    def Initialize(self):
        self.moving_averages_close = []
        self.moving_averages_high = []
        self.moving_averages_low = []
        # self.ma_lengths = [5, 10, 20, 62]
        self.ma_lengths = [62]
        self.trade_status = len(self.ma_lengths) * [0]
       
        #self.ticker = "UDOW"        
        # self.ticker = "^GSPC"
        self.ticker = "TQQQ"
        #self.ticker = "TNA"
        #self.ticker = "^IXIC"
        #self.ticker = "UPRO"
        # self.ticker = "UDOW"
        #self.ticker = "SOXL"
   
        get_yahoo_data(self.ticker, '2021-01-01', '2022-01-01')
        self.SetStartDate(2021, 1, 1)
        self.SetEndDate(2022, 1, 1)
        self.SetCash(100000)
        self.SetWarmUp(100)

        self.symbol = self.AddData(
            YahooData, self.ticker, Resolution.Daily).Symbol
        
        #Relative Strength index method - adjust period as needed
        self.rsi = self.RSI(self.symbol, 14) 

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
            #SMA to BUY         
            if data[self.ticker].Close > self.moving_averages_high[i].Current.Value and self.trade_status[i] == 0:
                self.trade_status[i] = 1
                changed = True
                self.Debug(f"{self.Time}: *Order to BUY - based off SMA")
            
                # ****ROC Indicator****                              
                #if the ROC is +0.1-5%, then this could begining of momentum
                if self.roc_since_open > 0.1 and self.roc_since_open < 5 and self.trade_status[i] == 0:
                    self.Debug(f"MOM:{self.mom_rounded }, ROC: {self.roc_rounded }%  :  MOM Start point")                                  
                
                # #if the ROC is +5% or greater, then this could be momentum climbing
                if self.roc_since_open >= 5 and self.trade_status[i] == 0:
                   self.Debug(f"MOM:{self.mom_rounded }, ROC: {self.roc_rounded }%  :  MOM TREND UPWARD")
                
            #SMA to SELL
            if data[self.ticker].Close < self.moving_averages_low[i].Current.Value and self.trade_status[i] == 1:
                
                #****ROC Indicator****  
                #if the ROC is 0.1-5%, then momentum slowing down
                if self.roc_since_open > 0.1 and self.roc_since_open < 5 and self.trade_status[i] == 1:
                     self.Debug(f"MOM:{self.mom_rounded }, ROC: {self.roc_rounded }%  :  MOM slowing down") 
                                        
                
                #if the ROC is negative, then sell as this is momentum downtrend                
                if self.roc_since_open < 0 and self.trade_status[i] == 1:
                    self.Debug(f"MOM:{self.mom_rounded }, ROC: {self.roc_rounded }%  :  MOM TREND DOWNWARD")
                    self.trade_status[i] = 0
                    changed = True
                    self.Debug(f"{self.Time}: *Order to SELL based off SMA & ROC")
                
           #****RSI Indicator**** - adjust RSI bounds as needed 
           # if oversold stock and ROC is trending positive, then BUY
            #if self.rsi.Current.Value <= 30 and self.trade_status[i] == 0 and self.roc_since_open > 0:
            if self.rsi.Current.Value <= 30 and self.trade_status[i] == 0:
                self.trade_status[i] = 1
                changed = True
                self.Debug(f"{self.Time}: *Order to BUY based off RSI")
                
            #if overbought stock AND (ROC trends negative OR ROC is slowing down), then SELL
            #if self.rsi.Current.Value > 70 and self.trade_status[i] == 1 and (self.roc_since_open < 0 or (self.roc_since_open > 0.1 and self.roc_since_open < 5)):
            if self.rsi.Current.Value > 70 and self.trade_status[i] == 1 and self.roc_since_open < 0:
                self.Debug("*RSI - overvalued AND ROC - momentum slowdown")
                self.trade_status[i] = 0
                changed = True
                self.Debug(f"{self.Time}: *Order to SELL based off RSI") 
                        
           # self.Debug(f"{self.Time}: Open={self.open_price}, Close={self.close_price}, MOM:{self.mom_rounded }, ROC = {self.roc_rounded}, RSI = {self.rsi}")       


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
