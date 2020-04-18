# MA_Backtester
## Un module permettant le backtesting de stratégies de trading, basées sur le croisement de moyennes mobiles

---

# Contenu :

- [Algorithmes](https://github.com/MartinsAlex/Backtesting/tree/master/Algorithmes) : toutes les fonctions
- [Stratégies](https://github.com/MartinsAlex/Backtesting/tree/master/Strat%C3%A9gies) : exemples de stratégies analysées
- [Listes de tickers](https://github.com/MartinsAlex/Backtesting/tree/master/Listes%20de%20tickers) : fichiers csv contenant quelques tickers (symbol) pouvant être utilisés
- Documentation : fichier d'aide pour les fonction (..)
- [Examples](https://github.com/MartinsAlex/Backtesting/tree/master/Examples) : quelques examples d'utilisation

---


# Comment ça marche ?


```python
    import MA_Backtester as mab
    
    stats, transactions, fig = MA_CROSS(["BTC-USD"], 50, 200, "2015-02-01", "2020-04-18", 
                                ma="simple", 
                                showplot=True, 
                                shortLong="both", 
                                capital=1_000_000)
    
```
<table border="1" class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th></th>
      <th>From</th>
      <th>To</th>
      <th>Ticker</th>
      <th>Number of Trades</th>
      <th>Winning Trades</th>
      <th>Losing Trades</th>
      <th>Largest Winning Trade</th>
      <th>Largest Losing Trade</th>
      <th>% Profitable</th>
      <th>Expectancy</th>
      <th>Total Realized Return</th>
      <th>Buy &amp; Hold Return</th>
      <th>Asset Return %</th>
      <th>Strategy Return %</th>
      <th>Strategy Max Drawdown</th>
      <th>Asset Max Drawdown</th>
      <th>Open position</th>
      <th>Open Trade P/L</th>
      <th>Total Return</th>
      <th>Strategy Annualized Volatility</th>
      <th>Asset Annualized Volatility</th>
      <th>Used Stop-Loss</th>
      <th>Used Stop-Gain</th>
      <th>Asset Sharpe Ratio</th>
      <th>Market Exposure</th>
      <th>Strategy Sharpe Ratio</th>
      <th>Asset Daily Avg Volume</th>
      <th>Avg Holding Days</th>
      <th>Initial Capital</th>
      <th>Final Capital</th>
      <th>Asset Annualized Return %</th>
      <th>Strategy Annualized Return %</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>1</th>
      <td>2015-02-01</td>
      <td>2020-04-18</td>
      <td>BTC-USD</td>
      <td>6</td>
      <td>3</td>
      <td>3</td>
      <td>3.17921e+06</td>
      <td>-1.31789e+06</td>
      <td>0.5</td>
      <td>1396.16</td>
      <td>1.98418e+07</td>
      <td>3.044e+07</td>
      <td>30.44</td>
      <td>19.8418</td>
      <td>-0.646593</td>
      <td>-0.83399</td>
      <td>-6681.06</td>
      <td>-1.4194e+06</td>
      <td>1.98413e+07</td>
      <td>0.643272</td>
      <td>0.624574</td>
      <td>0</td>
      <td>0</td>
      <td>0.729799</td>
      <td>0.88124</td>
      <td>0.800122</td>
      <td>6.92948e+09</td>
      <td>276</td>
      <td>1000000</td>
      <td>2.08418e+07</td>
      <td>0.578703</td>
      <td>0.495053</td>
    </tr>
  </tbody>
</table>






