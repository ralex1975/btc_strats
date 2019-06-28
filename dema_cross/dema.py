import backtrader as bt
from data.get_data import Binance
from dema_cross.strategy import DEMACross
from sizers import AllInSizer
from cerebro import Cerebro
import pickle

# Get prices from pickle or use the api
try:
    infile = open('btc_30min', 'rb')
    price = pickle.load(infile)
    infile.close()
except:
    binance = Binance()
    price  = binance.getPrice(nWeeks=104)


# Make df object - we only have a "close" in column 0
data = bt.feeds.PandasData(dataname=price, open=0, high=1, low=2, close=3, volume=4, openinterest=None)

# Initialize Cerebro Engine and add strategy
cerebro = Cerebro(data=data, sizer=AllInSizer)
cerebro.addstrategy(strategy=DEMACross, fast=25, slow=50)

# Run the Strategy and Plot the results
cerebro.Run(cheat_on_close=True)
cerebro.Plot()
cerebro.PlotEquity()