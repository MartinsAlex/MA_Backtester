import pandas as pd
import numpy as np
from pandas_datareader import data, wb
import datetime as dt
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import matplotlib.dates as mdates
import matplotlib as mpl
from pandas.plotting import register_matplotlib_converters
from pandas_datareader._utils import RemoteDataError
import warnings
import math
import matplotlib.ticker as ticker
from scipy import stats as st
import sys


register_matplotlib_converters()


pd.set_option('display.max_columns', 500)
pd.set_option('display.max_rows', 250)


class movingAverageCrossover:
    '''
    The class to define the caracteristics of your moving average crossover strategy.


    Parameters
    ----------

    tickers (str list) -- The ticker or ticker list on which the strategy will be tested (examples : ["FB"] or ["AAPL", "TSLA", "AMZN", "GOOG"]). All the tickers from Yahoo and FRED (for the forex) can be used. Lists samples are available in the folder "tickerLists".

    fastMA (int) -- The number of days for the short term moving average

    slowMA (int) -- The number of days for the long term moving average

    beginDate (date, format: yyyy-mm-dd) -- The begin date of the analysis

    endDate (date, format: yyyy-mm-dd) -- The end date of the analysis

    * Key-worded args :

    shortLong (str) -- the type of position taken in the strategy. 3 possibilities :"long" : long only / "short" : short only / "both" : long and short

    capital (int) -- Initial portfolio balance. All the capital available is invested in each trade. Default is 1 million.

    maType (str) -- the type of moving average for your strategy. Default is simple. 3 possibilities : "simple" : simple moving average / "weighted" : weighted moving average / "exp" : exponentially weighted moving average

    stopLoss (float, from 0 to 1) -- stop-loss limit, in %.
        Note that : because the analysis is made on Adjusted close prices (at the end of trading days) your loss can exceed the stop-loss. (example : stop-loss of 5 %, today price of a stock is 100. If tomorrow the price drops to 90, the share will be sold and the loss will be 10 : a 10 % loss)

    takeProfit (float, from 0 to 1) -- take-profit limit, in %. Working on Adj. Close, like the stop-loss.

    rf (float) -- you can specify the risk-free rate for the statistics calculations. If not, the default risk-free rate will be the
                 13 Week Treasury Bill rate of the day (Yahoo : ^IRX)

    plot (bool) -- If True, the strategy behavior is plotted. Default is False and is recommended when you analyze multiple stocks (5 or more).

    signals (bool) -- Optionnal arg that allows you to plot all the signals, even if the balance drops under a level that makes it impossible to buy.

    Attributes
    ----------

        resultsTable :
            Pandas Dataframe containing the strategy statistics. Some specific stats explained :
            - "Total return" : in comparaison to "Total realized return", this is the realized return plus the open position return
            - "Buy & Hold Return" : the return that you would have made if you bought the asset and holded it till the end
            - "Open position (price)" : If < 0 , it is a short position.
            - "Out/Under-performance %" : Underperform if this stats is < 0
            - The Value at Risk is a normal parametric VaR

        transactionTable :
            Pandas Dataframe containing all the transactions that would have been made by the strategy.

        portfolioBalanceEvolution :
            Pandas Serie containing the evolution of the portfolio balance (with dates)

    '''

    def __init__(self, tickers, fastMA, slowMA, beginDate, endDate, **kwargs):

        self.tickers = tickers
        self.beginDate = beginDate
        self.endDate = endDate
        self.fastMA = fastMA
        self.slowMA = slowMA

        # Kwargs :
        self.initialBalance = kwargs.get('capital', 1_000_000)
        self.shortLong = kwargs.get('shortLong', "long")
        self.maType = kwargs.get('maType', "simple")
        self.stopLoss = kwargs.get('stopLoss', None)
        self.takeProfit = kwargs.get('takeProfit', None)
        self.rf = kwargs.get("rf", None)
        self.__makeplot = kwargs.get("plot", False)
        self.__allSignals = kwargs.get("signals", False)
        self.commission = kwargs.get("commission", False)


    def analyse(self):

        '''
        The method that runs the analysis.

        '''

        # Table containing final results
        resultsTable = pd.DataFrame(
            columns=["From", "To", "Ticker", "Number of Trades", "Winning Trades", "Losing Trades",
                     "Largest Winning Trade", "Largest Losing Trade", "Win Rate", "Expectancy", "Total Realized Return", "Total Return",
                     "Buy & Hold Return", "Asset Return %", "Strategy Realized Return %", "Out/Under-performance %", 'Asset Annualized Return %', 'Strategy Annualized Return %',
                     "Open position (price)", "Open Trade P/L",  "Asset Annualized Volatility", "Strategy Annualized Volatility", "Asset Sharpe Ratio", "Strategy Sharpe Ratio",
                     "Asset Max Drawdown", "Strategy Max Drawdown", "Market Exposure", "99 % Strategy Daily VaR", "99 % Asset Daily VaR",
                     "Asset Daily Avg Volume", "Avg Holding Days", "Initial Capital",
                     "Final Capital", "Used Stop-Loss", "Used Take-Profit", "Total fees payed"])  # Result table with column names

        # Table of transactions
        transactionTable = pd.DataFrame(columns=["Date", "Type", "Price", "Ticker", "P/L", "Number of shares"])

        print(os.path.dirname(os.path.realpath(__file__)))
        # Read the csv list of Forex Tickers
        forexFREDlist = pd.read_csv("tickerLists/forex_tickers.csv", sep=";")
        forexFREDlist = forexFREDlist.iloc[:, 0]


        # Pairs who are indirectly quoted (Foreign/USD)
        forexIndirect = ["DEXBZUS", "DEXCAUS", "DEXCHUS", "DEXDNUS", "DEXHKUS", "DEXINUS", "DEXJPUS", "DEXMAUS",
                         "DEXMXUS", "DEXTAUS", "DEXNOUS", "DEXSIUS", "DEXSFUS", "DEXKOUS", "DEXSLUS", "DEXSDUS",
                         "DEXSZUS", "DEXTHUS"]

        x = 1  # Indexer for results tables

        for symbol in self.tickers:  # We begin the boucle that will iterate on every tickers

            ######################################################
            # 1st step : identify the source and download prices #
            ######################################################

            symbol = str.upper(symbol)

            if symbol in list(forexFREDlist):  # Ticker is a forex one
                self.AssetDf = data.get_data_fred(symbol, self.beginDate, self.endDate).dropna()  # We use pandas_datareader function to download the datas and we drop NaN values
                priceColumn = symbol  # We fix the price column name

                if symbol in forexIndirect:  # If the forex is indirectyl quoted, we inverse his price to reflect his value in USD
                    self.AssetDf[symbol] = self.AssetDf[symbol] ** (-1)

            else: # It's a Yahoo ticker

                try:
                    self.AssetDf = data.get_data_yahoo(symbol, self.beginDate, self.endDate, interval='d').dropna()
                except (KeyError, OverflowError, RemoteDataError):  # Request can return an error
                    print("Something went wrong with {}. Problem may come from date or ticker.".format(symbol))
                    resultsTable.loc[x, ["Ticker"]] = symbol
                    x += 1
                    if len(self.tickers) == 1:  # If there is no other ticker, we quit the application
                        quit()
                    else:
                        continue # Next ticker

                priceColumn = "Adj Close"  # Price column name

            self.AssetDf["Log_Returns"] = np.log(1 + self.AssetDf[priceColumn].pct_change(1))
            self.AssetDf["Deltas"] = self.AssetDf[priceColumn].diff()

            # We check if there is enough data (daily prices) for the analysis
            if len(self.AssetDf) < self.slowMA:
                print("Not enough prices to analyze {}".format(symbol))

                if len(self.tickers) == 1:  # If there is no other ticker, we quit the application
                    quit()
                else:
                    continue  # Next ticker

            print("Working on ticker {} / {} ({})".format(x, len(self.tickers), symbol))  # Print progression

            ######################################################

            #########################################
            # 2nd step : moving average calculation #
            #########################################

            # Simple Moving Average
            if self.maType == "simple":
                moyenneAcronym = "SMA"
                shortMaCol = "{}{}".format(moyenneAcronym, self.fastMA)
                longMaCol = "{}{}".format(moyenneAcronym, self.slowMA)

                self.AssetDf[shortMaCol] = self.AssetDf[priceColumn].rolling(self.fastMA).mean() # Arithmetic mean
                self.AssetDf[longMaCol] = self.AssetDf[priceColumn].rolling(self.slowMA).mean()

            # Weighted Moving Average
            elif self.maType == "weighted":
                moyenneAcronym = "WMA"
                shortMaCol = "{}{}".format(moyenneAcronym, self.fastMA) # Columns names
                longMaCol = "{}{}".format(moyenneAcronym, self.slowMA)

                weights1 = np.arange(1, (self.fastMA) + 1) # Vector from 1 to fastMa (example : 1 to 50)
                weights2 = np.arange(1, (self.slowMA) + 1)

                self.AssetDf[shortMaCol] = self.AssetDf[priceColumn].rolling(self.fastMA).apply(
                    lambda prices: np.dot(prices, weights1) / weights1.sum(), raw=True)

                self.AssetDf[longMaCol] = self.AssetDf[priceColumn].rolling(self.slowMA).apply(
                    lambda prices: np.dot(prices, weights2) / weights2.sum(), raw=True)

            # Exponential Moving Average
            elif self.maType == "exp":
                moyenneAcronym = "EMA"
                shortMaCol = "{}{}".format(moyenneAcronym, self.fastMA)
                longMaCol = "{}{}".format(moyenneAcronym, self.slowMA)

                self.AssetDf[shortMaCol] = self.AssetDf[priceColumn].ewm(span=self.fastMA, adjust=False, min_periods=self.fastMA).mean() # ewm is a pandas exponential weighted function

                self.AssetDf[longMaCol] = self.AssetDf[priceColumn].ewm(span=self.slowMA, adjust=False, min_periods=self.slowMA).mean()

            #########################################

            ################################
            ## Variables for calculations ##
            ################################

            longPrice, shortPrice = 0, 0  # Variables that record the purchase price of a long or short position

            usedStopLoss, usedTakeProfit = 0, 0  # Number of stop-loss or take-profit activated

            holdingDays, totalDays, avgDays = 0, 0, []  # Number of days in which we hold a position and average number of days holding

            assetNb = 0 # Number of assets bought

            stopLo, dateSL, takeProf, dateTp = [], [], [], []  # Vectors that record prices and date of sales (related to stop-loss and take-profit)

            capitalEvo, self.portfolioBalanceEvolution = self.initialBalance, [] # capitalEvo is the total portfolio balance and the portfolioBalanceEvolution is a vector of his evolution

            BUY, dateBUY, SELL, dateSELL = [], [], [], []  # Moving Average vectors for plotting signals on the graph

            totalFees, fee = 0, 0 # Total fees payed and fee for each trade

            ################################

            ##################################################
            # 3rd step : Loop iterating on every trading day #
            ##################################################

            self.AssetDf = self.AssetDf.iloc[self.slowMA : ] # We keep only data after the date where both MA are calculated

            for i in range(1, len(self.AssetDf[priceColumn])):  # We have to start at 1 because otherwise we can't compare to the previous period

                totalFees += fee

                if longPrice > 0:  # If we have an open long position, we record:

                    capitalEvo += self.AssetDf["Deltas"].iloc[i] * assetNb - fee # The portfolio evolves according to the number of positions and the change in assets

                    holdingDays += 1  # One more day that we held a position
                    totalDays += 1

                    self.portfolioBalanceEvolution.append(capitalEvo)

                    fee = 0

                elif shortPrice > 0:  # If we have a short position open, we record:

                    capitalEvo += assetNb * - self.AssetDf["Deltas"].iloc[i] - fee

                    holdingDays += 1
                    totalDays += 1

                    self.portfolioBalanceEvolution.append(capitalEvo)

                    fee = 0
                else:
                    self.portfolioBalanceEvolution.append(capitalEvo)


                ##############
                # BUY SIGNAL #
                ##############

                # If in period t-1 the MA50 was weaker than the MA200 and now it is bigger, we buy
                if (self.AssetDf[shortMaCol].iloc[i - 1] < self.AssetDf[longMaCol].iloc[i - 1] and self.AssetDf[shortMaCol].iloc[i] > self.AssetDf[longMaCol].iloc[i]):

                    if self.__allSignals == True:  # If the user choosed to plot all signals
                        BUY.append(self.AssetDf[shortMaCol].iloc[i])
                        dateBUY.append(self.AssetDf.index[i])

                    ###############
                    # Sell Short  #
                    ###############

                    # We liquidate the short position if there is one and if the short is activated
                    if (self.shortLong == "both" or self.shortLong == "short") and shortPrice > 0:

                        # We record the transaction
                        transac = {"Date": self.AssetDf.index[i].strftime("%Y-%m-%d"), "Type": "Sell Short",
                                   "Price": self.AssetDf[priceColumn].iloc[i], "Ticker": symbol,
                                   "P/L": (shortPrice - self.AssetDf[priceColumn].iloc[i]),
                                   "Number of shares": assetNb}
                        transactionTable = transactionTable.append(transac, ignore_index=True)

                        avgDays.append(holdingDays)
                        assetNb, holdingDays, shortPrice = 0, 0, 0 # We reset those variables

                        BUY.append(self.AssetDf[shortMaCol].iloc[i]) # We record the moving average and date of signal
                        dateBUY.append(self.AssetDf.index[i])

                        fee = self.commission * (self.AssetDf[priceColumn].iloc[i] * assetNb) # Fees of the transaction

                    ##############
                    # Buy Long #
                    ##############

                    # We liquidate the long position if there is one and if the long is activated
                    if longPrice == 0 and (self.shortLong == "both" or self.shortLong == "long"):

                        # We check that there are enough funds to buy at least 1 asset
                        if ((self.portfolioBalanceEvolution[-1] / self.AssetDf[priceColumn].iloc[i]) < 1):
                            continue

                        longPrice = self.AssetDf[priceColumn].iloc[i]

                        assetNb = int(math.trunc(self.portfolioBalanceEvolution[-1] / longPrice)) # Number of asset we can buy

                        # We record the transaction
                        transac = {"Date": self.AssetDf.index[i].strftime("%Y-%m-%d"), "Type": "Buy Long",
                                   "Price": self.AssetDf[priceColumn].iloc[i], "Ticker": symbol,
                                   "Number of shares": assetNb}
                        transactionTable = transactionTable.append(transac, ignore_index=True)

                        BUY.append(self.AssetDf[shortMaCol].iloc[i])
                        dateBUY.append(self.AssetDf.index[i])

                        fee = self.commission * (self.AssetDf[priceColumn].iloc[i] * assetNb)


                ###############
                # SELL SIGNAL #
                ###############

                # If in period t-1 the MA50 was higher than the MA200 and now it is lower, we sell
                if (self.AssetDf[shortMaCol].iloc[i - 1] > self.AssetDf[longMaCol].iloc[i - 1] and self.AssetDf[shortMaCol].iloc[i] < self.AssetDf[longMaCol].iloc[i]):

                    if self.__allSignals == True: # If the user choosed to plot all signals
                        SELL.append(self.AssetDf[shortMaCol].iloc[i])
                        dateSELL.append(self.AssetDf.index[i])

                    ##############
                    # Sell Long #
                    ##############

                    if (self.shortLong == "both" or self.shortLong == "long") and longPrice > 0:

                        # We record the transaction
                        transac = {"Date": self.AssetDf.index[i].strftime("%Y-%m-%d"), "Type": "Sell Long",
                                   "Price": self.AssetDf[priceColumn].iloc[i], "Ticker": symbol,
                                   "P/L": (self.AssetDf[priceColumn].iloc[i] - longPrice),
                                   "Number of shares": assetNb}
                        transactionTable = transactionTable.append(transac, ignore_index=True)


                        avgDays.append(holdingDays)
                        holdingDays, longPrice, assetNb = 0, 0, 0

                        SELL.append(self.AssetDf[shortMaCol].iloc[i])
                        dateSELL.append(self.AssetDf.index[i])

                        fee = self.commission * (self.AssetDf[priceColumn].iloc[i] * assetNb)


                    ###############
                    # Buy Short #
                    ###############

                    # A short position is taken if the short is activated and if there is not already one
                    if (self.shortLong == "both" or self.shortLong == "short") and shortPrice == 0:

                        # Although shorting does not require funds, we do not take a larger position than the funds we have to avoid debt.
                        if ((self.portfolioBalanceEvolution[-1] / self.AssetDf[priceColumn].iloc[i]) < 1):
                            continue

                        shortPrice = self.AssetDf[priceColumn].iloc[i]
                        assetNb = int(math.trunc(self.portfolioBalanceEvolution[-1] / shortPrice)) # Number of asset we can buy

                        # We record the transaction
                        transac = {"Date": self.AssetDf.index[i].strftime("%Y-%m-%d"), "Type": "Buy Short",
                                   "Price": self.AssetDf[priceColumn].iloc[i], "Ticker": symbol,
                                   "Number of shares": assetNb}
                        transactionTable = transactionTable.append(transac, ignore_index=True)

                        SELL.append(self.AssetDf[shortMaCol].iloc[i])
                        dateSELL.append(self.AssetDf.index[i])

                        fee = self.commission * (self.AssetDf[priceColumn].iloc[i] * assetNb)

                ###############
                ## STOP-LOSS ##
                ###############

                # Si le stop-loss est précisé
                if self.stopLoss != None:

                    ##############
                    # Sell Long #
                    ##############

                    if longPrice > 0 and (longPrice / self.AssetDf[priceColumn].iloc[i] - 1) >= self.stopLoss:

                        # We record MA and date to plot signal on the graph
                        stopLo.append(self.AssetDf[priceColumn].iloc[i])
                        dateSL.append(self.AssetDf.index[i])

                        transac = {"Date": self.AssetDf.index[i].strftime("%Y-%m-%d"), "Type": "Stop-Loss Long",
                                   "Price": self.AssetDf[priceColumn].iloc[i], "Ticker": symbol,
                                   "P/L": (self.AssetDf[priceColumn].iloc[i] - longPrice),
                                   "Number of shares": assetNb}
                        transactionTable = transactionTable.append(transac, ignore_index=True)

                        usedStopLoss += 1
                        avgDays.append(holdingDays)
                        holdingDays, longPrice, assetNb = 0, 0, 0

                        fee = self.commission * (self.AssetDf[priceColumn].iloc[i] * assetNb)

                    ###############
                    # Sell Short #
                    ###############

                    if shortPrice > 0 and (self.AssetDf[priceColumn].iloc[i] / shortPrice - 1) >= self.stopLoss:

                        stopLo.append(self.AssetDf[priceColumn].iloc[i])
                        dateSL.append(self.AssetDf.index[i])

                        transac = {"Date": self.AssetDf.index[i].strftime("%Y-%m-%d"), "Type": "Stop-Loss Short",
                                   "Price": self.AssetDf[priceColumn].iloc[i], "Ticker": symbol,
                                   "P/L": (shortPrice - self.AssetDf[priceColumn].iloc[i]),
                                   "Number of shares": assetNb}
                        transactionTable = transactionTable.append(transac, ignore_index=True)

                        usedStopLoss += 1
                        avgDays.append(holdingDays)
                        assetNb, holdingDays, shortPrice = 0, 0, 0

                        fee = self.commission * (self.AssetDf[priceColumn].iloc[i] * assetNb)

                #################
                ## Take-Profit ##
                #################

                if self.takeProfit != None:  # Si un Take-Profit est précisé

                    ##############
                    # Sell Long #
                    ##############

                    if longPrice > 0 and (self.AssetDf[priceColumn].iloc[i] / longPrice - 1) >= self.takeProfit:

                        # We record MA and date to plot signal on the graph
                        takeProf.append(self.AssetDf[priceColumn].iloc[i])
                        dateTp.append(self.AssetDf.index[i])

                        transac = {"Date": self.AssetDf.index[i].strftime("%Y-%m-%d"), "Type": "Take-Profit Long",
                                   "Price": self.AssetDf[priceColumn].iloc[i], "Ticker": symbol,
                                   "P/L": (self.AssetDf[priceColumn].iloc[i] - longPrice)}
                        transactionTable = transactionTable.append(transac, ignore_index=True)

                        usedTakeProfit += 1
                        avgDays.append(holdingDays)
                        holdingDays, longPrice, assetNb = 0, 0, 0

                        fee = self.commission * (self.AssetDf[priceColumn].iloc[i] * assetNb)

                    ###############
                    # Sell Short #
                    ###############

                    if shortPrice > 0 and (shortPrice / self.AssetDf[priceColumn].iloc[i] - 1) >= self.takeProfit:

                        # We record MA and date to plot signal on the graph
                        takeProf.append(self.AssetDf[priceColumn].iloc[i])
                        dateTp.append(self.AssetDf.index[i])

                        transac = {"Date": self.AssetDf.index[i].strftime("%Y-%m-%d"), "Type": "Take-Profit Short",
                                   "Price": self.AssetDf[priceColumn].iloc[i], "Ticker": symbol,
                                   "P/L": (shortPrice - self.AssetDf[priceColumn].iloc[i])}
                        transactionTable = transactionTable.append(transac, ignore_index=True)

                        usedTakeProfit += 1
                        avgDays.append(holdingDays)
                        assetNb, holdingDays, shortPrice = 0, 0, 0

                        fee = self.commission * (self.AssetDf[priceColumn].iloc[i] * assetNb)

            ##########################################
            # Final calculations (Open position, ..) #
            ##########################################

            # We look to see if there is an open position (long or short)
            if longPrice > 0:
                openPosition = longPrice
                nonRealizedReturn = (self.AssetDf[priceColumn].iloc[-1] - longPrice) # Open return
                longPrice = 0  # We reset the variable for the next ticker

            elif shortPrice > 0:
                openPosition = -shortPrice
                nonRealizedReturn = (shortPrice - self.AssetDf[priceColumn].iloc[-1])
                shortPrice = 0

            else:  # There is no open position
                openPosition = 0
                nonRealizedReturn = 0

            transactionTable = pd.DataFrame(transactionTable) # We transform transactionTable in pandas dataframe
            self.transactionTable = transactionTable # We assign table to the attribute

            ################################
            # Writing in the results table #
            ################################

            resultsTable.loc[x, ["From"]] = self.AssetDf.index[0].strftime("%Y-%m-%d")
            resultsTable.loc[x, ["To"]] = self.AssetDf.index[-1].strftime("%Y-%m-%d")

            resultsTable.loc[x, ["Ticker"]] = symbol

            nbTrades = len(transactionTable.loc[transactionTable["Ticker"] == symbol, ("P/L")].dropna()) # Number of P/L made correspond to the number of trade made
            resultsTable.loc[x, ["Number of Trades"]] = nbTrades

            assetPercentPerf = (self.AssetDf[priceColumn].iloc[-1] / self.AssetDf[priceColumn].iloc[0]) - 1 # Performance of assets in %

            cryptoTickerList = pd.read_csv("tickerLists/crypto_tickers.csv", sep=";")
            cryptoTickerList = str(cryptoTickerList.iloc[:, 0])

            # Number of trading days per year (for annualization calculation)
            if symbol in cryptoTickerList:
                tradingDaysNb = 365  # Because a crypto is traded all the days of the year
            else:
                tradingDaysNb = 252  # Conventionnal number of trading days for stocks and forex

            # Risk-free rate
            if self.rf == None: # Si le taux sans risque n'est pas précisé on prend le taux du treasury bond à 3 mois
                try:
                    tYield = data.get_data_yahoo("^IRX", "2019-12-30", dt.datetime.today(), interval='d')
                    self.rf = tYield["Adj Close"].iloc[len(tYield) - 1] / 100
                except:
                    print("Risk-free rate can't be downloaded. Rate automatically set to zero.")
                    self.rf = 0


            if nbTrades > 0:  # If at least 1 trade has been made
                # Gains and losses
                gains = transactionTable[transactionTable["P/L"] > 0]
                gains = gains.loc[gains["Ticker"]==symbol, ("P/L")]
                losses = transactionTable[transactionTable["P/L"] < 0]
                losses = losses.loc[losses["Ticker"]==symbol, ("P/L")]
                wonTrade = len(gains)
                looseTrade = len(losses)

                resultsTable.loc[x, ["Winning Trades"]] = wonTrade
                resultsTable.loc[x, ["Losing Trades"]] = looseTrade


                winLossVector = transactionTable.loc[transactionTable["Ticker"] == symbol, ("P/L")].astype(float) * transactionTable.loc[transactionTable["Ticker"] == symbol, ("Number of shares")].astype(float)

                resultsTable.loc[x, ["Largest Winning Trade"]] = round(np.nanmax(winLossVector), 4)
                resultsTable.loc[x, ["Largest Losing Trade"]] = round(np.nanmin(winLossVector), 4)
                resultsTable.loc[x, ["Win Rate"]] = round(wonTrade / nbTrades, 4)

                # Expectancy calculation :
                winRate = wonTrade / nbTrades
                if len(gains) == 0:  # If there are no gains
                    resultsTable.loc[x, ["Expectancy"]] = (1 - winRate) * np.mean(losses)
                elif len(losses) == 0: # If there are no losses
                    resultsTable.loc[x, ["Expectancy"]] = (winRate) * np.mean(gains)
                else: # If there are gains and losses
                    resultsTable.loc[x, ["Expectancy"]] = ((winRate) * np.mean(gains)) + ((1 - winRate) * np.mean(losses))

                resultsTable.loc[x, ["Avg Holding Days"]] = round(np.mean(avgDays), 0)

                # - (holdingDays+1) as indexer takes the balance without open position (the realized return)
                resultsTable.loc[x, ["Total Realized Return"]] = (self.portfolioBalanceEvolution[-(holdingDays+1)] - self.initialBalance)

                # Out/Under-performance calculation :
                finalBalance = self.portfolioBalanceEvolution[-(holdingDays+1)] # Without the open position
                # The calculation depends if the asset and/or strategy performance are above zero
                stratPercentPerf = (finalBalance / self.initialBalance - 1)
                if assetPercentPerf < 0 and stratPercentPerf > 0:
                    resultsTable.loc[x, ["Out/Under-performance %"]] = abs(assetPercentPerf) + stratPercentPerf
                elif assetPercentPerf > 0 and (finalBalance / self.initialBalance - 1) < 0:
                    resultsTable.loc[x, ["Out/Under-performance %"]] = stratPercentPerf - assetPercentPerf
                elif assetPercentPerf > 0 and stratPercentPerf > 0:
                    resultsTable.loc[x, ["Out/Under-performance %"]] = stratPercentPerf - assetPercentPerf
                else: # both < 0
                    if assetPercentPerf > stratPercentPerf:
                        resultsTable.loc[x, ["Out/Under-performance %"]] = stratPercentPerf - assetPercentPerf
                    else: # if strategy return > asset return
                        resultsTable.loc[x, ["Out/Under-performance %"]] = abs(assetPercentPerf - stratPercentPerf)

                if self.portfolioBalanceEvolution[-1] < 0:  # If we went into debt because of a short position, the return is null.
                    resultsTable.loc[x, ["Strategy Annualized Return %"]] = float("NaN")
                else:
                    resultsTable.loc[x, ["Strategy Annualized Return %"]] = (finalBalance / self.initialBalance) ** (tradingDaysNb / totalDays) - 1

                # The max drawdown is calculated on the portfolio balance
                resultsTable.loc[x, ["Strategy Max Drawdown"]] = self.__maxDD(self.portfolioBalanceEvolution)[0]

                resultsTable.loc[x, ["Strategy Realized Return %"]] = self.portfolioBalanceEvolution[-(holdingDays+1)] / self.initialBalance - 1
                resultsTable.loc[x, ["Total Return"]] = round((self.portfolioBalanceEvolution[-1] - self.initialBalance), 4)

                resultsTable.loc[x, ["Market Exposure"]] = totalDays / len(self.AssetDf)

                self.portfolioBalanceEvolution = pd.Series(self.portfolioBalanceEvolution, index=self.AssetDf.index[1:])
                # We take the portfolio values after the first position is taken, because before, his balance is not moving
                portfolioReturns = np.log(1 + self.portfolioBalanceEvolution[self.portfolioBalanceEvolution.index > self.transactionTable["Date"].iloc[0]].pct_change(1))

                resultsTable.loc[x, ["Strategy Annualized Volatility"]] = np.std(portfolioReturns) * (tradingDaysNb ** 0.5)

                resultsTable.loc[x, ["Strategy Sharpe Ratio"]] = (tradingDaysNb * np.mean(portfolioReturns) - self.rf) / (np.std(portfolioReturns) * (tradingDaysNb ** 0.5))

                resultsTable.loc[x, ["99 % Strategy Daily VaR"]] = (np.mean(portfolioReturns) + st.norm.ppf(1-0.01) * np.std(portfolioReturns))


            # These stats can be computed, even if no position has been taken :
            resultsTable.loc[x, ["Final Capital"]] = self.portfolioBalanceEvolution[-1]
            if openPosition==0:
                resultsTable.loc[x, ["Open position (price)"]] = float("NaN")
                resultsTable.loc[x, ["Open Trade P/L"]] = float("NaN")
            else:
                resultsTable.loc[x, ["Open position (price)"]] = openPosition
                resultsTable.loc[x, ["Open Trade P/L"]] = nonRealizedReturn * assetNb


            if symbol in list(forexFREDlist):  # The volume is not provided by FRED for forex
                resultsTable.loc[x, ["Asset Daily Avg Volume"]] = float("NaN")
            else:
                resultsTable.loc[x, ["Asset Daily Avg Volume"]] = np.mean(self.AssetDf["Volume"])

            assetCumulReturns = np.exp(self.AssetDf["Log_Returns"].cumsum())  # Cumulative Sum of Log Asset Returns
            buyAndHoldcapital = self.initialBalance * assetCumulReturns  # Evolution of a buy and hold investment

            resultsTable.loc[x, ["Asset Return %"]] = assetPercentPerf

            resultsTable.loc[x, ["Buy & Hold Return"]] = assetPercentPerf * self.initialBalance

            resultsTable.loc[x, ["Asset Max Drawdown"]] = self.__maxDD(self.AssetDf[priceColumn])[0]
            resultsTable.loc[x, ["99 % Asset Daily VaR"]] = (np.mean(self.AssetDf["Log_Returns"]) + st.norm.ppf(1 - 0.01) * np.std(self.AssetDf["Log_Returns"]))
            resultsTable.loc[x, ["Used Stop-Loss"]] = usedStopLoss

            resultsTable.loc[x, ["Used Take-Profit"]] = usedTakeProfit

            resultsTable.loc[x, ["Initial Capital"]] = self.initialBalance

            resultsTable.loc[x, ["Total fees payed"]] = totalFees

            resultsTable.loc[x, ["Asset Annualized Return %"]] =  (assetPercentPerf + 1) ** (tradingDaysNb / len(self.AssetDf)) - 1
            resultsTable.loc[x, ["Asset Annualized Volatility"]] = np.std(self.AssetDf["Log_Returns"]) * (tradingDaysNb ** 0.5)

            resultsTable.loc[x, ["Asset Sharpe Ratio"]] = (((assetPercentPerf + 1) ** (tradingDaysNb / len(self.AssetDf)) - 1) - self.rf) / (np.std(self.AssetDf["Log_Returns"]) * (tradingDaysNb ** 0.5))

            self.resultsTable = resultsTable


            ################
            # Graph coding #
            ################

            if self.__makeplot == True:
                fig, (ax1, ax2, ax3) = plt.subplots(3, figsize=(16, 9), gridspec_kw={'height_ratios': [3, 1.2, 1.2]})
                fig.subplots_adjust(hspace=0.3)
                fig.subplots_adjust(top=0.92)
                ax1.grid(True)
                ax1.set_ylabel("USD")
                ax1.set_facecolor('#1d1d1f')
                ax2.set_ylabel("USD")
                ax2.set_facecolor('#1d1d1f')
                ax2.grid(True)
                ax2.set_title("Portfolio vs Asset", fontsize=11)
                ax2.ticklabel_format(style='plain', axis='y')

                ax3.grid(True)
                ax3.set_facecolor('#1d1d1f')
                ax3.set_title("Drawdowns", fontsize=11)

                ax3.yaxis.set_major_formatter(ticker.PercentFormatter(xmax=1))

                if self.shortLong == "long":
                    slTitre = "(Long only)"
                    buySignalLabel = "BUY LONG"
                    sellSignalLabel = "SELL LONG"
                elif self.shortLong == "both":
                    slTitre = "(Long & Short)"
                    buySignalLabel = "BUY LONG / SELL SHORT"
                    sellSignalLabel = "SELL LONG / BUY SHORT"
                else:
                    slTitre = "(Short only)"
                    buySignalLabel = "SELL SHORT"
                    sellSignalLabel = "BUY SHORT"

                if moyenneAcronym == "EMA":
                    fig.suptitle("Exponential Moving Average crossover strategy for {} {}".format(symbol, slTitre), size=20)
                elif moyenneAcronym == "SMA":
                    fig.suptitle("Simple Moving Average crossover strategy for {} {}".format(symbol, slTitre), size=20)
                else:
                    fig.suptitle("Weighted Moving Average crossover strategy for {} {}".format(symbol, slTitre), size=20)

                ax1.plot(self.AssetDf.index, self.AssetDf[priceColumn], label="AssetPrice", linewidth=0.8)

                ax1.plot(self.AssetDf.index, self.AssetDf[shortMaCol], label=shortMaCol, linewidth=0.8)
                ax1.plot(self.AssetDf.index, self.AssetDf[longMaCol], label=longMaCol, linewidth=0.8, color='#0d7a21')

                ax1.plot(dateBUY, BUY, 'o', markersize=4, color='#41e86e', label=buySignalLabel)
                ax1.plot(dateSELL, SELL, '^', markersize=4, color='#ffe608', label=sellSignalLabel)

                _, stratDD = self.__maxDD(self.portfolioBalanceEvolution)
                _, assetDD = self.__maxDD(self.AssetDf[priceColumn])

                ax3.fill_between(self.AssetDf.index[1:], 0, stratDD, zorder=1, label="Strategy Drawdown")
                ax3.fill_between(self.AssetDf.index, 0, assetDD, color="red", zorder=3, alpha=0.5, label="Asset Drawdown")

                ax2.yaxis.set_major_formatter(mpl.ticker.StrMethodFormatter('{x:,.0f}'))


                # If there is an open position, we record the date of the order (to plot it on graph)
                if openPosition != 0:
                    lastDate = transactionTable["Date"].iloc[-1]

                    # Plot the portfolio evolution, without open position
                    realisedReturn = (self.AssetDf.index <= lastDate)  # yields prior to last order
                    dateRdtRealise = self.AssetDf.index[realisedReturn]  # dates prior to the last order
                    ax2.plot(dateRdtRealise[1:], np.array(self.portfolioBalanceEvolution)[realisedReturn[1:]], label="Portfolio equity", linewidth=0.8, color='#0d7a21')

                    # Plot the open position evolution
                    openReturn = (self.AssetDf.index >= lastDate)  # post-last order returns
                    dateOpenReturn = self.AssetDf.index[openReturn]  # post-last order dates
                    ax2.plot(dateOpenReturn, np.array(self.portfolioBalanceEvolution)[openReturn[1:]], label="Open position", linewidth=0.8, color="red")

                else:
                    ax2.plot(self.AssetDf.index[1:], self.portfolioBalanceEvolution, label="Portfolio equity", linewidth=0.8, color='#0d7a21')

                ax2.plot(self.AssetDf.index, buyAndHoldcapital, label="Buy & Hold Scenario", linewidth=0.8)

                if len(dateSL) > 0: # If stop-loss have been used
                    ax1.plot(dateSL, stopLo, "_", markersize=7, color='r', label="Stop-Loss Activated")
                if len(dateTp) > 0: # If take-profit have been used
                    ax1.plot(dateTp, takeProf, "_", markersize=7, color='#d000ff', label="Take-Profit Activated")

                leg = ax1.legend(loc=2, prop={'size': 9}, markerscale=1.5)
                for line in leg.get_lines():
                    line.set_linewidth(2)

                leg = ax2.legend(loc=2, prop={'size': 9})
                for line in leg.get_lines():
                    line.set_linewidth(2)

                ax3.legend(loc=2, prop={'size': 9})
            x += 1

        print("Done !")

    # Function to calculate the max drawdown
    def __maxDD(self, vector):
        vector = pd.Series(vector)  # We transform the vector into a pandas list and apply the pandas "cummax" function to it.
        rolledMax = vector.cummax()  # It calculates the max, each day, according to the last max
        dailyDD = vector / rolledMax - 1.0  # So if we divide each price by the max of the period, we get the change from the max of the period.

        return np.nanmin(dailyDD), dailyDD # Max drawdown and vector of all drawdowns (for the graph)

    def seasonalityTable(self, ticker=None):

        """

        Return a pandas pivot table with the average profits & losses of each years / months of the strategy.
        It gives a good overview of the return seasonality.


        Parameter
        ---------

        ticker (str) -- You can choose to specify a ticker if there is multiple in the class


        """

        if ticker != None:
            seasonTable = self.transactionTable[self.transactionTable["Ticker"] == ticker] # L'utilisateur peut préciser un ticker si l'analyse a été faite sur plusieurs
        else:
            seasonTable = self.transactionTable  # On crée une copie de la table des transactions

        seasonTable['Date'] = pd.to_datetime(seasonTable['Date'], errors='coerce')
        seasonTable["Year"] = seasonTable['Date'].dt.year
        seasonTable["Month"] = seasonTable['Date'].dt.strftime('%b')

        seasonTable = pd.pivot_table(seasonTable, index=seasonTable["Month"], columns=seasonTable['Year'], values='P/L', aggfunc=np.mean, fill_value=0)

        seasonTable = seasonTable.reindex(['Jan', 'Feb', 'Mar', "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct",
                                           "Nov", "Dec"])

        return seasonTable

    def optimize(self, indicator, fastMaRange=[], slowMaRange=[], type="max"):

        """

        Finds the best moving average allocation to optimize an indicator (ex : maximize Sharpe-ratio)

        Parameter
        ---------

        indicator (str) -- You can choose to specify a ticker

        Key-worded :

        fastMaRange (list) -- The range for the fast moving average (example : [0 , 20])

        slowMaRange (list) -- The range for the slow moving average (example : [30 , 50])

        type (str) -- "min" for minimization, and "max" for maximization


        Return
        ------

        A pandas dataframe with all the combinations tried

        """

        results = pd.DataFrame(columns=["fastMA", "slowMA", str(indicator)])

        totalPossibilies = (fastMaRange[1] - fastMaRange[0] + 1)*(slowMaRange[1] - slowMaRange[0] + 1)
        if totalPossibilies > 10:
            answer = input("{} combinaisons possibles found, it may take some times. Continue ? y/n \n".format(totalPossibilies))
            if answer == "n":
                quit()
            elif answer == "y":
                pass
            else:
                print("I didn't understand")
                quit()

        i = 0

        for fastDays in range(fastMaRange[0], fastMaRange[1] + 1):
            for slowDays in range(slowMaRange[0], slowMaRange[1] + 1):
                print("\n", "Trying combinaison {}/{}".format(i, totalPossibilies))

                test = movingAverageCrossover(self.tickers, fastDays, slowDays, self.beginDate, self.endDate, shortLong="both", capital=1_000_000, maType=self.maType,
                                              stopLoss=self.stopLoss, takeProfit=self.takeProfit, rf=self.rf, signals=self.__allSignals,commission=self.commission)
                test.analyse()

                testData = {"fastMA": fastDays, "slowMA": slowDays,
                           str(indicator): np.mean(test.resultsTable[str(indicator)])}

                results = results.append(testData, ignore_index=True)

                i += 1

        print(results)

        print("\n Best combinaison found :\n")
        if type=="max":
            print(results[results[str(indicator)] == max(results[str(indicator)])])
        elif type=="min":
            print(results[results[str(indicator)] == min(results[str(indicator)])])
        else:
            raise ValueError("Wrong optimisation type")

        return results
