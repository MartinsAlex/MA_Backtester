import pandas as pd
import numpy as np
from pandas_datareader import data, wb
import datetime as dt
from scipy import stats
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import matplotlib.dates as mdates
from pandas.plotting import register_matplotlib_converters
from pandas_datareader._utils import RemoteDataError

register_matplotlib_converters()

pd.set_option('display.max_columns', 500)
pd.set_option('display.max_rows', 250)


def MA_CROSS(tickerList, fastSma, slowSma, beginDate, endDate, ma=str, shortLong=str, capital=1_000_000, showplot=bool,
             stop=[None, None], rf=None):

    # Result table with column names
    resultsTable = pd.DataFrame(columns=["From", "To", "Ticker", "Number of Trades", "Winning Trades", "Losing Trades", "Largest Winning Trade",
                 "Largest Losing Trade", "% Profitable", "Expectancy", "Total Realized Return",
                 "Buy & Hold Return", "Asset Return %", "Strategy Return %", "Strategy Max Drawdown", "Asset Max Drawdown",
                 "Open position", "Open Trade P/L", "Total Return", "Strategy Annualized Volatility",
                 "Asset Annualized Volatility", "Used Stop-Loss", "Used Stop-Gain", "Asset Sharpe Ratio", "Market Exposure",
                 "Strategy Sharpe Ratio", "Asset Daily Avg Volume", "Avg Holding Days", "Initial Capital", "Final Capital", 'Asset Annualized Return %',
                                         'Strategy Annualized Return %'])

    # Table of transactions
    transactionTable = pd.DataFrame(columns=["Date", "Type", "Price", "Ticker", "P/L", "Number of shares"])

    # Forex Symbols from Federal Reserve Economic Data | FRED | St. Louis Fed
    forexFREDlist = ['DEXUSAL', "DEXBZUS", "DEXUSUK", "DEXCAUS", "DEXCHUS", "DEXDNUS", "DEXUSEU", "DEXHKUS", "DEXINUS",
                     "DEXJPUS", "DEXMAUS", "DEXMXUS", "DEXTAUS", "DEXUSNZ", "DEXNOUS", "DEXSIUS", "DEXSFUS", "DEXKOUS",
                     "DEXSLUS", "DEXSDUS", "DEXSZUS", "DEXTHUS"]

    # Liste des monnaies cotées indirectement
    forexIndirect = ["DEXBZUS", "DEXCAUS", "DEXCHUS", "DEXDNUS", "DEXHKUS", "DEXINUS", "DEXJPUS", "DEXMAUS",
                     "DEXMXUS", "DEXTAUS", "DEXNOUS", "DEXSIUS", "DEXSFUS", "DEXKOUS", "DEXSLUS", "DEXSDUS",
                     "DEXSZUS", "DEXTHUS"]

    x = 1  # Sers à indiquer la ligne pour l'ajout dans la table des résultats

    for symbol in tickerList: # On commence la boucle qui va itérer sur chaque symbol dans la liste
        print(x / len(tickerList) * 100, " %..")  # Sert à imprimer la progression

        if symbol in forexFREDlist: # On vérifie si le symbol est une monnaie (s'il est dans la liste des symbols forex)
            df = data.get_data_fred(symbol, beginDate, endDate) # On effectue la requête avec la fonction de pandas_datareader
            df = df.dropna()  # On élimine toutes les lignes qui ont des NaN
            priceColumn = symbol # On fixe le nom de la colonne contenant les prix car il varie selon la source

            if symbol in forexIndirect : # Si la monnaie est dans la liste des indirectes, il faut inverser son cours pour refléter sa valeur en USD
                df[symbol] = df[symbol] ** (-1)

        else:

            try:
                df = data.get_data_yahoo(symbol, beginDate, endDate, interval='d')
            except (RemoteDataError, KeyError, OverflowError) as exp: # Si il y a erreur on regarde si le problème vient de la date
                try:
                    dfTest = data.get_data_yahoo(symbol, "1980-01-01", interval='d') # On télécharge la df entièrement
                    firstDate = dfTest.index[0] # On prend la date minimale
                    df = data.get_data_yahoo(symbol, firstDate, "2017-08-31", interval='d') # On re-effectue la requête avec cette date
                except: # Sinon le problème vient du fait que le symbol ne marche pas
                    print("Ticker {} not working".format(symbol))
                    resultsTable.loc[x, ["Ticker"]] = symbol


                    if len(tickerList)==1: # Si il n'y pas d'autres actif à analyser on quitte l'application
                        quit()
                    else:
                        continue

                    i += 1
                    x += 1

            df = df.dropna() # On élimine toutes les lignes qui ont des NaN
            priceColumn = "Adj Close" # On fixe le nom de la colonne contenant les prix car il varie selon la source


        df["Log_Returns"] = np.log(1 + df[priceColumn].pct_change(1)) # Rendeemnt logarithmique journalier: permet des opérations arithmétiques plus simples que les rendements discrets

        # Simple Moving Average
        if ma == "simple":
            moyenneAcronym = "SMA"
            shortMaCol = moyenneAcronym + str(fastSma)
            longMaCol = moyenneAcronym + str(slowSma)

            df[shortMaCol] = df[priceColumn].rolling(fastSma).mean()
            df[longMaCol] = df[priceColumn].rolling(slowSma).mean()

        # Weighted Moving Average
        elif ma == "weighted":
            moyenneAcronym = "WMA"
            shortMaCol = moyenneAcronym + str(fastSma)
            longMaCol = moyenneAcronym + str(slowSma)

            weights1 = np.arange(1, (fastSma) + 1)
            weights2 = np.arange(1, (slowSma) + 1)

            df[moyenneAcronym + str(fastSma)] = df[priceColumn].rolling(fastSma).apply(
                lambda prices: np.dot(prices, weights1) / weights1.sum(), raw=True) # On multiplie chaque x dernier prix prix par le poids qui lui est attribué,
            # puis on divise par la somme des poids pour obtenir la moyenne pondérée

            df[moyenneAcronym + str(slowSma)] = df[priceColumn].rolling(slowSma).apply(
                lambda prices: np.dot(prices, weights2) / weights2.sum(), raw=True)

        # Exponentially weighted Moving Average
        elif ma == "exp":
            moyenneAcronym = "EMA"
            shortMaCol = moyenneAcronym + str(fastSma)
            longMaCol = moyenneAcronym + str(slowSma)

            df[shortMaCol] = df[priceColumn].ewm(span=fastSma,
                                                 adjust=False,
                                                 min_periods=fastSma,
                                                 ).mean()

            df[longMaCol] = df[priceColumn].ewm(span=slowSma,
                                                adjust=False,
                                                min_periods=slowSma,
                                                ).mean()


        ############################
        ## Variables pour calculs ##
        ############################

        longPrice, shortPrice = 0, 0 # Variables qui enregistrent le prix d'achat d'une position long ou short

        nbTrades = 0 # Variable qui enregistre le nombre de trade (positions clôturées)

        winTrade, looseTrade  = 0, 0 # Nb de trade gagnants et perdants

        usedStopLoss, usedStopGain = 0, 0 # Nb de stops activés

        stratReturns = [] # Vecteur qui enregistre les variations journalières

        profitAndLoss = [] # Vecteur qui enregistre les pertes et profits des opérations

        stratMaxDD, stratPrice = 0, [] # Pour le calcul du max DrawDown de la stratégie

        gains, lost = [], [] # Montant des trades gagnants / perdants

        holdingDays, avgDays = 0, [] # Nb de jours durant lequel on détient une position et nb de jours moyen

        capit, assetNb = capital, 0 # Capital initial et nb d'actifs détenus

        #################################
        ## Variables pour le graphique ##
        #################################

        stopLo, dateSL, stopGain, dateSg = [], [], [], [] # Vecteurs qui enregistrent les prix et date de ventes (liées aux stop-loss)

        portfolioEvolution, portfolioDate = [], [] # Pour le graphique qui compare le portefeuille à l'actif

        BUY, dateBUY, SELL, dateSELL = [], [], [], [] # Vecteurs prix d'achats, ventes et dates

        #############
        # Main Loop #
        #############

        for i in range(1, len(df[priceColumn])): # On doit commencer à 1 car sinon on peut pas comparer à la période précédente

            portfolioEvolution.append(capit) # On enregistre la valeur actuelle du portefeuille (et la date)
            portfolioDate.append(df.index[i])

            if longPrice > 0: # Si on a une position long ouverte, on enregistre :
                stratReturns.append(df["Log_Returns"].iloc[i])  # La variation journalière subit (pour calculer la volatilité)
                stratPrice.append(df[priceColumn].iloc[i])  # Le prix du titre détenu

                stratDD = maxDD(stratPrice, "long")  # Le DD actuel
                if stratMaxDD > stratDD : stratMaxDD = stratDD  # Si le DD calculé est plus faible que le précédent on le replace par le nouveau
                holdingDays += 1 # Un jour de plus durant lequel on a détenu une position

            elif shortPrice>0: # Si on a une position short ouverte, on enregistre :
                stratReturns.append(df["Log_Returns"].iloc[i])  # La variation journalière subit (pour calculer la volatilité)
                stratPrice.append(df[priceColumn].iloc[i])  # Le prix du titre détenu
                stratDD = maxDD(stratPrice, "short")  # Le DD actuel
                if stratMaxDD > stratDD : stratMaxDD = stratDD # Si le DD calculé est plus faible que le précédent on le replace par le nouveau

                holdingDays += 1  # Un jour de plus durant lequel on a détenu une position



            ##############
            # BUY SIGNAL #
            ##############

            # Si en période t-1 la MA50 était plus faible que la MA200 et que maintenant elle est plus grande, on achète car cela veut dire qu'elle a dépassé par le bas
            if (df[shortMaCol].iloc[i - 1] < df[longMaCol].iloc[i - 1] and df[shortMaCol].iloc[i] > df[longMaCol].iloc[i]):

                BUY.append(df[shortMaCol].iloc[i])
                dateBUY.append(df.index[i])

                ###############
                # Vente Short #
                ###############

                # Et on liquide la position short si il y en a une et que le short est activé
                if (shortLong == "both" or shortLong == "short") and shortPrice > 0:
                    profitAndLoss.append((shortPrice - df[priceColumn].iloc[i])* assetNb)

                    capit += (shortPrice - df[priceColumn].iloc[i]) * assetNb

                    # Win & Loss stats
                    winTrade, looseTrade, gains, lost = winLossRatio((shortPrice - df[priceColumn].iloc[i]), winTrade, looseTrade, gains, lost)

                    # On enregistre la transaction
                    transac = {"Date": df.index[i].strftime("%Y-%m-%d"), "Type": "Sell Short",
                               "Price": df[priceColumn].iloc[i], "Ticker": symbol,
                               "P/L": (shortPrice - df[priceColumn].iloc[i]),
                               "Number of shares": assetNb}

                    transactionTable = transactionTable.append(transac, ignore_index=True)

                    nbTrades += 1
                    shortPrice = 0
                    stratPrice = []  # Pour "Strategy Max DrawDown"
                    avgDays.append(holdingDays)
                    holdingDays = 0
                    assetNb = 0


                ##############
                # Achat Long #
                ##############

                # On achète que si aucune position est déjà détenue, le long est activé
                if longPrice == 0 and (shortLong == "both" or shortLong == "long"):
                    # On vérifie qu'il y ait assez de fonds pour acheté au moins 1 actif
                    if ((capit / df[priceColumn].iloc[i]) < 1):
                        #print("Fonds insuffisant")
                        continue

                    if shortLong == "both" or shortLong == "long":  # On achète que si le long est activé (ou le short + long)
                        longPrice = df[priceColumn].iloc[i]

                        assetNb = int(round(capit / longPrice, 0))

                        # On enregistre la transaction
                        transac = {"Date": df.index[i].strftime("%Y-%m-%d"), "Type": "Buy Long",
                                   "Price": df[priceColumn].iloc[i], "Ticker": symbol,
                                   "Number of shares": assetNb}
                        transactionTable = transactionTable.append(transac, ignore_index=True)



            ###############
            # SELL SIGNAL #
            ###############

            # Si en période t-1 la MA50 était plus élevée que la MA200 et que mnt elle est plus faible, on vend car cela veut dire qu'elle est repassé en dessous (par le haut)
            if (df[shortMaCol].iloc[i - 1] > df[longMaCol].iloc[i - 1] and df[shortMaCol].iloc[i] < df[longMaCol].iloc[i]): #le i ne doit pas dépasser la longueur de la df


                SELL.append(df[shortMaCol].iloc[i])
                dateSELL.append(df.index[i])

                ##############
                # Vente Long #
                ##############

                # Et que mnt elle est plus faible, on vend car cela veut dire qu'elle est repassé en dessous (par le haut)
                # On enregistre la date et le prix du signal de vente

                if shortLong == "both" or shortLong == "long":  # Cette partie ne concerne que le long
                    # Si il y a une position long ouverte, on la vend
                    if longPrice > 0:

                        profitAndLoss.append(df[priceColumn].iloc[i] - longPrice)

                        capit += (df[priceColumn].iloc[i] - longPrice)*assetNb

                        # Win & Loss stats
                        winTrade, looseTrade, gains, lost = winLossRatio((df[priceColumn].iloc[i] - longPrice), winTrade, looseTrade, gains, lost)

                        # On enregistre la transaction
                        transac = {"Date": df.index[i].strftime("%Y-%m-%d"), "Type": "Sell Long",
                                   "Price": df[priceColumn].iloc[i], "Ticker": symbol,
                                   "P/L": (df[priceColumn].iloc[i] - longPrice),
                                   "Number of shares": assetNb}
                        transactionTable = transactionTable.append(transac, ignore_index=True)

                        longPrice = 0
                        nbTrades += 1
                        stratPrice = []  # Pour "Strategy Max DrawDown"
                        avgDays.append(holdingDays)
                        holdingDays = 0
                        assetNb = 0

                ###############
                # Achat Short #
                ###############

                # On prend une position short si le short est activé (ou le short + long) et qu'il n'y en a pas déjà une
                if (shortLong == "both" or shortLong == "short") and shortPrice==0:

                    shortPrice = df[priceColumn].iloc[i]
                    assetNb = int(round(capit / shortPrice, 0))

                    # On enregistre la transaction
                    transac = {"Date": df.index[i].strftime("%Y-%m-%d"), "Type": "Buy Short",
                               "Price": df[priceColumn].iloc[i], "Ticker": symbol,
                               "Number of shares": assetNb}
                    transactionTable = transactionTable.append(transac, ignore_index=True)


            ##########
            ## STOP ##
            ##########

            ###############
            ## STOP-LOSS ##  =  Vente à partir d'une certaine perte
            ###############

            # Si le stop-loss est précisé
            if stop[0] != None :

                ##############
                # Vente Long #
                ##############

                if longPrice > 0:
                    # Et que la perte dépasse le stop-loss on vend
                    if (longPrice / df[priceColumn].iloc[i] - 1) >= stop[0]:

                        # gain réalisé
                        capit += (df[priceColumn].iloc[i] - longPrice)*assetNb
                        profitAndLoss.append(df[priceColumn].iloc[i] - longPrice)

                        # Win & Loss stats
                        winTrade, looseTrade, gains, lost = winLossRatio((df[priceColumn].iloc[i] - longPrice),
                                                                         winTrade, looseTrade, gains, lost)

                        # on enregistre le prix et la date de la vente
                        stopLo.append(df[priceColumn].iloc[i])
                        dateSL.append(df.index[i])

                        # On enregistre la transaction
                        transac = {"Date": df.index[i].strftime("%Y-%m-%d"), "Type": "Stop Loss Long",
                                   "Price": df[priceColumn].iloc[i], "Ticker": symbol,
                                   "P/L": (df[priceColumn].iloc[i] - longPrice),
                                   "Number of shares": assetNb}
                        transactionTable = transactionTable.append(transac, ignore_index=True)

                        longPrice = 0
                        nbTrades += 1
                        usedStopLoss += 1
                        stratPrice = []  # Pour "Strategy Max DrawDown"
                        avgDays.append(holdingDays)
                        holdingDays = 0
                        assetNb = 0


                ###############
                # Vente Short #
                ###############

                if shortPrice > 0 :
                    if (df[priceColumn].iloc[i] / shortPrice - 1) >= stop[0]: #Si la perte dépasse celle indiquée

                        capit += (shortPrice - df[priceColumn].iloc[i]) * assetNb
                        profitAndLoss.append(shortPrice - df[priceColumn].iloc[i])

                        # on enregistre le prix et la date de la vente
                        stopLo.append(df[priceColumn].iloc[i])
                        dateSL.append(df.index[i])

                        # Win & Loss stats
                        winTrade, looseTrade, gains, lost = winLossRatio((shortPrice - df[priceColumn].iloc[i]), winTrade, looseTrade, gains, lost)

                            # On enregistre la transaction
                        transac = {"Date": df.index[i].strftime("%Y-%m-%d"), "Type": "Stop Loss Short",
                                   "Price": df[priceColumn].iloc[i], "Ticker": symbol,
                                   "P/L": (shortPrice - df[priceColumn].iloc[i]),
                                   "Number of shares": assetNb}

                        transactionTable = transactionTable.append(transac, ignore_index=True)

                        nbTrades += 1
                        shortPrice = 0
                        usedStopLoss += 1
                        stratPrice = []  # Pour "Strategy Max DrawDown"
                        avgDays.append(holdingDays)
                        holdingDays = 0
                        assetNb = 0

            #################
            ##  STOP-GAIN  ##  =  Vente à partir d'un certain gain
            #################

            #Si un stop-gain est précisé
            if stop[1] != None:

                ##############
                # Vente Long #
                ##############

                if longPrice > 0:
                    # Et que le gain dépasse on vend
                    if (df[priceColumn].iloc[i] / longPrice - 1) >= stop[1]:
                        # gain réalisé
                        capit += (df[priceColumn].iloc[i] - longPrice)*assetNb
                        profitAndLoss.append(df[priceColumn].iloc[i] - longPrice)

                        # Win & Loss stats
                        winTrade, looseTrade, gains, lost = winLossRatio((df[priceColumn].iloc[i] - longPrice),
                                                                         winTrade, looseTrade, gains, lost)

                        # on enregistre le prix et la date de la vente
                        stopGain.append(df[priceColumn].iloc[i])
                        dateSg.append(df.index[i])

                        # On enregistre la transaction
                        transac = {"Date": df.index[i].strftime("%Y-%m-%d"), "Type": "Stop Gain Long",
                                   "Price": df[priceColumn].iloc[i], "Ticker": symbol,
                                   "P/L": (df[priceColumn].iloc[i] - longPrice)}
                        transactionTable = transactionTable.append(transac, ignore_index=True)

                        longPrice = 0
                        nbTrades += 1
                        usedStopGain += 1
                        stratPrice = []  # Pour "Strategy Max DrawDown"
                        avgDays.append(holdingDays)
                        holdingDays = 0
                        assetNb = 0

                ###############
                # Vente Short #
                ###############

                if shortPrice > 0:
                    if (shortPrice / df[priceColumn].iloc[i]  - 1) >= stop[1]:
                        capit += (shortPrice - df[priceColumn].iloc[i]) * assetNb
                        profitAndLoss.append(shortPrice - df[priceColumn].iloc[i])

                        # on enregistre le prix et la date de la vente
                        stopGain.append(df[priceColumn].iloc[i])
                        dateSg.append(df.index[i])

                        # Win & Loss stats
                        winTrade, looseTrade, gains, lost = winLossRatio((shortPrice - df[priceColumn].iloc[i]), winTrade, looseTrade, gains, lost)

                        # On enregistre la transaction
                        transac = {"Date": df.index[i].strftime("%Y-%m-%d"), "Type": "Stop Gain Short",
                                   "Price": df[priceColumn].iloc[i], "Ticker": symbol,
                                   "P/L": (shortPrice - df[priceColumn].iloc[i])}
                        transactionTable = transactionTable.append(transac, ignore_index=True)

                        nbTrades += 1
                        shortPrice = 0
                        usedStopGain += 1
                        avgDays.append(holdingDays)
                        holdingDays = 0
                        assetNb = 0


        #######################################
        # Calculs finaux (dont open position) #
        #######################################

        # On regarde si il reste une position ouverte (long ou short)
        if longPrice > 0:
            openPosition = longPrice
            nonRealizedReturn = (df[priceColumn].iloc[len(df) - 1] - longPrice)
            longPrice = 0  # On remet la variable à zéro pour la prochaine boucle

        elif shortPrice > 0:
            openPosition = -shortPrice
            nonRealizedReturn = (shortPrice - df[priceColumn].iloc[len(df) - 1])
            shortPrice = 0

        else:  # Il n'y pas de position ouverte
            openPosition = 0
            nonRealizedReturn = 0


        #####################################################
        # Début de l'écriture dans le tableau des résultats #
        #####################################################

        resultsTable.loc[x, ["From"]] = df.index[0].strftime("%Y-%m-%d")
        resultsTable.loc[x, ["To"]] = df.index[len(df) - 1].strftime("%Y-%m-%d")

        resultsTable.loc[x, ["Ticker"]] = symbol
        resultsTable.loc[x, ["Number of Trades"]] = nbTrades

        assetPercentPerf = (df[priceColumn].iloc[len(df) - 1] / df[priceColumn].iloc[0]) - 1


        if nbTrades > 0: # Si au moins 1 trade a été effectué
            resultsTable.loc[x, ["Winning Trades"]] = winTrade
            resultsTable.loc[x, ["Losing Trades"]] = looseTrade
            resultsTable.loc[x, ["Largest Winning Trade"]] = round(max(profitAndLoss, default=0), 4)
            resultsTable.loc[x, ["Largest Losing Trade"]] = round(min(profitAndLoss, default=0), 4)

            resultsTable.loc[x, ["% Profitable"]] = round(winTrade / nbTrades, 4)

            resultsTable.loc[x, ["Expectancy"]] = ((winTrade / nbTrades) * np.mean(gains)) + (
                        (1 - winTrade / nbTrades) * np.mean(lost)) # = Espérance

            resultsTable.loc[x, ["Avg Holding Days"]] = round(np.mean(avgDays), 0)
            resultsTable.loc[x, ["Strategy Annualized Volatility"]] = np.std(stratReturns) * (252 ** 0.5)
            resultsTable.loc[x, ["Total Realized Return"]] = (capit - capital)
            resultsTable.loc[x, ["Strategy Return %"]] = capit / capital - 1

            if capit < 1 : # Si on s'est carrément endetté avec une position short, on ne peut pas calculer le rdt annualisé
                resultsTable.loc[x, ["Strategy Annualized Return %"]] = float("NaN")
            else:
                resultsTable.loc[x, ["Strategy Annualized Return %"]] = (capit / capital) ** (252 / float(len(df))) - 1


        resultsTable.loc[x, ["Open position"]] = openPosition
        resultsTable.loc[x, ["Open Trade P/L"]] = nonRealizedReturn*assetNb
        resultsTable.loc[x, ["Total Return"]] = round(((capit-capital) + nonRealizedReturn), 4)

        if symbol in forexFREDlist: # Le volume n'est pas fourni par FRED pour le forex
            resultsTable.loc[x, ["Asset Daily Avg Volume"]] = float("NaN")
        else:
            resultsTable.loc[x, ["Asset Daily Avg Volume"]] = np.mean(df["Volume"])

        rt = df["Log_Returns"].cumsum()  # Somme cumulés des rendements logarithmiques
        rt = np.exp(rt)  # Transformations en rendements discrets
        buyAndHoldcapital = capital * rt  # Evolution d'un investissemnt "buy and hold"

        resultsTable.loc[x, ["Asset Return %"]] = assetPercentPerf

        resultsTable.loc[x, ["Buy & Hold Return"]] = assetPercentPerf * capital

        resultsTable.loc[x, ["Strategy Max Drawdown"]] = stratMaxDD

        resultsTable.loc[x, ["Asset Max Drawdown"]] = maxDD(df[priceColumn], "long")

        resultsTable.loc[x, ["Market Exposure"]] = len(stratReturns) / len(df)

        resultsTable.loc[x, ["Asset Annualized Volatility"]] = np.std(df["Log_Returns"]) * (252 ** 0.5)

        if rf == None:
            # Si le taux sans risque n'est pas précisé on prend le taux du treasury bond à 3 mois
            tYield = data.get_data_yahoo("^IRX", "2019-12-30", dt.datetime.today(), interval='d')
            rf = tYield["Adj Close"].iloc[len(tYield) - 1] / 100

        # Il faut annualiser le rendement et la volatilité pour calculer le sharpe-ratio
        resultsTable.loc[x, ["Asset Sharpe Ratio"]] = (252 * np.mean(df["Log_Returns"]) - rf) / (np.std(df["Log_Returns"]) * (252 ** 0.5))

        resultsTable.loc[x, ["Strategy Sharpe Ratio"]] = (252 * np.mean(stratReturns) - rf) / (np.std(stratReturns) * (252 ** 0.5)) #Rdt annualisé

        resultsTable.loc[x, ["Used Stop-Loss"]] = usedStopLoss

        resultsTable.loc[x, ["Used Stop-Gain"]] = usedStopGain

        resultsTable.loc[x, ["Initial Capital"]] = capital

        resultsTable.loc[x, ["Final Capital"]] = capit

        resultsTable.loc[x, ["Asset Annualized Return %"]] = (df[priceColumn].iloc[len(df) - 1] / df[priceColumn].iloc[0]) ** (252 / float(len(df))) - 1


        #######################
        # Codage du graphique #
        #######################

        #fig = None #Il faut tout de même attribuer une valeur à la variable fig (même si il n'y pas de graphique)

        if showplot == True:
            fig, (ax1, ax2) = plt.subplots(2, figsize=(14, 7), gridspec_kw={'height_ratios': [3, 1]})
            fig.subplots_adjust(hspace=0.3)
            fig.subplots_adjust(top=0.92)
            ax1.grid(True)

            if shortLong == "long":
                slTitre = "(Long only)"
                buySignalLabel = "BUY LONG"
                sellSignalLabel = "SELL LONG"
            elif shortLong == "both":
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

            #ax1.bar(df.index, df["Volume"])
            #ax3 = ax1.twinx()  # instantiate a second axes that shares the same x-axis
            #ax3.bar(df.index, df["Volume"], 1, alpha=0.3, color=(df['Log_Returns'] > 0).map({True: 'g', False: 'r'}))

            ax1.set_ylabel("USD")
            ax1.plot(df.index, df[priceColumn], label="AssetPrice", linewidth=0.8)

            ax1.plot(df.index, df[shortMaCol], label=shortMaCol, linewidth=0.8)
            ax1.plot(df.index, df[longMaCol], label=longMaCol, linewidth=0.8)

            ax1.plot(dateBUY, BUY, 'o', markersize=4, color='#41e86e', label=buySignalLabel)
            ax1.plot(dateSELL, SELL, '^', markersize=4, color='#ffe608', label=sellSignalLabel)
            ax1.set_facecolor('#1d1d1f')

            ax2.plot(df.index, buyAndHoldcapital, label="Buy & Hold")

            ax2.plot(portfolioDate, portfolioEvolution, label="Portfolio", linewidth=0.8, color="red")
            ax2.set_ylabel("USD")
            ax2.set_facecolor('#1d1d1f')
            ax2.grid(True)
            ax2.set_title("Portfolio vs Asset", fontsize=10)
            ax2.ticklabel_format(style='plain', axis='y')

            if len(dateSL) > 0:
                ax1.plot(dateSL, stopLo, "_", markersize=6, color='r', label="Stop-Loss Activated")
            if len(dateSg) > 0:
                ax1.plot(dateSg, stopGain, "_", markersize=6, color='#db7ddb', label="Stop-Gain Activated")

            ax1.legend(loc=2, prop={'size': 9})
            ax2.legend(loc=2, prop={'size': 9})


            #if saveplot == True:
                #fig.savefig(r"plots/{}/{}.jpg".format(moyenneAcronym, symbol), dpi=400)


        x += 1


        transactionTable = pd.DataFrame(transactionTable)
        transactionTable["Total P/L"] = transactionTable["P/L"] * transactionTable["Number of shares"]

    return resultsTable, transactionTable, fig


