import backtrader as bt
from indicators import DEMA

class DEMACross(bt.Strategy):
    params = (
        # period for the fast Moving Average
        ('fast', 11),
        # period for the slow moving average
        ('slow', 25),
        # moving average to use
        ('_ema', bt.ind.ExponentialMovingAverage)
    )

    def __init__(self):
        self.dataclose = self.datas[0]
        self.fastma  = self.p._ema(period=self.p.fast)
        self.slowma  = DEMA()
        self.signal  = bt.ind.CrossOver(self.fastma, self.slowma)
        self.order   = None


    def log(self, txt, dt=None):
        dt = dt or self.datas[0].datetime.date(0)
        print('%s, %s' % (dt.isoformat(), txt))

    def notify_order(self, order):
        if order.status in [order.Submitted, order.Accepted]:
            return

        if order.status in [order.Completed]:
            if order.isbuy():
                self.log('BUY EXECUTED, %.2f' % order.executed.price)
            elif order.issell():
                self.log('SELL EXECUTED, %.2f' % order.executed.price)

        elif order.status in [order.Canceled, order.Margin, order.Rejected]:
            self.log('Order Cancelled/Margin/Rejected')

        self.order = None

    def next(self):
        self.log('Close, %.2f' % self.dataclose[0])

        if self.signal > 0:
            self.order = self.buy()
            self.log('BUY CREATE, %.2f' % self.dataclose[0])

        elif self.signal < 0:
            self.order = self.sell()
            self.log('SELL CREATE, %.2f' % self.dataclose[0])

        else:
            return



