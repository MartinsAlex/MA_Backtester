import MA_Backtester as mab

strat = mab.movingAverageCrossover(["AAPL", "TSLA"], 50, 200, "2017-01-01", "2020-01-01", shortLong="both", capital=1_000_000, maType="exp", makeplot=True)

strat.analyse()

print(strat.resultsTable)

print(strat.transactionTable)
