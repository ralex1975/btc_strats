import backtrader as bt
import ffn
import plotly
import plotly.graph_objs as go
import warnings

class Cerebro(bt.Cerebro):

    def __init__(self, data, startcash=10000, sizer=None, margin=2000, commission=0):

        super().__init__()
        self.adddata(data)
        self.broker.set_cash(startcash)
        self.broker.setcommission(margin=margin, commission=commission) # allows for leverage
        self.addobserver(bt.observers.DrawDown)
        self.addanalyzer(bt.analyzers.PyFolio)
        self.addanalyzer(bt.analyzers.TradeAnalyzer)
        self.addanalyzer(bt.analyzers.TimeReturn)
        self.returns = None
        self.equity  = None
        self.positions = None
        self.transactions = None
        self.gross_lev = None
        self.strat_list = None

        if sizer:
            self.addsizer(sizer)

    def Run(self, **kwargs):
        """
        Run the strategy
        """

        self.strat_list = self.run(maxcpus=7, **kwargs) # run the strategy

        if len(self.strat_list) != 1: # if there are more than 1 strat, we save analysis for later
            return

        # Access the pyfolio analyzer
        pyfoliozer = self.strat_list[0].analyzers.getbyname('pyfolio')
        self.returns, self.positions, self.transactions, self.gross_lev = pyfoliozer.get_pf_items()


        # Create the equity series
        equity_series = self.returns + 1
        self.equity = equity_series.cumprod()

        return

    def Plot(self, **kwargs):
        """
        Plot the results, using kwargs that were causing issues
        """

        #import matplotlib.pyplot as plt
        #plt.switch_backend('tkagg')
        self.plot(volume = False, voloverlay = False, **kwargs)

    def PlotEquity(self):
        """
        Plot the equity series for the backtest result
        """

        import matplotlib.pyplot as plt
        #plt.switch_backend('module://backend_interagg')
        plt.switch_backend('TkAgg')
        plt.plot(self.equity)
        plt.show()

    def AnalyzeResults(self, plot=True, *args):
        """
        Applies only to optimized strategies where there are more than 1 strategy result
        """

        # Initialize lists and dictionary to hold our results
        first_param = []
        second_param = []

        performance_dict = {
            "returns" : [],
            "num_transactions" : [],
            "max_drawdown": [],
            "sharpe": [],
            "days_pos": [],
            "calmar": [],
            "drawdown_len": [],
            "win_pct": [],
            "profit_factor": []
        }

        if args: # option to pass in the parameter names use for matching
            param_name1 = args[0]
            param_name2 = args[1]
        else: # find the parameters and use those
            # Get parameter names and assign them
            param_names = self.strat_list[0][0].params._gettuple()

            if len(param_names) > 2:
                warnings.warn("There are more than two keyward arguments supplied to the dictionary, make sure that "
                              "the two parameters you wish to graph are the first two parameters supplied to the "
                              "strategy, otherwise pass in a list of string param names")
            param_name1 = param_names[0][0]
            param_name2 = param_names[1][0]

        for strat in self.strat_list:

            # Get the strategy from the list and append the lists
            strat0 = strat[0]
            param_value1 = eval("strat0.params." + param_name1)
            param_value2 = eval("strat0.params." + param_name2)
            first_param.append(param_value1) # add to list
            second_param.append(param_value2)  # add to list

            # Get pyfolio analyzer elements
            pyfoliozer = strat0.analyzers.getbyname('pyfolio')
            rets, positions, transactions, gross_lev = pyfoliozer.get_pf_items()

            # Calculate cumulative return and add to list
            cum_returns = rets + 1
            total_return_series = cum_returns.cumprod()
            tr_tail = total_return_series.tail(1) - 1
            performance_dict['returns'].append(tr_tail[0])

            # Sharpe Ratio
            sharpe_ratio = ffn.core.calc_sharpe(rets)
            performance_dict['sharpe'].append(sharpe_ratio)

            # Calmar Ratio
            calmar_ratio = ffn.core.calc_calmar_ratio(total_return_series)
            performance_dict['calmar'].append(calmar_ratio)

            # Percent of trading days positive
            days_pos_ratio = sum(rets >= 0) / len(rets)
            performance_dict['days_pos'].append(days_pos_ratio)

            # Max Drawdown
            drawdown_series = ffn.core.to_drawdown_series(total_return_series)
            max_drawdown = drawdown_series.min()
            performance_dict['max_drawdown'].append(max_drawdown)

            # Max Drawdown Length
            drawdowns = ffn.core.drawdown_details(drawdown_series)
            drawdown_length = drawdowns.Length.max()
            performance_dict['drawdown_len'].append(drawdown_length)

            # Get trades analyzer
            trades = strat0.analyzers.getbyname('tradeanalyzer').rets

            # Get number of trades
            num_trades = trades.total.total
            performance_dict['num_transactions'].append(num_trades)

            # Win / Loss Ratio
            win_pct_ratio = trades.won.total / num_trades
            performance_dict['win_pct'].append(win_pct_ratio)

            # Profit Factor
            avg_win_loss_ratio = trades.won.pnl.average / abs(trades.lost.pnl.average)
            performance_dict['profit_factor'].append(avg_win_loss_ratio)

        if not plot:
            return first_param, second_param, performance_dict

        # Else plot all of the heatmaps
        for performance_list in performance_dict:
            if performance_list in ["draw_length"]:
                reversescale = True
            else:
                reversescale = False

            # Create plotly graph object
            trace = go.Heatmap(x=first_param, y=second_param, z=performance_dict[performance_list], zsmooth=None,
                               connectgaps=True,
                               colorscale='Viridis', reversescale=reversescale,
                               colorbar=dict(thickness=60, tickfont=dict(
                                   size=18)))

            # Stylize the layout
            layout = dict(xaxis=dict(range=[min(first_param), max(first_param)], title=param_name1, tickfont=dict(
                            size=25)),
                          yaxis=dict(range=[min(second_param), max(second_param)], title=param_name2, tickfont=dict(
                              size=25)),
                          title=str(performance_list), width=3000, height=2100, titlefont=dict(size=40))

            data = [trace]
            figure = dict(data=data, layout=layout)
            stratname = self.strat_list[0].__class__.__name__
            plotly.offline.plot(figure, filename=str(performance_list) + stratname + '.html', image='png')



