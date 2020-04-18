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


