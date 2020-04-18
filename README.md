[![Build Status](https://travis-ci.com/MartinsAlex/MA_Backtester.svg?branch=master)](https://travis-ci.com/MartinsAlex/MA_Backtester)

# MA_Backtester
## Un module permettant le backtesting de stratégies de trading, basées sur le croisement de moyennes mobiles



# Contenu de la page :

- [Algorithmes](https://github.com/MartinsAlex/Backtesting/tree/master/Algorithmes) : toutes les fonctions
- [Stratégies](https://github.com/MartinsAlex/Backtesting/tree/master/Strat%C3%A9gies) : exemples de stratégies analysées
- [Listes de tickers](https://github.com/MartinsAlex/Backtesting/tree/master/Listes%20de%20tickers) : fichiers csv contenant quelques tickers (symbol) pouvant être utilisés
- Documentation : fichier d'aide pour les fonction (..)
- [Examples](https://github.com/MartinsAlex/Backtesting/tree/master/Examples) : quelques examples d'utilisation



# Comment ça marche ?

## Example 1 :

#### Action Crédit Suisse, 2002 à 2010. Stratégie basée sur le croisement des moyennes mobiles simple de 50 et 200 jours. 
- Capital initial : 10'000 USD 
- Prise de position short et long.

```python
    from MA_Backtester import MA_CROSS
    import matplotlib.pyplot as plt
    
    stats, transactions, fig = MA_CROSS(["CS"], 50, 200, "2000-01-01", "2010-01-01", 
                                      ma="simple", showplot=True, shortLong="both", capital=10_000)
    
```
Les différents arguments sont expliqués dans la doc. Concernant les tickers, tout ceux de Yahoo Finance peuvent être utilisés ainsi que ceux de FRED (forex).

La fonction retourne deux tables pandas et une figure matplotlib. La première table contient différentes statistiques concernant la stratégie :

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
      <td>2000-01-03</td>
      <td>2009-12-31</td>
      <td>CS</td>
      <td>9</td>
      <td>6</td>
      <td>3</td>
      <td>5859</td>
      <td>-2148.08</td>
      <td>0.6667</td>
      <td>3.49751</td>
      <td>12994.8</td>
      <td>2871.65</td>
      <td>0.287165</td>
      <td>1.29948</td>
      <td>-0.550622</td>
      <td>-0.74091</td>
      <td>28.7958</td>
      <td>3794.66</td>
      <td>12999.6</td>
      <td>0.47174</td>
      <td>0.463312</td>
      <td>0</td>
      <td>0</td>
      <td>0.0523934</td>
      <td>0.913718</td>
      <td>0.0685191</td>
      <td>483259</td>
      <td>238</td>
      <td>10000</td>
      <td>22994.8</td>
      <td>0.0256171</td>
      <td>0.0870134</td>
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
      <td>2000-11-08</td>
      <td>Buy Short</td>
      <td>24.747902</td>
      <td>CS</td>
      <td>NaN</td>
      <td>404</td>
      <td>NaN</td>
    </tr>
    <tr>
      <th>1</th>
      <td>2002-01-10</td>
      <td>Sell Short</td>
      <td>24.150114</td>
      <td>CS</td>
      <td>0.597788</td>
      <td>404</td>
      <td>241.506</td>
    </tr>
    <tr>
      <th>2</th>
      <td>2002-01-10</td>
      <td>Buy Long</td>
      <td>24.150114</td>
      <td>CS</td>
      <td>NaN</td>
      <td>424</td>
      <td>NaN</td>
    </tr>
    <tr>
      <th>3</th>
      <td>2002-03-01</td>
      <td>Sell Long</td>
      <td>19.280340</td>
      <td>CS</td>
      <td>-4.869774</td>
      <td>424</td>
      <td>-2064.78</td>
    </tr>
    <tr>
      <th>4</th>
      <td>2002-03-01</td>
      <td>Buy Short</td>
      <td>19.280340</td>
      <td>CS</td>
      <td>NaN</td>
      <td>424</td>
      <td>NaN</td>
    </tr>
    <tr>
      <th>5</th>
      <td>2003-05-16</td>
      <td>Sell Short</td>
      <td>15.553974</td>
      <td>CS</td>
      <td>3.726366</td>
      <td>424</td>
      <td>1579.98</td>
    </tr>
    <tr>
      <th>6</th>
      <td>2003-05-16</td>
      <td>Buy Long</td>
      <td>15.553974</td>
      <td>CS</td>
      <td>NaN</td>
      <td>627</td>
      <td>NaN</td>
    </tr>
    <tr>
      <th>7</th>
      <td>2004-05-18</td>
      <td>Sell Long</td>
      <td>19.864042</td>
      <td>CS</td>
      <td>4.310068</td>
      <td>627</td>
      <td>2702.41</td>
    </tr>
    <tr>
      <th>8</th>
      <td>2004-05-18</td>
      <td>Buy Short</td>
      <td>19.864042</td>
      <td>CS</td>
      <td>NaN</td>
      <td>627</td>
      <td>NaN</td>
    </tr>
    <tr>
      <th>9</th>
      <td>2004-11-19</td>
      <td>Sell Short</td>
      <td>23.290010</td>
      <td>CS</td>
      <td>-3.425968</td>
      <td>627</td>
      <td>-2148.08</td>
    </tr>
    <tr>
      <th>10</th>
      <td>2004-11-19</td>
      <td>Buy Long</td>
      <td>23.290010</td>
      <td>CS</td>
      <td>NaN</td>
      <td>443</td>
      <td>NaN</td>
    </tr>
    <tr>
      <th>11</th>
      <td>2006-08-15</td>
      <td>Sell Long</td>
      <td>34.777523</td>
      <td>CS</td>
      <td>11.487513</td>
      <td>443</td>
      <td>5088.97</td>
    </tr>
    <tr>
      <th>12</th>
      <td>2006-08-15</td>
      <td>Buy Short</td>
      <td>34.777523</td>
      <td>CS</td>
      <td>NaN</td>
      <td>443</td>
      <td>NaN</td>
    </tr>
    <tr>
      <th>13</th>
      <td>2006-09-27</td>
      <td>Sell Short</td>
      <td>36.907272</td>
      <td>CS</td>
      <td>-2.129749</td>
      <td>443</td>
      <td>-943.479</td>
    </tr>
    <tr>
      <th>14</th>
      <td>2006-09-27</td>
      <td>Buy Long</td>
      <td>36.907272</td>
      <td>CS</td>
      <td>NaN</td>
      <td>392</td>
      <td>NaN</td>
    </tr>
    <tr>
      <th>15</th>
      <td>2007-08-24</td>
      <td>Sell Long</td>
      <td>43.742233</td>
      <td>CS</td>
      <td>6.834961</td>
      <td>392</td>
      <td>2679.3</td>
    </tr>
    <tr>
      <th>16</th>
      <td>2007-08-24</td>
      <td>Buy Short</td>
      <td>43.742233</td>
      <td>CS</td>
      <td>NaN</td>
      <td>392</td>
      <td>NaN</td>
    </tr>
    <tr>
      <th>17</th>
      <td>2009-05-19</td>
      <td>Sell Short</td>
      <td>28.795807</td>
      <td>CS</td>
      <td>14.946426</td>
      <td>392</td>
      <td>5859</td>
    </tr>
    <tr>
      <th>18</th>
      <td>2009-05-19</td>
      <td>Buy Long</td>
      <td>28.795807</td>
      <td>CS</td>
      <td>NaN</td>
      <td>799</td>
      <td>NaN</td>
    </tr>
  </tbody>
</table>


Le dernier élément retourné est un graphique, si l'argument showplot est "True" :

```python

plt.show()

```

![png](readme_files/Figure_1.png)

Activez l'intéraction graphique pour une meilleure expérience.

