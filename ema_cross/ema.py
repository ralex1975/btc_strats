import backtrader as bt
from ema_cross.strategy import EMACross
from sizers import AllInSizer
from cerebro import Cerebro
from datetime import datetime
from utils import unpickle

# Get prices from pickle or use the api
price = unpickle('data/test_data/btc_30min')

# Make df object - we only have a "close" in column 0
data = bt.feeds.PandasData(dataname=price, open=0, high=1, low=2, close=3, volume=4, openinterest=None)

# Initialize Cerebro Engine and add strategy
cerebro = Cerebro(data=data, sizer=AllInSizer)
cerebro.addstrategy(strategy=EMACross, fast=25, slow=50)

# Run the Strategy and Plot the results
cerebro.Run(cheat_on_close=True)
cerebro.Plot(start=datetime.strptime('2018-06-01', '%Y-%m-%d'), end=datetime.strptime('2018-10-31', '%Y-%m-%d'))
cerebro.PlotEquity()

import matplotlib.pyplot as plt
plt.show()

equity = cerebro.equity
equity.index[0]
equity.plot()
plt.show()