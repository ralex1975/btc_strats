import backtrader as bt
from data.get_data import Binance
from alma_cross.strategy import ALMACross
from sizers import AllInSizer
from cerebro import Cerebro

# Get BTC Data from Binance API
binance = Binance()
price = binance.getPrice(symbol='BTCUSDT', interval='30MINUTE', nWeeks=104)

# Make df object - we only have a "close" in column 0
data = bt.feeds.PandasData(dataname=price, open=0, high=1, low=2, close=3, volume=4, openinterest=None)

# Initialize Cerebro Engine and add strategy
cerebro = Cerebro(data=data, sizer=AllInSizer)
cerebro.addstrategy(strategy=ALMACross, fast=25, slow=50)

# Run the Strategy and Plot the results
cerebro.Run(cheat_on_open=True)
transactions = cerebro.transactions
positions = cerebro.positions
returns = cerebro.returns
cerebro.Plot()
cerebro.PlotEquity()

###### Run Optimization ######
# Initialize Cerebro Engine and add strategy
cerebro = Cerebro(data=data, sizer=AllInSizer)
cerebro.optstrategy(strategy=ALMACross, fast=range(5, 16), slow=range(16, 36))
cerebro.Run(cheat_on_close=True)
results1 = cerebro.AnalyzeResults(plot=False)

# Initialize Cerebro Engine and add strategy
cerebro = Cerebro(data=data, sizer=AllInSizer)
cerebro.optstrategy(strategy=ALMACross, fast=range(5, 36), slow=range(36, 101))
cerebro.Run()
results2 = cerebro.AnalyzeResults(plot=False)

# Combine the results and plot
fast1 = results1[0]
fast2 = results2[0]
fast = fast1 + fast2

slow1 = results1[1]
slow2 = results2[1]
slow = slow1 + slow2

dict1 = results1[2]
dict2 = results2[2]
new_dict = {}
for dct in dict1:
    new_dict[dct] = dict1[dct] + dict2[dct]

import plotly.graph_objs as go
import plotly

# Else plot all of the heatmaps
for performance_list in new_dict:
    if performance_list in ["draw_length"]:
        reversescale = True
    else:
        reversescale = False

    # Create plotly graph object
    trace = go.Heatmap(x=slow, y=fast, z=new_dict[performance_list], zsmooth=None,
                       connectgaps=True,
                       colorscale='Viridis', reversescale=reversescale,
                       colorbar=dict(thickness=60, tickfont=dict(
                           size=18)))

    # Stylize the layout
    layout = dict(xaxis=dict(range=[min(slow), max(slow)], title='slow', tickfont=dict(
        size=25)),
                  yaxis=dict(range=[min(fast), max(fast)], title='fast', tickfont=dict(
                      size=25)),
                  title=str(performance_list), width=3000, height=2100, titlefont=dict(size=40))

    data = [trace]
    figure = dict(data=data, layout=layout)
    plotly.offline.plot(figure, image='png', filename=str(performance_list) + 'Jurik' '.html')  # todo try image='png'
