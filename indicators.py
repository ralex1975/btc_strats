import backtrader as bt
import numpy as np
from utils import stride_axis


class ALMA(bt.Indicator):
    """

    """

    lines = ('alma',)
    params = (('period', 9),
              ('sigma', 6),
              ('offset', 0.85))

    def __init__(self):
        self.addminperiod(self.p.period)

    def next(self):
        self.lines.alma[0] = self.alma(data=self.data.get(size=self.p.period), period=self.p.period, sigma=self.p.sigma,
                                       offset=self.p.offset)


    @staticmethod
    def alma(**kwargs):
        """

        :return:
        """

        data   = np.array(kwargs['df'], dtype='d')
        offset = kwargs['offset'] # 0 to 1 controls the
        period = kwargs['period'] # window period
        sigma  = kwargs['sigma'] # int value, controls

        m = np.floor(offset * (period-1))
        s = period/ sigma
        dss = 2 * (s**2)

        wtds = np.exp(-((np.arange(period)-m)**2)/dss) # Calculate weights
        windows = stride_axis(data, len(wtds)) # Calculate the arrays
        output = np.matmul(windows, wtds) / wtds.sum() # multiply the vectors by the weights divide by weights sum

        return output


class DEMA(bt.Indicator):
    """
    Calculate the double exponential moving average.
    """

    lines = ('dema',)
    params = (('first_pass', 20),
              ('second_pass', 10))


    def __init__(self):
        self.addminperiod(self.data_needed()) # need more days than just the first pass
        first_ema = bt.ind.ExponentialMovingAverage(period=self.p.first_pass)
        self.lines.dema = bt.ind.ExponentialMovingAverage(first_ema, period=self.p.second_pass)

    def data_needed(self):
        days_needed = self.p.first_pass + self.p.second_pass + 1

        return days_needed


