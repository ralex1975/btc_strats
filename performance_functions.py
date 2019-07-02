import numpy as np
import ffn.core as ffn
from scipy import stats

def lpm(returns, order=2):
    """
    Calculate the Lower Partial Moment of the returns ie "Downside Risk"

    :param returns:
    :param order: Magnitude to exponentiate the series
    :return:
    """

    calc_lower_diff = 0 - returns
    clip_lower_diff = calc_lower_diff.clip(lower=0)
    calc_lpm = np.sum(clip_lower_diff ** order) / len(returns)

    return calc_lpm

def hpm(returns, order=2):
    """
    Calculate the Higher Partial Moment of the returns

    :param returns:
    :param order: Magnitude to exponentiate the series
    :return:
    """

    clip_upper_diff = returns.clip(lower=0)
    calc_hpm = np.sum(clip_upper_diff ** order) / len(returns)

    return calc_hpm

def gain_loss_ratio(returns):
    """

    :param returns:
    :return:
    """

    numer = hpm(returns, order=1)
    denom = lpm(returns, order = 1)
    ratio = numer / denom

    return ratio

def sterling_ratio(prices):
    """

    :param prices:
    :return:
    """

    returns = ffn.to_returns(prices)
    mean_rets = returns.mean()

    drawdowns  = ffn.to_drawdown_series(prices)
    average_dd = drawdowns.mean()
    ratio = mean_rets / abs(average_dd)

    return ratio

def stability_of_timeseries(returns):
    """Determines R-squared of a linear fit to the cumulative
    log returns. Computes an ordinary least squares linear fit,
    and returns R-squared.
   """

    def linregress(cum_returns):
        regress = stats.linregress(np.arange(len(cum_returns)), cum_returns)
        r2 = regress[2] ** 2
        return r2

    cum_prod = (1 + returns).cumprod()
    result = linregress(cum_prod)

    return result


def tail_ratio(returns):
    """
    Determines the ratio between the right (95%) and left tail (5%).
    """

    right = returns.quantile(q=0.95)
    left  = returns.quantile(q=0.05)
    ratio = right / abs(left)

    return  ratio

def hld(prices):
    """
    Compute the high/low differential score

    :param prices:
    :return:
    """

    # Get last price
    last = prices.tail(1)
    stand_dev = prices.std()

    # Get high price and calculate ratio
    high = prices.max()
    high_ratio = high / last
    high_diff = high_ratio / stand_dev

    # Get low price and calculate ratio
    low = prices.min()
    low_ratio = low / last
    low_diff = low_ratio / stand_dev

    hld_ratio = (low_diff - high_diff) / 100

    return hld_ratio

def smaRatio(prices):
    """
    Calculate the ratio of the current price to the mean price over the period (Simple Moving Average)

    :param prices:
    :return:
    """

    last = prices.iloc[-1,:]
    average = prices.mean()

    ratio = (last / average) - 1

    return ratio