from AlgorithmImports import *
from sqlalchemy import false
from yahoo_reader import YahooData
from yahoo_loader import *
from QuantConnect.Indicators import *


class SMAAlgorithm(QCAlgorithm):
   # def __init__(self):
    def Initialize(self):
        self.moving_averages_close = []
        self.moving_averages_high = []
        self.moving_averages_low = []
        self.ma_lengths = [5, 10, 20, 62]
        self.trade_status = len(self.ma_lengths) * [0]
<<<<<<< HEAD
        #self.ticker = "TQQQ"
        #self.ticker = "UDOW"        
        # self.ticker = "^GSPC"
        #self.ticker = "TQQQ"
        #self.ticker = "TNA"
        #self.ticker = "^IXIC"
        #self.ticker = "UPRO"
        # self.ticker = "UDOW"
        self.ticker = "SOXL"

   
        get_yahoo_data(self.ticker, '2021-01-01', '2022-01-01')

        self.SetStartDate(2021, 1, 1)
        self.SetEndDate(2022, 1, 1)
=======
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
        # self.SetStartDate(2012, 2, 1)
        # self.SetEndDate(2012, 9, 28)
        # Uptrend Low Volitility
        # self.SetStartDate(1990, 11, 1)
        # self.SetEndDate(1991, 2, 27)

>>>>>>> d6d6dfb761b3d4b6884c6162d42d04c1d7212755
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

        # could not get data from data.bars but data[self.ticker].Close appears to be working
        # bar = data.Bars[self.symbol]
        # bar = data.Bars[self.ticker]

        changed = False
        for i in range(len(self.ma_lengths)):
            # self.Debug("CLOSING PRICE " + str(data[self.ticker].Close))
            # self.Debug("TRADE STATUS " + str(self.trade_status))
            # self.Debug("M.A. HIGH CUR VALUE " +
            #            str(self.moving_averages_high[i].Current.Value))
            # self.Debug("M.A. LOW CUR VALUE " +
            #            str(self.moving_averages_low[i].Current.Value))
            # self.Debug(str(changed))
            if data[self.ticker].Close > self.moving_averages_high[i].Current.Value and self.trade_status[i] == 0:
                self.trade_status[i] = 1
                changed = True

            if data[self.ticker].Close < self.moving_averages_low[i].Current.Value and self.trade_status[i] == 1:
                self.trade_status[i] = 0
                changed = True

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
