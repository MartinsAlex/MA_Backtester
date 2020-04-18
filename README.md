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

La fonction retourne deux tables, la première contient différentes statistiques concernant la stratégie :

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

La seconde, les transactions effectuées :

<table border="1" class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th></th>
      <th>Date</th>
      <th>Type</th>
      <th>Price</th>
      <th>Ticker</th>
      <th>P/L</th>
      <th>Number of shares</th>
      <th>Total P/L</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>0</th>
      <td>2015-09-13</td>
      <td>Buy Short</td>
      <td>230.643997</td>
      <td>BTC-USD</td>
      <td>NaN</td>
      <td>4336</td>
      <td>NaN</td>
    </tr>
    <tr>
      <th>1</th>
      <td>2015-10-28</td>
      <td>Sell Short</td>
      <td>304.618011</td>
      <td>BTC-USD</td>
      <td>-73.974014</td>
      <td>4336</td>
      <td>-320751</td>
    </tr>
    <tr>
      <th>2</th>
      <td>2015-10-28</td>
      <td>Buy Long</td>
      <td>304.618011</td>
      <td>BTC-USD</td>
      <td>NaN</td>
      <td>2230</td>
      <td>NaN</td>
    </tr>
    <tr>
      <th>3</th>
      <td>2018-03-29</td>
      <td>Sell Long</td>
      <td>6890.520020</td>
      <td>BTC-USD</td>
      <td>6585.902008</td>
      <td>2230</td>
      <td>1.46866e+07</td>
    </tr>
    <tr>
      <th>4</th>
      <td>2018-03-29</td>
      <td>Buy Short</td>
      <td>6890.520020</td>
      <td>BTC-USD</td>
      <td>NaN</td>
      <td>2230</td>
      <td>NaN</td>
    </tr>
    <tr>
      <th>5</th>
      <td>2019-04-23</td>
      <td>Sell Short</td>
      <td>5464.866699</td>
      <td>BTC-USD</td>
      <td>1425.653320</td>
      <td>2230</td>
      <td>3.17921e+06</td>
    </tr>
    <tr>
      <th>6</th>
      <td>2019-04-23</td>
      <td>Buy Long</td>
      <td>5464.866699</td>
      <td>BTC-USD</td>
      <td>NaN</td>
      <td>3393</td>
      <td>NaN</td>
    </tr>
    <tr>
      <th>7</th>
      <td>2019-10-25</td>
      <td>Sell Long</td>
      <td>9244.972656</td>
      <td>BTC-USD</td>
      <td>3780.105957</td>
      <td>3393</td>
      <td>1.28259e+07</td>
    </tr>
    <tr>
      <th>8</th>
      <td>2019-10-25</td>
      <td>Buy Short</td>
      <td>9244.972656</td>
      <td>BTC-USD</td>
      <td>NaN</td>
      <td>3393</td>
      <td>NaN</td>
    </tr>
    <tr>
      <th>9</th>
      <td>2020-02-19</td>
      <td>Sell Short</td>
      <td>9633.386719</td>
      <td>BTC-USD</td>
      <td>-388.414062</td>
      <td>3393</td>
      <td>-1.31789e+06</td>
    </tr>
    <tr>
      <th>10</th>
      <td>2020-02-19</td>
      <td>Buy Long</td>
      <td>9633.386719</td>
      <td>BTC-USD</td>
      <td>NaN</td>
      <td>3120</td>
      <td>NaN</td>
    </tr>
    <tr>
      <th>11</th>
      <td>2020-03-25</td>
      <td>Sell Long</td>
      <td>6681.062988</td>
      <td>BTC-USD</td>
      <td>-2952.323730</td>
      <td>3120</td>
      <td>-9.21125e+06</td>
    </tr>
    <tr>
      <th>12</th>
      <td>2020-03-25</td>
      <td>Buy Short</td>
      <td>6681.062988</td>
      <td>BTC-USD</td>
      <td>NaN</td>
      <td>3120</td>
      <td>NaN</td>
    </tr>
  </tbody>
</table>


Le dernier élément retourné est un graphique, si l'argument showplot est "True" :

```python

plt.show()

```

![png](readme_files/btc.png)



