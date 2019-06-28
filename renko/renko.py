import backtrader as bt
from renko.strategy import Renko
from sizers import AllInSizer
from cerebro import Cerebro
from utils import unpickle
from candlestick_chart import candlestick_chart

prices = unpickle('data/test_data/btc_daily')
data = bt.feeds.PandasData(dataname=prices, open=0, high=1, low=2, close=3, openinterest=None)

# Initialize Cerebro Engine and add strategy
cerebro = Cerebro(data=data, sizer=AllInSizer)
cerebro.addstrategy(strategy=Renko, brick_size=350)
#cerebro.optstrategy(strategy=Renko, brick_size=range(50, 1050, 50))

# Run the Strategy and Plot the results
cerebro.Run(cheat_on_open=True)

import pandas as pd
strats = cerebro.strat_list
df = pd.DataFrame()
for strat in strats:
    brick_size = strat[0].params.brick_size
    pyfoliozer = strat[0].analyzers.pyfolio
    rets, positions, transactions, gross_lev = pyfoliozer.get_pf_items()
    df[str(brick_size)] = rets

cum_returns = (df + 1 ).cumprod()
cum_returns.plot.bar()




cerebro.Plot()
cerebro.PlotEquity()
trades = cerebro.strat_list[0].analyzers.getbyname('tradeanalyzer')
trades1 = trades.get_analysis()
#cerebro.Plot()

transactions = cerebro.transactions
positions = cerebro.positions
equity = cerebro.equity[:-1]
equity.plot()
equity.plot(logy=True)
import matplotlib.pyplot as plt
plt.show()