# Fonction qui permet de calculer le max DrawDown
def maxDD(vector, tradeType):
    vector = pd.Series(vector)  # On transforme le vecteur en liste pandas pour lui appliquer la fonction pandas "cummax"
    if tradeType=="long":
        rolledMax = vector.cummax()  # Permet de recenser le max, chaque jour, en fonction du dernier max
        dailyDD = vector / rolledMax - 1.0  # Si on divise chaque prix par le max de la période, on obtient le changement par rapport au max de la période
    elif tradeType=="short":
        rolledMin = vector.cummin()
        dailyDD = rolledMin / vector - 1.0  # Si on divise chaque prix par le max de la période, on obtient le changement par rapport au max de la période

    return np.nanmin(dailyDD)


# Fonction qui calcule le win & loss ratio (pour simplifier et éviter de le mettre à chaque transactions)
def winLossRatio(profit, winVar, looseVar, gainVector, lostVector):
    if profit > 0:
        winVar += 1
        gainVector.append(profit)
    else:
        looseVar += 1
        lostVector.append(profit)

    return  winVar, looseVar, gainVector, lostVector

df, df2, fig = MA_CROSS(["BTC-USD"], 50, 200, "2015-02-01", dt.datetime.today(), ma="simple", showplot=True, shortLong="both", capital=1_000_000)

print(df, df2)

print(df["Asset Annualized Return %"])
print(df["Strategy Annualized Return %"])


plt.show()