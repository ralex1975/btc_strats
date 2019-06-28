# this is analysis after the program has been run and the strategy object is loaded into the environment

strat = cerebro.strat_list[0]

fastma_line = strat.fastma.array
slowma_line = strat.slowma.array
close_line  = strat.data.array
open_line   = strat.data.l.open.array
signals = strat.signal.array
equity_line = strat.stats.broker.value.array
import pandas as pd

s1 = pd.Series(fastma_line)
s2 = pd.Series(slowma_line)
s3 = pd.Series(close_line)
s6 = pd.Series(open_line)
s4 = pd.Series(signals)
s5 = pd.Series(equity_line)
s = pd.concat([s1,s2,s4,s3,s6,s5], axis=1)
s = s.iloc[0:25381,:]
s.index = price.index
s.columns = ['fast', 'slow', 'signal', 'close', 'open', 'equity']

import matplotlib.pyplot as plt
plt.switch_backend('TkAgg')
plt.plot(fastma_line[:800], label='fast')
plt.plot(slowma_line[:800], label='slow')
plt.plot(close_line[:800], label='close')
#s[['fast', 'slow', 'close']].loc[:"2017-08-27"].plot()
plt.legend()
plt.show()