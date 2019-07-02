import os
os.environ["DISPLAY"] = ':0' # needed to make sure ffn doesn't set the display which breaks
import ffn.core as ffn
import pandas as pd
import numpy as np
from performance_functions import gain_loss_ratio, sterling_ratio, stability_of_timeseries, tail_ratio


class Performance:
    """ This class is mostly just a base class but can also be used during a single run to calculate and plot the
    performance of strategy"""

    def __init__(self, strats):
        self.strats = strats

        # If there is more than 1 strategy we extract them, for some reason is a list of lists not list of strats
        if len(self.strats) > 1:
            self.strats = [strat[0] for strat in self.strats]

        metrics = ['Total Return', 'Annual Return', 'Standard Deviation', 'Sharpe', 'Calmar', 'Ulcer',
                   'Sterling', 'Max Drawdown', 'Max Drawdown Len', 'Avg Drawdown', 'Avg Drawdown Len', 'Days Pos',
                   'Num Trades', 'Win Pct', 'Profit Factor', 'R^2', 'Tail Ratio', 'Gain Loss']

        self.table = pd.DataFrame(index=metrics)
        self.performance_dict = {metric : [] for metric in metrics} # Dictionary of lists used for plotting


    def run(self):
        for strat in self.strats:
            self.record_param_vals(strat)
            self.calc_performance(strat)

    def record_param_vals(self, strat):
        pass

    def calc_performance(self, strat):
        pyfoliozer = strat.analyzers.getbyname('pyfolio')
        rets, _, _, _ = pyfoliozer.get_pf_items()

        analyzer = strat.analyzers.getbyname('tradeanalyzer').get_analysis()

        # Create the equity series
        equity_series = rets + 1
        equity = equity_series.cumprod()

        # Total Return
        total_return = (equity.tail(1) - 1)[0]
        self.performance_dict['Total Return'].append(total_return)

        # Annualized Return
        cagr = ffn.calc_cagr(equity)
        self.performance_dict['Annual Return'].append(cagr)

        # Standard Deviation
        sd = np.std(rets) * np.sqrt(252) # Daily SD
        self.performance_dict['Standard Deviation'].append(sd)

        # Sharpe
        sharpe = ffn.calc_sharpe(rets, nperiods=252)
        self.performance_dict['Sharpe'].append(sharpe)

        # Calmar
        calmar = ffn.calc_calmar_ratio(equity)
        self.performance_dict['Sharpe'].append(calmar)

        # Ulcer
        ulcer = ffn.to_ulcer_index(equity)
        self.performance_dict['Ulcer'].append(ulcer)

        # Sterling
        sterling = sterling_ratio(equity)
        self.performance_dict['Sterling'].append(sterling)

        # Max Drawdown
        drawdown_series = ffn.to_drawdown_series(equity)
        max_drawdown = drawdown_series.min()
        self.performance_dict['Max Drawdown'].append(max_drawdown)

        # Drawdown Length
        drawdowns = ffn.drawdown_details(drawdown_series)
        drawdown_length = drawdowns.Length.max()
        self.performance_dict['Max Drawdown Len'].append(drawdown_length)

        # Avg Drawdown
        avg_drawdown = drawdowns['drawdown'].mean()
        self.performance_dict['Avg Drawdown'].append(avg_drawdown)

        # Avg Drawdown Len
        avg_len = drawdowns['Length'].mean()
        self.performance_dict['Avg Drawdown Len'].append(avg_len)

        # Days Positive
        days_pos = len(rets[rets > 0]) / len(rets)
        self.performance_dict['Days Pos'].append(days_pos)

        # Number of Trades
        num_trades = analyzer['total']['total']
        self.performance_dict['Num Trades'].append(num_trades)

        # Win Pct
        win_pct_ratio = analyzer.won.total / num_trades
        self.performance_dict['Win Pct'].append(win_pct_ratio)

        # Profit Factor
        avg_win_loss_ratio = analyzer.won.pnl.average / abs(analyzer.lost.pnl.average)
        self.performance_dict['Profit Factor'].append(avg_win_loss_ratio)

        # R^2
        r2 = stability_of_timeseries(rets)
        self.performance_dict['R^2'].append(r2)

        # Tail Ratio
        tr = tail_ratio(rets)
        self.performance_dict['Tail Ratio'].append(tr)

        # Gain Loss
        gl = gain_loss_ratio(rets)
        self.performance_dict['Gain Loss'].append(gl)

        # Add to the Table
        colname = self.make_colname()
        self.table.insert(loc=0, value=[total_return, cagr, sd, sharpe, calmar, ulcer, sterling, max_drawdown,
                                        drawdown_length, avg_drawdown, avg_len, days_pos, num_trades, win_pct_ratio,
                                        avg_win_loss_ratio, r2, tr, gl], column=colname)

    def make_colname(self):
        return "Strat"

    def plot(self):
        pass


class SingleParamPerformance(Performance):
    """ This class can be used during a single parameter optimization to calculate and plot the performance of each
    strategy"""

    def __init__(self, cerebro):
        Performance.__init__(self, cerebro)

        self.param_names = self.strats[0].params._gettuple()
        self.param_name1 = self.param_names[0][0]
        self.param1 = [] # list to hold the param values


    def record_param_vals(self, strat):
        param_value1 = eval("strat.params." + self.param_name1)
        self.param1.append(param_value1)  # add to list

    def make_colname(self):
        return str(self.param1[-1])

    def plot(self):
        pass


class TwoParamPerformance(SingleParamPerformance):
    """ This class can be used during a two parameter optimization to calculate and plot the performance of each
    strategy - The two parameters you want to record must be passed to the strategy first. """

    def __init__(self, cerebro):
        SingleParamPerformance.__init__(self, cerebro)

        self.param_name2 = self.param_names[1][0]
        self.param2 = []  # list to hold the param values


    def record_param_vals(self, strat):

        # Get the param values and add to list
        param_value1 = eval("strat.params." + self.param_name1)
        param_value2 = eval("strat.params." + self.param_name2)
        self.param1.append(param_value1)  # add to list
        self.param2.append(param_value2)  # add to list

    def make_colname(self):
        name= str(self.param1[-1]) + str(self.param2[-1])

        return name

    def plot(self, metric:str):
        pass

    def plot_all(self):
        pass
