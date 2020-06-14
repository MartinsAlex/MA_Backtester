import pandas as pd
import numpy as np
from pandas_datareader import data, wb
import datetime as dt
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import matplotlib.dates as mdates
from pandas.plotting import register_matplotlib_converters
from pandas_datareader._utils import RemoteDataError
import warnings
import math
import matplotlib.ticker as ticker

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
            - "Over/Under-performance %" : Underperform if this stats is < 0

        transactionTable :
            Pandas Dataframe containing all the transactions that would have been made by the strategy.


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

        resultsTable = pd.DataFrame(
            columns=["From", "To", "Ticker", "Number of Trades", "Winning Trades", "Losing Trades",
                     "Largest Winning Trade", "Largest Losing Trade", "Win Rate", "Expectancy", "Total Realized Return", "Total Return",
                     "Buy & Hold Return", "Asset Return %", "Strategy Realized Return %", "Over/Under-performance %", 'Asset Annualized Return %', 'Strategy Annualized Return %',
                     "Open position (price)", "Open Trade P/L",  "Asset Annualized Volatility", "Strategy Annualized Volatility", "Asset Sharpe Ratio", "Strategy Sharpe Ratio",
                     "Asset Max Drawdown", "Strategy Max Drawdown", "Market Exposure",  "Asset Daily Avg Volume", "Avg Holding Days", "Initial Capital",
                     "Final Capital", "Used Stop-Loss", "Used Take-Profit", "Total fees payed"])  # Result table with column names # "Correlation with Hold & Buy",

        # Table of transactions
        transactionTable = pd.DataFrame(columns=["Date", "Type", "Price", "Ticker", "P/L", "Number of shares"])

        forexFREDlist = pd.read_csv("tickerLists/forex_tickers.csv", sep=";")
        forexFREDlist = forexFREDlist.iloc[:, 0]


        # Liste des monnaies cotées indirectement
        forexIndirect = ["DEXBZUS", "DEXCAUS", "DEXCHUS", "DEXDNUS", "DEXHKUS", "DEXINUS", "DEXJPUS", "DEXMAUS",
                         "DEXMXUS", "DEXTAUS", "DEXNOUS", "DEXSIUS", "DEXSFUS", "DEXKOUS", "DEXSLUS", "DEXSDUS",
                         "DEXSZUS", "DEXTHUS"]

        x = 1  # Sers à indiquer la ligne pour l'ajout dans la table des résultats

        for symbol in self.tickers:  # On commence la boucle qui va itérer sur chaque symbol dans la liste
            print("Working on ticker {} / {} ({})".format(x, len(self.tickers), symbol))  # Sert à indiquer la progression

            ######################################################
            # 1st step : identify the source and download prices #
            ######################################################

            symbol = str.upper(symbol)

            if symbol in forexFREDlist:  # Forex
                self.AssetDf = data.get_data_fred(symbol, self.beginDate, self.endDate)  # On effectue la requête avec la fonction de pandas_datareader
                self.AssetDf = self.AssetDf.dropna()  # On élimine toutes les lignes qui ont des NaN
                priceColumn = symbol  # On fixe le nom de la colonne contenant les prix car il varie selon la source

                if symbol in forexIndirect:  # Si la monnaie est dans la liste des indirectes, il faut inverser son cours pour refléter sa valeur en USD
                    self.AssetDf[symbol] = self.AssetDf[symbol] ** (-1)

            else: # Yahoo Data

                try:
                    self.AssetDf = data.get_data_yahoo(symbol, self.beginDate, self.endDate, interval='d')
                except (RemoteDataError, KeyError, OverflowError) as exp:  # Si il y a erreur on regarde si le problème vient de la date
                    try:
                        self.__AssetDfTest = data.get_data_yahoo(symbol, "1980-01-01", interval='d')  # On télécharge la self.AssetDf entièrement
                        firstDate = self.__AssetDfTest.index[0]  # On prend la date minimale
                        self.AssetDf = data.get_data_yahoo(symbol, firstDate, "2017-08-31", interval='d')  # On re-effectue la requête avec cette date

                    except:  # Sinon le problème vient du fait que le symbol ne marche pas
                        print("Ticker {} not working".format(symbol))
                        resultsTable.loc[x, ["Ticker"]] = symbol
                        x += 1

                        if len(self.tickers) == 1:  # Si il n'y pas d'autres actif à analyser on quitte l'application
                            quit()
                        else:
                            continue


                self.AssetDf = self.AssetDf.dropna()  # On élimine toutes les lignes qui ont des NaN
                priceColumn = "Adj Close"  # On fixe le nom de la colonne contenant les prix car il varie selon la source

            self.AssetDf["Log_Returns"] = np.log(1 + self.AssetDf[priceColumn].pct_change(1))
            self.AssetDf["Deltas"] = self.AssetDf[priceColumn].diff()

            # We check if there is enough data (daily price) for the analysis
            if len(self.AssetDf) < self.slowMA:
                print("Not enough data to analyze {}".format(symbol))

                if len(self.tickers) == 1:  # Si il n'y pas d'autres actif à analyser on quitte l'application
                    quit()
                else:
                    #x += 1
                    continue  # Next stock


            ######################################################

            #########################################
            # 2nd step : moving average calculation #
            #########################################

            # Simple Moving Average
            if self.maType == "simple":
                moyenneAcronym = "SMA"
                shortMaCol = "{}{}".format(moyenneAcronym, self.fastMA)
                longMaCol = "{}{}".format(moyenneAcronym, self.slowMA)

                self.AssetDf[shortMaCol] = self.AssetDf[priceColumn].rolling(self.fastMA).mean()
                self.AssetDf[longMaCol] = self.AssetDf[priceColumn].rolling(self.slowMA).mean()

            # Weighted Moving Average
            elif self.maType == "weighted":
                moyenneAcronym = "WMA"
                shortMaCol = "{}{}".format(moyenneAcronym, self.fastMA)
                longMaCol = "{}{}".format(moyenneAcronym, self.slowMA)

                weights1 = np.arange(1, (self.fastMA) + 1)
                weights2 = np.arange(1, (self.slowMA) + 1)

                self.AssetDf[moyenneAcronym + str(self.fastMA)] = self.AssetDf[priceColumn].rolling(self.fastMA).apply(
                    lambda prices: np.dot(prices, weights1) / weights1.sum(), raw=True)  # On multiplie chaque x dernier prix prix par le poids qui lui est attribué,
                # puis on divise par la somme des poids pour obtenir la moyenne pondérée

                self.AssetDf[moyenneAcronym + str(self.slowMA)] = self.AssetDf[priceColumn].rolling(self.slowMA).apply(
                    lambda prices: np.dot(prices, weights2) / weights2.sum(), raw=True)

            # Exponential Moving Average
            elif self.maType == "exp":
                moyenneAcronym = "EMA"
                shortMaCol = "{}{}".format(moyenneAcronym, self.fastMA)
                longMaCol = "{}{}".format(moyenneAcronym, self.slowMA)

                self.AssetDf[shortMaCol] = self.AssetDf[priceColumn].ewm(span=self.fastMA, adjust=False, min_periods=self.fastMA).mean()

                self.AssetDf[longMaCol] = self.AssetDf[priceColumn].ewm(span=self.slowMA, adjust=False, min_periods=self.slowMA).mean()

            #########################################

            ################################
            ## Variables for calculations ##
            ################################

            longPrice, shortPrice = 0, 0  # Variables qui enregistrent le prix d'achat d'une position long ou short

            usedStopLoss, usedTakeProfit = 0, 0  # Nb de stops activés

            holdingDays, totalDays, avgDays = 0, 0, []  # Nb de jours durant lequel on détient une position et nb de jours moyen

            assetNb = 0

            stopLo, dateSL, takeProf, dateTp = [], [], [], []  # Vecteurs qui enregistrent les prix et date de ventes (liées aux stop-loss et take-profit)

            capitalEvo, self.portfolioBalanceEvolution = self.initialBalance, [] # Pour le graphique qui compare le portefeuille à l'actif

            BUY, dateBUY, SELL, dateSELL = [], [], [], []  # Vecteurs prix d'achats, ventes et dates

            totalFees, fee = 0, 0 # Total fees payed and fee for each trade

            ################################

            ##################################################
            # 3rd step : Loop iterating on every trading day #
            ##################################################

            for i in range(1, len(self.AssetDf[priceColumn])):  # On doit commencer à 1 car sinon on peut pas comparer à la période précédente

                totalFees += fee

                if longPrice > 0:  # Si on a une position long ouverte, on enregistre :

                    capitalEvo += self.AssetDf["Deltas"].iloc[i] * assetNb - fee # Le portefeuille évolue en fonction du nombre de positions et de la variation de l'actif

                    holdingDays += 1  # Un jour de plus durant lequel on a détenu une position
                    totalDays += 1

                    self.portfolioBalanceEvolution.append(capitalEvo)

                    fee = 0

                elif shortPrice > 0:  # Si on a une position short ouverte, on enregistre :

                    capitalEvo += assetNb * - self.AssetDf["Deltas"].iloc[i] - fee

                    holdingDays += 1  # Un jour de plus durant lequel on a détenu une position
                    totalDays += 1

                    self.portfolioBalanceEvolution.append(capitalEvo)

                    fee = 0
                else:
                    self.portfolioBalanceEvolution.append(capitalEvo)


                ##############
                # BUY SIGNAL #
                ##############

                # Si en période t-1 la MA50 était plus faible que la MA200 et que maintenant elle est plus grande, on achète car cela veut dire qu'elle a dépassé par le bas
                if (self.AssetDf[shortMaCol].iloc[i - 1] < self.AssetDf[longMaCol].iloc[i - 1] and self.AssetDf[shortMaCol].iloc[i] > self.AssetDf[longMaCol].iloc[i]):

                    if self.__allSignals == True:  # l'utilisateur peut choisir d'afficher tout les signals même si aucun achat n'est réellement effectué
                        BUY.append(self.AssetDf[shortMaCol].iloc[i])
                        dateBUY.append(self.AssetDf.index[i])

                    ###############
                    # Sell Short  #
                    ###############

                    # Et on liquide la position short si il y en a une et que le short est activé
                    if (self.shortLong == "both" or self.shortLong == "short") and shortPrice > 0:

                        # On enregistre la transaction
                        transac = {"Date": self.AssetDf.index[i].strftime("%Y-%m-%d"), "Type": "Sell Short",
                                   "Price": self.AssetDf[priceColumn].iloc[i], "Ticker": symbol,
                                   "P/L": (shortPrice - self.AssetDf[priceColumn].iloc[i]),
                                   "Number of shares": assetNb}

                        transactionTable = transactionTable.append(transac, ignore_index=True)

                        avgDays.append(holdingDays)
                        assetNb, holdingDays, shortPrice = 0, 0, 0

                        BUY.append(self.AssetDf[shortMaCol].iloc[i])
                        dateBUY.append(self.AssetDf.index[i])

                        fee = self.commission * (self.AssetDf[priceColumn].iloc[i] * assetNb)

                    ##############
                    # Buy Long #
                    ##############

                    # On achète que si aucune position est déjà détenue, le long est activé
                    if longPrice == 0 and (self.shortLong == "both" or self.shortLong == "long"):
                        # On vérifie qu'il y ait assez de fonds pour acheté au moins 1 actif
                        if ((self.portfolioBalanceEvolution[-1] / self.AssetDf[priceColumn].iloc[i]) < 1):
                            # print("Fonds insuffisant")
                            continue

                        # On achète que si le long est activé (ou le short + long)
                        longPrice = self.AssetDf[priceColumn].iloc[i]

                        assetNb = int(math.trunc(self.portfolioBalanceEvolution[-1] / longPrice)) # Number of asset we can buy

                        # On enregistre la transaction
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

                # Si en période t-1 la MA50 était plus élevée que la MA200 et que mnt elle est plus faible, on vend car cela veut dire qu'elle est repassé en dessous (par le haut)
                if (self.AssetDf[shortMaCol].iloc[i - 1] > self.AssetDf[longMaCol].iloc[i - 1] and self.AssetDf[shortMaCol].iloc[i] < self.AssetDf[longMaCol].iloc[i]):

                    if self.__allSignals == True:  # l'utilisateur peut choisir d'afficher tout les signals même si aucun achat n'est réellement effectué
                        SELL.append(self.AssetDf[shortMaCol].iloc[i])
                        dateSELL.append(self.AssetDf.index[i])

                    ##############
                    # Sell Long #
                    ##############

                    # Et que mnt elle est plus faible, on vend car cela veut dire qu'elle est repassé en dessous (par le haut)
                    # On enregistre la date et le prix du signal de vente

                    if (self.shortLong == "both" or self.shortLong == "long") and longPrice > 0:  # Cette partie ne concerne que le long
                        # Si il y a une position long ouverte, on la vend

                        # On enregistre la transaction
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

                    # On prend une position short si le short est activé (ou le short + long) et qu'il n'y en a pas déjà une
                    if (self.shortLong == "both" or self.shortLong == "short") and shortPrice == 0:

                        # Malgrès que le short ne nécessite pas de fonds on ne prend pas de position supérieur aux fonds qu'on possède pour éviter le sur-endettemment
                        if ((self.portfolioBalanceEvolution[-1] / self.AssetDf[priceColumn].iloc[i]) < 1):
                            # print("Fonds insuffisant")
                            continue

                        shortPrice = self.AssetDf[priceColumn].iloc[i]
                        assetNb = int(math.trunc(self.portfolioBalanceEvolution[-1] / shortPrice)) # Number of asset we can buy

                        # On enregistre la transaction
                        transac = {"Date": self.AssetDf.index[i].strftime("%Y-%m-%d"), "Type": "Buy Short",
                                   "Price": self.AssetDf[priceColumn].iloc[i], "Ticker": symbol,
                                   "Number of shares": assetNb}

                        transactionTable = transactionTable.append(transac, ignore_index=True)

                        SELL.append(self.AssetDf[shortMaCol].iloc[i])
                        dateSELL.append(self.AssetDf.index[i])

                        fee = self.commission * (self.AssetDf[priceColumn].iloc[i] * assetNb)

                ###############
                ## STOP-LOSS ##  =  Vente à partir d'une certaine perte
                ###############

                # Si le stop-loss est précisé
                if self.stopLoss != None:

                    ##############
                    # Sell Long #
                    ##############

                    if longPrice > 0 and (longPrice / self.AssetDf[priceColumn].iloc[i] - 1) >= self.stopLoss:

                        # on enregistre le prix et la date de la vente
                        stopLo.append(self.AssetDf[priceColumn].iloc[i])
                        dateSL.append(self.AssetDf.index[i])

                        # On enregistre la transaction
                        transac = {"Date": self.AssetDf.index[i].strftime("%Y-%m-%d"), "Type": "Stop-Loss Long",
                                   "Price": self.AssetDf[priceColumn].iloc[i], "Ticker": symbol,
                                   "P/L": (self.AssetDf[priceColumn].iloc[i] - longPrice),
                                   "Number of shares": assetNb}
                        transactionTable = transactionTable.append(transac, ignore_index=True)


                        usedStopLoss += 1
                        avgDays.append(holdingDays)
                        holdingDays, longPrice, assetNb = 0, 0, 0

                    ###############
                    # Sell Short #
                    ###############

                    if shortPrice > 0 and (self.AssetDf[priceColumn].iloc[i] / shortPrice - 1) >= self.stopLoss:


                        # on enregistre le prix et la date de la vente
                        stopLo.append(self.AssetDf[priceColumn].iloc[i])
                        dateSL.append(self.AssetDf.index[i])

                        # On enregistre la transaction
                        transac = {"Date": self.AssetDf.index[i].strftime("%Y-%m-%d"), "Type": "Stop-Loss Short",
                                   "Price": self.AssetDf[priceColumn].iloc[i], "Ticker": symbol,
                                   "P/L": (shortPrice - self.AssetDf[priceColumn].iloc[i]),
                                   "Number of shares": assetNb}

                        transactionTable = transactionTable.append(transac, ignore_index=True)


                        usedStopLoss += 1
                        avgDays.append(holdingDays)
                        assetNb, holdingDays, shortPrice = 0, 0, 0

                #################
                ## Take-Profit ##
                #################

                if self.takeProfit != None:  # Si un Take-Profit est précisé

                    ##############
                    # Sell Long #
                    ##############

                    if longPrice > 0 and (self.AssetDf[priceColumn].iloc[i] / longPrice - 1) >= self.takeProfit:

                        # on enregistre le prix et la date de la vente
                        takeProf.append(self.AssetDf[priceColumn].iloc[i])
                        dateTp.append(self.AssetDf.index[i])

                        # On enregistre la transaction
                        transac = {"Date": self.AssetDf.index[i].strftime("%Y-%m-%d"), "Type": "Take-Profit Long",
                                   "Price": self.AssetDf[priceColumn].iloc[i], "Ticker": symbol,
                                   "P/L": (self.AssetDf[priceColumn].iloc[i] - longPrice)}

                        transactionTable = transactionTable.append(transac, ignore_index=True)

                        usedTakeProfit += 1
                        avgDays.append(holdingDays)
                        holdingDays, longPrice, assetNb = 0, 0, 0

                    ###############
                    # Sell Short #
                    ###############

                    if shortPrice > 0 and (shortPrice / self.AssetDf[priceColumn].iloc[i] - 1) >= self.takeProfit:

                        # on enregistre le prix et la date de la vente
                        takeProf.append(self.AssetDf[priceColumn].iloc[i])
                        dateTp.append(self.AssetDf.index[i])


                        # On enregistre la transaction
                        transac = {"Date": self.AssetDf.index[i].strftime("%Y-%m-%d"), "Type": "Take-Profit Short",
                                   "Price": self.AssetDf[priceColumn].iloc[i], "Ticker": symbol,
                                   "P/L": (shortPrice - self.AssetDf[priceColumn].iloc[i])}
                        transactionTable = transactionTable.append(transac, ignore_index=True)

                        usedTakeProfit += 1
                        avgDays.append(holdingDays)
                        assetNb, holdingDays, shortPrice = 0, 0, 0


            #######################################
            # Calculs finaux (dont open position) #
            #######################################

            # On regarde si il reste une position ouverte (long ou short)
            if longPrice > 0:
                openPosition = longPrice
                nonRealizedReturn = (self.AssetDf[priceColumn].iloc[-1] - longPrice)
                longPrice = 0  # On remet la variable à zéro pour la prochaine boucle

            elif shortPrice > 0:
                openPosition = -shortPrice
                nonRealizedReturn = (shortPrice - self.AssetDf[priceColumn].iloc[-1])
                shortPrice = 0

            else:  # Il n'y pas de position ouverte
                openPosition = 0
                nonRealizedReturn = 0

            transactionTable = pd.DataFrame(transactionTable)
            self.transactionTable = transactionTable


            #####################################################
            # Début de l'écriture dans le tableau des résultats #
            #####################################################

            resultsTable.loc[x, ["From"]] = self.AssetDf.index[0].strftime("%Y-%m-%d")
            resultsTable.loc[x, ["To"]] = self.AssetDf.index[-1].strftime("%Y-%m-%d")

            resultsTable.loc[x, ["Ticker"]] = symbol

            transactionTable.loc[transactionTable["Ticker"] == symbol, ("P/L")]

            nbTrades = len(transactionTable.loc[transactionTable["Ticker"] == symbol, ("P/L")].dropna())
            resultsTable.loc[x, ["Number of Trades"]] = nbTrades

            assetPercentPerf = (self.AssetDf[priceColumn].iloc[-1] / self.AssetDf[priceColumn].iloc[0]) - 1

            cryptoTickerList = pd.read_csv("tickerLists/crypto_tickers.csv", sep=";")
            cryptoTickerList = str(cryptoTickerList.iloc[:, 0])

            # Number of trading days per year
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
                    print("Risk-free rate can't be downloaded. Automatically set to zero.")
                    self.rf = 0


            if nbTrades > 0:  # If at least 1 trade has been made
                # Gains and losses
                gains = transactionTable[transactionTable["P/L"] > 0]
                gains = gains["P/L"]
                losses = transactionTable[transactionTable["P/L"] < 0]
                losses = losses["P/L"]
                wonTrade = len(gains)
                looseTrade = len(losses)


                resultsTable.loc[x, ["Winning Trades"]] = wonTrade
                resultsTable.loc[x, ["Losing Trades"]] = looseTrade

                winLossVector = transactionTable.loc[transactionTable["Ticker"] == symbol, ("P/L")].astype(float) * transactionTable.loc[transactionTable["Ticker"] == symbol, ("Number of shares")].astype(float)
                #print(winLossVector)
                resultsTable.loc[x, ["Largest Winning Trade"]] = round(np.nanmax(winLossVector), 4)
                resultsTable.loc[x, ["Largest Losing Trade"]] = round(np.nanmin(winLossVector), 4)
                resultsTable.loc[x, ["Win Rate"]] = round(wonTrade / nbTrades, 4)

                # Expectancy calculation
                winRate = wonTrade / nbTrades

                if len(gains) == 0:  # Si il n'y aucun gains (sers à éviter une erreur de numpy quand il y a moyenne d'un vecteur vide)
                    resultsTable.loc[x, ["Expectancy"]] = (1 - winRate) * np.mean(losses)  # = Espérance
                elif len(losses) == 0:
                    resultsTable.loc[x, ["Expectancy"]] = (winRate) * np.mean(gains)
                else:
                    resultsTable.loc[x, ["Expectancy"]] = ((winRate) * np.mean(gains)) + ((1 - winRate) * np.mean(losses))  # = Espérance

                resultsTable.loc[x, ["Avg Holding Days"]] = round(np.mean(avgDays), 0)

                resultsTable.loc[x, ["Total Realized Return"]] = (self.portfolioBalanceEvolution[-(holdingDays+1)] - self.initialBalance)

                if assetPercentPerf < 0 and (self.portfolioBalanceEvolution[-(holdingDays+1)] / self.initialBalance - 1) > 0:
                    resultsTable.loc[x, ["Over/Under-performance %"]] = abs(assetPercentPerf) + (self.portfolioBalanceEvolution[-(holdingDays+1)] / self.initialBalance - 1)
                elif assetPercentPerf > 0 and (self.portfolioBalanceEvolution[-(holdingDays+1)] / self.initialBalance - 1) < 0:
                    resultsTable.loc[x, ["Over/Under-performance %"]] = (self.portfolioBalanceEvolution[-(holdingDays+1)] / self.initialBalance - 1) - assetPercentPerf
                elif assetPercentPerf > 0 and (self.portfolioBalanceEvolution[-(holdingDays+1)] / self.initialBalance - 1) > 0:
                    resultsTable.loc[x, ["Over/Under-performance %"]] = (self.portfolioBalanceEvolution[-(holdingDays+1)] / self.initialBalance - 1) - assetPercentPerf
                else: # both < 0
                    if assetPercentPerf > (self.portfolioBalanceEvolution[-(holdingDays+1)] / self.initialBalance - 1):
                        resultsTable.loc[x, ["Over/Under-performance %"]] = assetPercentPerf - (self.portfolioBalanceEvolution[-(holdingDays+1)] / self.initialBalance - 1)
                    else:
                        resultsTable.loc[x, ["Over/Under-performance %"]] = (self.portfolioBalanceEvolution[-(holdingDays+1)] / self.initialBalance - 1) - assetPercentPerf


                if self.portfolioBalanceEvolution[-1] < 1:  # Si on s'est carrément endetté avec une position short, le rdt est nulle
                    resultsTable.loc[x, ["Strategy Annualized Return %"]] = float("NaN")
                else:
                    resultsTable.loc[x, ["Strategy Annualized Return %"]] = (self.portfolioBalanceEvolution[-(holdingDays + 1)] / self.initialBalance) ** (tradingDaysNb / totalDays) - 1

                stratMaxDD, _ = self.__maxDD(self.portfolioBalanceEvolution)
                resultsTable.loc[x, ["Strategy Max Drawdown"]] = stratMaxDD

                resultsTable.loc[x, ["Strategy Realized Return %"]] = self.portfolioBalanceEvolution[-(holdingDays+1)] / self.initialBalance - 1
                resultsTable.loc[x, ["Total Return"]] = round((self.portfolioBalanceEvolution[-1] - self.initialBalance), 4)

                resultsTable.loc[x, ["Market Exposure"]] = totalDays / len(self.AssetDf)


                self.portfolioBalanceEvolution = pd.Series(self.portfolioBalanceEvolution, index=self.AssetDf.index[1:])
                # We take the portfolio values after the first position is taken, because before, the value is not moving
                portfolioReturns = np.log(1 + self.portfolioBalanceEvolution[self.portfolioBalanceEvolution.index > self.transactionTable["Date"].iloc[0]].pct_change(1))

                resultsTable.loc[x, ["Strategy Annualized Volatility"]] = np.std(portfolioReturns) * (tradingDaysNb ** 0.5)

                resultsTable.loc[x, ["Strategy Sharpe Ratio"]] = (tradingDaysNb * np.mean(portfolioReturns) - self.rf) / (np.std(portfolioReturns) * (tradingDaysNb ** 0.5))  # Rdt annualisé

                #try:
                #    resultsTable.loc[x, ["Correlation with Hold & Buy"]] = np.corrcoef(self.AssetDf.loc[self.AssetDf.index > self.transactionTable["Date"].iloc[0], "Log_Returns"].iloc[1:],
                #                                                                       portfolioReturns.dropna())[0,1]
                #except:
                #    resultsTable.loc[x, ["Correlation with Hold & Buy"]] = float("NaN")


            resultsTable.loc[x, ["Final Capital"]] = self.portfolioBalanceEvolution[-1]
            if openPosition==0:
                resultsTable.loc[x, ["Open position (price)"]] = float("NaN")
                resultsTable.loc[x, ["Open Trade P/L"]] = float("NaN")
            else:
                resultsTable.loc[x, ["Open position (price)"]] = openPosition
                resultsTable.loc[x, ["Open Trade P/L"]] = nonRealizedReturn * assetNb


            if symbol in forexFREDlist:  # Le volume n'est pas fourni par FRED pour le forex
                resultsTable.loc[x, ["Asset Daily Avg Volume"]] = float("NaN")
            else:
                resultsTable.loc[x, ["Asset Daily Avg Volume"]] = np.mean(self.AssetDf["Volume"])

            assetCumulReturns = self.AssetDf["Log_Returns"].cumsum()  # Somme cumulée des rendements logarithmiques de l'actif
            assetCumulReturns = np.exp(assetCumulReturns)  # Transformations en rendements discrets
            buyAndHoldcapital = self.initialBalance * assetCumulReturns  # Evolution d'un investissemnt "buy and hold"

            resultsTable.loc[x, ["Asset Return %"]] = assetPercentPerf

            resultsTable.loc[x, ["Buy & Hold Return"]] = assetPercentPerf * self.initialBalance

            assetMaxDD, _ = self.__maxDD(self.AssetDf[priceColumn])

            resultsTable.loc[x, ["Asset Max Drawdown"]] = assetMaxDD

            resultsTable.loc[x, ["Used Stop-Loss"]] = usedStopLoss

            resultsTable.loc[x, ["Used Take-Profit"]] = usedTakeProfit

            resultsTable.loc[x, ["Initial Capital"]] = self.initialBalance

            resultsTable.loc[x, ["Total fees payed"]] = totalFees

            resultsTable.loc[x, ["Asset Annualized Return %"]] =  (assetPercentPerf + 1) ** (tradingDaysNb / len(self.AssetDf)) - 1
            resultsTable.loc[x, ["Asset Annualized Volatility"]] = np.std(self.AssetDf["Log_Returns"]) * (tradingDaysNb ** 0.5)

            #print(tradingDaysNb * np.mean(self.AssetDf["Log_Returns"]))
            resultsTable.loc[x, ["Asset Sharpe Ratio"]] = (((assetPercentPerf + 1) ** (tradingDaysNb / len(self.AssetDf)) - 1) - self.rf) / (np.std(self.AssetDf["Log_Returns"]) * (tradingDaysNb ** 0.5))

            self.resultsTable = resultsTable


            ##################
            # Graphic coding #
            ##################

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
                ax3.legend(loc=2, prop={'size': 9})


                # On enregistre la date du dernier ordre, qu'il soit achat ou vente pour pouvoir déterminer le capital dans le marché
                if len(dateBUY) > 0 and len(dateSELL) > 0: # Si il y a eu des achats et des ventes
                    if dateBUY[-1] > dateSELL[-1]: # Le dernier ordre est un achat
                        lastDate = dateBUY[-1]
                    elif dateBUY[-1] < dateSELL[-1]:
                        lastDate = dateSELL[-1] # Dans ce cas on vérifie si le short est activé
                elif len(dateBUY) > 0 or len(dateSELL) > 0: # Sinon on vérifie si il y a eu au moins 1 achat ou 1 vente
                    if len(dateBUY) > 0: lastDate = dateBUY[-1]
                    if len(dateSELL) > 0: lastDate = dateSELL[-1]
                else: # Sinon cela veut dire qu'il n'y eu ni achat ni vente
                    lastDate = 0

                if lastDate != 0:
                    if openPosition == 0:
                        ax2.plot(self.AssetDf.index[1:], self.portfolioBalanceEvolution, label="Portfolio equity", linewidth=0.8, color='#0d7a21')
                    else:
                        realisedReturn = (self.AssetDf.index <= lastDate)  # les rendements antérieurs au dernier ordre
                        dateRdtRealise = self.AssetDf.index[realisedReturn]  # les dates antérieurs au dernier ordre

                        ax2.plot(dateRdtRealise[1:], np.array(self.portfolioBalanceEvolution)[realisedReturn[1:]], label="Portfolio equity", linewidth=0.8, color='#0d7a21') # L'évolution du portefeuille réalisé

                        openReturn = (self.AssetDf.index >= lastDate)  # les rendements postérieurs au dernier ordre
                        dateOpenReturn = self.AssetDf.index[openReturn]  # les dates postérieures au dernier ordre
                        ax2.plot(dateOpenReturn, np.array(self.portfolioBalanceEvolution)[openReturn[1:]], label="Capital in market", linewidth=0.8, color="red")

                ax2.plot(self.AssetDf.index, buyAndHoldcapital, label="Buy & Hold Scenario", linewidth=0.8)

                if len(dateSL) > 0:
                    ax1.plot(dateSL, stopLo, "_", markersize=7, color='r', label="Stop-Loss Activated")
                if len(dateTp) > 0:
                    ax1.plot(dateTp, takeProf, "_", markersize=7, color='#d000ff', label="Take-Profit Activated")


                ax1.legend(loc=2, prop={'size': 9})
                ax2.legend(loc=2, prop={'size': 8})

            x += 1

        print("Done !")

    # Fonction qui permet de calculer le max DrawDown
    def __maxDD(self, vector):
        vector = pd.Series(vector)  # On transforme le vecteur en liste pandas pour lui appliquer la fonction pandas "cummax"
        rolledMax = vector.cummax()  # Permet de recenser le max, chaque jour, en fonction du dernier max
        dailyDD = vector / rolledMax - 1.0  # Si on divise chaque prix par le max de la période, on obtient le changement par rapport au max de la période

        return np.nanmin(dailyDD), dailyDD

    def seasonalityTable(self, ticker=None):

        """

        Returns a pivot table with the profits & losses for each years / months of the strategy.
        It gives a good overview of the return seasonality.

        """

        if ticker != None:
            transacDf = self.transactionTable[self.transactionTable["Ticker"] == ticker] # L'utilisateur peut préciser un ticker si l'analyse a été faite sur plusieurs
        else:
            transacDf = self.transactionTable  # On crée une copie de la table des transactions

        transacDf['Date'] = pd.to_datetime(transacDf['Date'], errors='coerce')
        transacDf["Year"] = transacDf['Date'].dt.year
        transacDf["Month"] = transacDf['Date'].dt.strftime('%b')

        transacDf = pd.pivot_table(transacDf, index=transacDf["Month"], columns=transacDf['Year'], values='P/L', aggfunc=np.mean, fill_value=0)

        return transacDf

    def optimize(self, indicator, fastMaRange=[], slowMaRange=[], type="max"):

        results = pd.DataFrame(columns=["fastMA", "slowMA", str(indicator)])

        totalPossibilies = (fastMaRange[1] - fastMaRange[0] + 1)*(slowMaRange[1] - slowMaRange[0] + 1) # Revoir ça
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


