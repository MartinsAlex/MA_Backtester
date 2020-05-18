

# MA_Backtester

[![Build Status](https://travis-ci.com/MartinsAlex/MA_Backtester.svg?branch=master)](https://travis-ci.com/MartinsAlex/MA_Backtester)<space><space>
[![Known Vulnerabilities](https://snyk.io/test/github/MartinsAlex/MA_Backtester/badge.svg?targetFile=requirements.txt)](https://snyk.io/test/github/MartinsAlex/MA_Backtester?targetFile=requirements.txt)<space><space>
[![Project Status: Concept – Minimal or no implementation has been done yet, or the repository is only intended to be a limited example, demo, or proof-of-concept.](https://www.repostatus.org/badges/latest/concept.svg)](https://www.repostatus.org/#concept)



# This code is still in development and docs will be available in english soon.



### A simple, but powerful, fintech module. It allows to test strategies based on moving averages crossover, on nearly :

* 100'000 stocks
* 120 crypto-currencies
* 35 currencies quoted in USD
* Numerous other assets such as indices, futures and ETFs

<p>&nbsp;</p>

> “ What has happened in the past will happen again. This is because Markets are driven by humans and human nature never changes. “
> > Jesse Livermore



<p>&nbsp;</p>

# Summary

1. [Installation](https://github.com/MartinsAlex/MA_Backtester/blob/master/README.md#installation)
1. [Utilisation](https://github.com/MartinsAlex/MA_Backtester/blob/master/README.md#utilisation)
    + Examples


&nbsp;

# Installation

```python

pip install https://github.com/MartinsAlex/MA_Backtester/archive/master.zip
    
```
#### Required modules :

- matplotlib
- pandas
- numpy
- pandas-datareader


&nbsp;

# Utilisation

Detailed documentation can be called with built-in help() function. All Yahoo and FRED forex Tickers are working. Some example list can be found in "tickerLists" folder.

&nbsp;

## Example 1 : SPDR S&P 500 Trust ETF

#### January 2018 to may 2020. Stratégie basée sur le croisement des moyennes mobiles simples de 50 et 200 jours. 
- Capital initial : 10'000 USD 
- Prise de position short et long
- Absence de frais de transactions

```python

import MA_Backtester as mb
import matplotlib.pyplot as plt


spyStrat = mb.movingAverageCrossover(["SPY"], 50, 200, "2018-01-01", "2020-05-01", 
                                   maType="simple", plot=True, shortLong="both", balance=10_000)

spyStrat.analyse()


plt.show()


```

![png](readme_files/Figure1.png)

Les différents arguments sont expliqués dans la doc. Concernant les tickers, tout ceux de Yahoo Finance peuvent être utilisés ainsi que ceux de FRED (forex).

La fonction retourne deux tables pandas et une figure matplotlib. La première table contient différentes statistiques concernant la stratégie :


```python

spyStrat.resultsTable

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
      <th>Win Rate</th>
      <th>Expectancy</th>
      <th>Total Realized Return</th>
      <th>Total Return</th>
      <th>Buy &amp; Hold Return</th>
      <th>Asset Return %</th>
      <th>Strategy Realized Return %</th>
      <th>Over/Under-performance %</th>
      <th>Asset Annualized Return %</th>
      <th>Strategy Annualized Return %</th>
      <th>Open position (price)</th>
      <th>Open Trade P/L</th>
      <th>Asset Annualized Volatility</th>
      <th>Strategy Annualized Volatility</th>
      <th>Asset Sharpe Ratio</th>
      <th>Strategy Sharpe Ratio</th>
      <th>Asset Max Drawdown</th>
      <th>Strategy Max Drawdown</th>
      <th>Market Exposure</th>
      <th>Correlation with Hold &amp; Buy</th>
      <th>Asset Daily Avg Volume</th>
      <th>Avg Holding Days</th>
      <th>Initial Capital</th>
      <th>Final Capital</th>
      <th>Used Stop-Loss</th>
      <th>Used Take-Profit</th>
      <th>Total fees payed</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>1</th>
      <td>2018-01-02</td>
      <td>2020-05-01</td>
      <td>SPY</td>
      <td>2</td>
      <td>0</td>
      <td>2</td>
      <td>-59893.4</td>
      <td>-69858.8</td>
      <td>0</td>
      <td>-17.8659</td>
      <td>-129752</td>
      <td>-214287</td>
      <td>98875.1</td>
      <td>0.0988751</td>
      <td>-0.129752</td>
      <td>-0.228627</td>
      <td>0.0413079</td>
      <td>-0.0957403</td>
      <td>-257.75</td>
      <td>-84535.1</td>
      <td>0.240043</td>
      <td>0.21896</td>
      <td>0.164623</td>
      <td>-0.479157</td>
      <td>-0.337173</td>
      <td>-0.33911</td>
      <td>0.592845</td>
      <td>0.511657</td>
      <td>9.26934e+07</td>
      <td>163</td>
      <td>1000000</td>
      <td>785713</td>
      <td>0</td>
      <td>0</td>
      <td>0</td>
    </tr>
  </tbody>
</table>

La seconde, les transactions effectuées :

```python

spyStrat.transactionTable

```
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
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>0</th>
      <td>2018-12-12</td>
      <td>Buy Short</td>
      <td>257.500000</td>
      <td>SPY</td>
      <td>NaN</td>
      <td>3883</td>
    </tr>
    <tr>
      <th>1</th>
      <td>2019-03-26</td>
      <td>Sell Short</td>
      <td>275.490936</td>
      <td>SPY</td>
      <td>-17.990936</td>
      <td>3883</td>
    </tr>
    <tr>
      <th>2</th>
      <td>2019-03-26</td>
      <td>Buy Long</td>
      <td>275.490936</td>
      <td>SPY</td>
      <td>NaN</td>
      <td>3376</td>
    </tr>
    <tr>
      <th>3</th>
      <td>2020-03-31</td>
      <td>Sell Long</td>
      <td>257.750000</td>
      <td>SPY</td>
      <td>-17.740936</td>
      <td>3376</td>
    </tr>
    <tr>
      <th>4</th>
      <td>2020-03-31</td>
      <td>Buy Short</td>
      <td>257.750000</td>
      <td>SPY</td>
      <td>NaN</td>
      <td>3376</td>
    </tr>
  </tbody>
</table>

--------

&nbsp;


## Example 2 : Goldman Sachs

#### From january 2017 to may 2020. Stratégie basée sur le croisement des moyennes mobiles pondérées de 20 et 50 jours. 
- Capital initial : 100'000 USD 
- Prise de position long only
- Stop-loss : 5 %
- Commission : 0.1 %


```python

goldmanStrat = mb.movingAverageCrossover(["gs"], 20, 50, "2017-01-01", "2020-05-01", 
                                      maType="weighted", plot=True, shortLong="long", capital=100_000,
                                     stopLoss=0.05, commission=0.001)
goldmanStrat.analyse()

plt.show()

```
![png](readme_files/Figure2.png)

```python

goldmanStrat.resultsTable

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
      <th>Win Rate</th>
      <th>Expectancy</th>
      <th>Total Realized Return</th>
      <th>Total Return</th>
      <th>Buy &amp; Hold Return</th>
      <th>Asset Return %</th>
      <th>Strategy Realized Return %</th>
      <th>Over/Under-performance %</th>
      <th>Asset Annualized Return %</th>
      <th>Strategy Annualized Return %</th>
      <th>Open position (price)</th>
      <th>Open Trade P/L</th>
      <th>Asset Annualized Volatility</th>
      <th>Strategy Annualized Volatility</th>
      <th>Asset Sharpe Ratio</th>
      <th>Strategy Sharpe Ratio</th>
      <th>Asset Max Drawdown</th>
      <th>Strategy Max Drawdown</th>
      <th>Market Exposure</th>
      <th>Correlation with Hold &amp; Buy</th>
      <th>Asset Daily Avg Volume</th>
      <th>Avg Holding Days</th>
      <th>Initial Capital</th>
      <th>Final Capital</th>
      <th>Used Stop-Loss</th>
      <th>Used Take-Profit</th>
      <th>Total fees payed</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>1</th>
      <td>2017-01-03</td>
      <td>2020-05-01</td>
      <td>GS</td>
      <td>10</td>
      <td>3</td>
      <td>7</td>
      <td>6184.15</td>
      <td>-7567.3</td>
      <td>0.3</td>
      <td>-2.46038</td>
      <td>-13423.2</td>
      <td>-12959.6</td>
      <td>-22720.7</td>
      <td>-0.227207</td>
      <td>-0.134232</td>
      <td>0.0929752</td>
      <td>-0.106191</td>
      <td>-0.13188</td>
      <td>175.98</td>
      <td>549.925</td>
      <td>0.384782</td>
      <td>0.182936</td>
      <td>-0.294783</td>
      <td>-0.336892</td>
      <td>-0.487488</td>
      <td>-0.29577</td>
      <td>0.443914</td>
      <td>0.474458</td>
      <td>3.18137e+06</td>
      <td>36</td>
      <td>100000</td>
      <td>87040.4</td>
      <td>2</td>
      <td>0</td>
      <td>1026.88</td>
    </tr>
  </tbody>
</table>

```python

goldmanStrat.transactionTable

```

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
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>0</th>
      <td>2017-06-19</td>
      <td>Buy Long</td>
      <td>215.806152</td>
      <td>GS</td>
      <td>NaN</td>
      <td>463</td>
    </tr>
    <tr>
      <th>1</th>
      <td>2017-08-24</td>
      <td>Sell Long</td>
      <td>212.809494</td>
      <td>GS</td>
      <td>-2.996658</td>
      <td>463</td>
    </tr>
    <tr>
      <th>2</th>
      <td>2017-09-19</td>
      <td>Buy Long</td>
      <td>219.205322</td>
      <td>GS</td>
      <td>NaN</td>
      <td>449</td>
    </tr>
    <tr>
      <th>3</th>
      <td>2017-11-20</td>
      <td>Sell Long</td>
      <td>228.034409</td>
      <td>GS</td>
      <td>8.829086</td>
      <td>449</td>
    </tr>
    <tr>
      <th>4</th>
      <td>2017-12-04</td>
      <td>Buy Long</td>
      <td>240.777908</td>
      <td>GS</td>
      <td>NaN</td>
      <td>425</td>
    </tr>
    <tr>
      <th>5</th>
      <td>2018-03-26</td>
      <td>Sell Long</td>
      <td>245.528625</td>
      <td>GS</td>
      <td>4.750717</td>
      <td>425</td>
    </tr>
    <tr>
      <th>6</th>
      <td>2018-07-24</td>
      <td>Buy Long</td>
      <td>228.029221</td>
      <td>GS</td>
      <td>NaN</td>
      <td>457</td>
    </tr>
    <tr>
      <th>7</th>
      <td>2018-09-14</td>
      <td>Sell Long</td>
      <td>222.344147</td>
      <td>GS</td>
      <td>-5.685074</td>
      <td>457</td>
    </tr>
    <tr>
      <th>8</th>
      <td>2018-11-09</td>
      <td>Buy Long</td>
      <td>215.952362</td>
      <td>GS</td>
      <td>NaN</td>
      <td>470</td>
    </tr>
    <tr>
      <th>9</th>
      <td>2018-11-12</td>
      <td>Sell Long</td>
      <td>199.851730</td>
      <td>GS</td>
      <td>-16.100632</td>
      <td>470</td>
    </tr>
    <tr>
      <th>10</th>
      <td>2019-01-18</td>
      <td>Buy Long</td>
      <td>197.242813</td>
      <td>GS</td>
      <td>NaN</td>
      <td>476</td>
    </tr>
    <tr>
      <th>11</th>
      <td>2019-02-08</td>
      <td>Stop-Loss Long</td>
      <td>186.657135</td>
      <td>GS</td>
      <td>-10.585678</td>
      <td>476</td>
    </tr>
    <tr>
      <th>12</th>
      <td>2019-04-05</td>
      <td>Buy Long</td>
      <td>197.882935</td>
      <td>GS</td>
      <td>NaN</td>
      <td>448</td>
    </tr>
    <tr>
      <th>13</th>
      <td>2019-05-17</td>
      <td>Sell Long</td>
      <td>193.042908</td>
      <td>GS</td>
      <td>-4.840027</td>
      <td>448</td>
    </tr>
    <tr>
      <th>14</th>
      <td>2019-06-27</td>
      <td>Buy Long</td>
      <td>195.769333</td>
      <td>GS</td>
      <td>NaN</td>
      <td>442</td>
    </tr>
    <tr>
      <th>15</th>
      <td>2019-08-14</td>
      <td>Sell Long</td>
      <td>192.076294</td>
      <td>GS</td>
      <td>-3.693039</td>
      <td>442</td>
    </tr>
    <tr>
      <th>16</th>
      <td>2019-09-12</td>
      <td>Buy Long</td>
      <td>216.191757</td>
      <td>GS</td>
      <td>NaN</td>
      <td>392</td>
    </tr>
    <tr>
      <th>17</th>
      <td>2019-09-24</td>
      <td>Stop-Loss Long</td>
      <td>205.329773</td>
      <td>GS</td>
      <td>-10.861984</td>
      <td>392</td>
    </tr>
    <tr>
      <th>18</th>
      <td>2019-10-28</td>
      <td>Buy Long</td>
      <td>215.213272</td>
      <td>GS</td>
      <td>NaN</td>
      <td>373</td>
    </tr>
    <tr>
      <th>19</th>
      <td>2020-02-18</td>
      <td>Sell Long</td>
      <td>231.792770</td>
      <td>GS</td>
      <td>16.579498</td>
      <td>373</td>
    </tr>
    <tr>
      <th>20</th>
      <td>2020-04-22</td>
      <td>Buy Long</td>
      <td>175.979996</td>
      <td>GS</td>
      <td>NaN</td>
      <td>491</td>
    </tr>
  </tbody>
</table>

--------

&nbsp;

## Example 3 : Analyse multiple crypto-currencies

#### Bitcoin, Ethereum, Litecoin, BitcoinCash and XRP. January 2018 to may 2020. Stratégie basée sur le croisement des moyennes mobiles exponentielles de 8 et 13 jours.
- Capital initial : 10'000 USD 
- Prise de position short et long
- Commission : 0.1 %

```python

cryptoStrat = mb.movingAverageCrossover(["BTC-USD", "ETH-USD", "LTC-USD", "BCH-USD", "XRP-USD"], 8, 13, "2018-01-01", "2020-05-01", 
                                   maType="exp", shortLong="both", balance=10_000, commission=0.001)

cryptoStrat.analyse()


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
      <th>Win Rate</th>
      <th>Expectancy</th>
      <th>Total Realized Return</th>
      <th>Total Return</th>
      <th>Buy &amp; Hold Return</th>
      <th>Asset Return %</th>
      <th>Strategy Realized Return %</th>
      <th>Over/Under-performance %</th>
      <th>Asset Annualized Return %</th>
      <th>Strategy Annualized Return %</th>
      <th>Open position (price)</th>
      <th>Open Trade P/L</th>
      <th>Asset Annualized Volatility</th>
      <th>Strategy Annualized Volatility</th>
      <th>Asset Sharpe Ratio</th>
      <th>Strategy Sharpe Ratio</th>
      <th>Asset Max Drawdown</th>
      <th>Strategy Max Drawdown</th>
      <th>Market Exposure</th>
      <th>Correlation with Hold &amp; Buy</th>
      <th>Asset Daily Avg Volume</th>
      <th>Avg Holding Days</th>
      <th>Initial Capital</th>
      <th>Final Capital</th>
      <th>Used Stop-Loss</th>
      <th>Used Take-Profit</th>
      <th>Total fees payed</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>1</th>
      <td>2018-01-01</td>
      <td>2020-05-01</td>
      <td>BTC-USD</td>
      <td>36</td>
      <td>12</td>
      <td>24</td>
      <td>1.05431e+06</td>
      <td>-227184</td>
      <td>0.3333</td>
      <td>299.844</td>
      <td>2.22628e+06</td>
      <td>3.38538e+06</td>
      <td>-341842</td>
      <td>-0.341842</td>
      <td>2.22628</td>
      <td>2.56812</td>
      <td>-0.16389</td>
      <td>0.699682</td>
      <td>6606.78</td>
      <td>1.16233e+06</td>
      <td>0.809079</td>
      <td>0.609549</td>
      <td>-0.222766</td>
      <td>1.03849</td>
      <td>-0.815327</td>
      <td>-0.475904</td>
      <td>0.9449</td>
      <td>0.00984759</td>
      <td>1.50842e+10</td>
      <td>22</td>
      <td>1000000</td>
      <td>4.38538e+06</td>
      <td>0</td>
      <td>0</td>
      <td>54648.1</td>
    </tr>
    <tr>
      <th>2</th>
      <td>2018-01-01</td>
      <td>2020-05-01</td>
      <td>ETH-USD</td>
      <td>85</td>
      <td>29</td>
      <td>56</td>
      <td>704959</td>
      <td>-206924</td>
      <td>0.3412</td>
      <td>131.779</td>
      <td>1.36725e+06</td>
      <td>2.50768e+06</td>
      <td>-721313</td>
      <td>-0.721313</td>
      <td>1.36725</td>
      <td>2.08856</td>
      <td>-0.421151</td>
      <td>0.459424</td>
      <td>145.219</td>
      <td>1.1428e+06</td>
      <td>1.02435</td>
      <td>0.786081</td>
      <td>-0.535348</td>
      <td>0.683427</td>
      <td>-0.939625</td>
      <td>-0.604254</td>
      <td>0.975381</td>
      <td>-0.0513255</td>
      <td>6.27227e+09</td>
      <td>16</td>
      <td>1000000</td>
      <td>3.50768e+06</td>
      <td>0</td>
      <td>0</td>
      <td>52297.3</td>
    </tr>
    <tr>
      <th>3</th>
      <td>2018-01-01</td>
      <td>2020-05-01</td>
      <td>LTC-USD</td>
      <td>122</td>
      <td>43</td>
      <td>79</td>
      <td>3.19187e+06</td>
      <td>-1.50961e+06</td>
      <td>0.3525</td>
      <td>93.7691</td>
      <td>5.87661e+06</td>
      <td>6.91407e+06</td>
      <td>-784057</td>
      <td>-0.784057</td>
      <td>5.87661</td>
      <td>6.66067</td>
      <td>-0.481006</td>
      <td>1.31594</td>
      <td>42.9372</td>
      <td>1.04434e+06</td>
      <td>1.03682</td>
      <td>0.820785</td>
      <td>-0.634306</td>
      <td>1.07973</td>
      <td>-0.92085</td>
      <td>-0.438839</td>
      <td>0.982415</td>
      <td>0.00283437</td>
      <td>2.01499e+09</td>
      <td>22</td>
      <td>1000000</td>
      <td>7.91407e+06</td>
      <td>0</td>
      <td>0</td>
      <td>150615</td>
    </tr>
    <tr>
      <th>4</th>
      <td>2018-01-01</td>
      <td>2020-05-01</td>
      <td>BCH-USD</td>
      <td>159</td>
      <td>61</td>
      <td>98</td>
      <td>2.18384e+06</td>
      <td>-1.01185e+06</td>
      <td>0.3836</td>
      <td>84.2901</td>
      <td>3.92802e+06</td>
      <td>4.37958e+06</td>
      <td>-892302</td>
      <td>-0.892302</td>
      <td>3.92802</td>
      <td>4.82033</td>
      <td>-0.614628</td>
      <td>1.00309</td>
      <td>239.769</td>
      <td>456488</td>
      <td>1.28352</td>
      <td>0.965125</td>
      <td>-0.744591</td>
      <td>0.746695</td>
      <td>-0.97328</td>
      <td>-0.540151</td>
      <td>0.982415</td>
      <td>0.0431008</td>
      <td>1.48351e+09</td>
      <td>22</td>
      <td>1000000</td>
      <td>5.37958e+06</td>
      <td>0</td>
      <td>0</td>
      <td>110203</td>
    </tr>
    <tr>
      <th>5</th>
      <td>2018-01-01</td>
      <td>2020-05-01</td>
      <td>XRP-USD</td>
      <td>191</td>
      <td>77</td>
      <td>114</td>
      <td>516900</td>
      <td>-292083</td>
      <td>0.4031</td>
      <td>70.1709</td>
      <td>922799</td>
      <td>1.46447e+06</td>
      <td>-906353</td>
      <td>-0.906353</td>
      <td>0.922799</td>
      <td>1.82915</td>
      <td>-0.637004</td>
      <td>0.344068</td>
      <td>0.174563</td>
      <td>543593</td>
      <td>1.04865</td>
      <td>0.762404</td>
      <td>-0.968472</td>
      <td>0.506076</td>
      <td>-0.958661</td>
      <td>-0.532172</td>
      <td>0.946073</td>
      <td>0.0632268</td>
      <td>1.23956e+09</td>
      <td>24</td>
      <td>1000000</td>
      <td>2.46447e+06</td>
      <td>0</td>
      <td>0</td>
      <td>42213.5</td>
    </tr>
  </tbody>
</table>


## Then find the moving averages allocation that would have produced the best performance :



```python

cryptoStrat.optimize("Over/Under-performance %", fastMaRange= [8, 10],  slowMaRange = [13, 15], type="max")

```
The function returns a pandas dataFrame with all the combinaison tested :

<table border="1" class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th></th>
      <th>fastMA</th>
      <th>slowMA</th>
      <th>Over/Under-performance %</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>0</th>
      <td>8.0</td>
      <td>13.0</td>
      <td>3.593365</td>
    </tr>
    <tr>
      <th>1</th>
      <td>8.0</td>
      <td>14.0</td>
      <td>3.631902</td>
    </tr>
    <tr>
      <th>2</th>
      <td>8.0</td>
      <td>15.0</td>
      <td>3.447292</td>
    </tr>
    <tr>
      <th>3</th>
      <td>9.0</td>
      <td>13.0</td>
      <td>3.913140</td>
    </tr>
    <tr>
      <th>4</th>
      <td>9.0</td>
      <td>14.0</td>
      <td>4.275443</td>
    </tr>
    <tr>
      <th>5</th>
      <td>9.0</td>
      <td>15.0</td>
      <td>3.075884</td>
    </tr>
    <tr>
      <th>6</th>
      <td>10.0</td>
      <td>13.0</td>
      <td>3.583561</td>
    </tr>
    <tr>
      <th>7</th>
      <td>10.0</td>
      <td>14.0</td>
      <td>2.452192</td>
    </tr>
    <tr>
      <th>8</th>
      <td>10.0</td>
      <td>15.0</td>
      <td>1.926440</td>
    </tr>
  </tbody>
</table>


## Or would have been the less risky :

```python

cryptoStrat.optimize("Strategy Annualized Volatility", fastMaRange= [8, 10],  slowMaRange = [13, 15], type="min")

```


<table border="1" class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th></th>
      <th>fastMA</th>
      <th>slowMA</th>
      <th>Strategy Annualized Volatility</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>0</th>
      <td>8.0</td>
      <td>13.0</td>
      <td>0.788789</td>
    </tr>
    <tr>
      <th>1</th>
      <td>8.0</td>
      <td>14.0</td>
      <td>0.788227</td>
    </tr>
    <tr>
      <th>2</th>
      <td>8.0</td>
      <td>15.0</td>
      <td>0.782712</td>
    </tr>
    <tr>
      <th>3</th>
      <td>9.0</td>
      <td>13.0</td>
      <td>0.788172</td>
    </tr>
    <tr>
      <th>4</th>
      <td>9.0</td>
      <td>14.0</td>
      <td>0.786504</td>
    </tr>
    <tr>
      <th>5</th>
      <td>9.0</td>
      <td>15.0</td>
      <td>0.786519</td>
    </tr>
    <tr>
      <th>6</th>
      <td>10.0</td>
      <td>13.0</td>
      <td>0.808755</td>
    </tr>
    <tr>
      <th>7</th>
      <td>10.0</td>
      <td>14.0</td>
      <td>0.810902</td>
    </tr>
    <tr>
      <th>8</th>
      <td>10.0</td>
      <td>15.0</td>
      <td>0.785784</td>
    </tr>
  </tbody>
</table>

--------

&nbsp;




