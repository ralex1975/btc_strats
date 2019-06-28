import backtrader as bt
from donchian.strategy import DonchianCross
from sizers import AllInSizer
from cerebro import Cerebro
from utils import unpickle


price = unpickle('df/btc_1hr')

# Make df object - we only have a "close" in column 0
data = bt.feeds.PandasData(dataname=price, open=0, high=1, low=2, close=3, volume=4, openinterest=None)

# Initialize Cerebro Engine and add strategy
cerebro = Cerebro(data=data, sizer=AllInSizer)
cerebro.addstrategy(strategy=DonchianCross)

# Run the Strategy and Plot the results
cerebro.Run(cheat_on_open=True)
cerebro.Plot()
cerebro.PlotEquity()
transactions = cerebro.transactions
positions = cerebro.positions