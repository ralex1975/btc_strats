import backtrader as bt

class DonchianCross(bt.Strategy):
    params = (
        # period for long signal
        ('longlookback', 150),
        # period for the short
        ('shortlookback', 150),
        # period for the Average True Range
        ('atrwindow', 14),
        # multiplier for ATR
        ('atrmultiplier', 1.8)
    )

    def __init__(self):
        self.order   = None
        self.atr     = bt.ind.AverageTrueRange(period=self.p.atrwindow)
        self.min     = bt.ind.Lowest(period=self.p.longlookback)
        self.max     = bt.ind.Highest(period=self.p.shortlookback)
        self.dataclose = self.datas[0]

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

        # Check if we have a position, if we do, skip this iteration
        if self.position:
            return

        # Find the recent extremes
        last = self.data[0]

        # If the last price is also the max, go long
        if last == self.max:
            stop_distance = self.p.atrmultiplier * self.atr[0]
            self.order = self.buy()
            self.sell(exectype=bt.Order.StopTrail, trailamount=stop_distance)

            self.log('BUY CREATE, %.2f' % self.dataclose[0])

        # Else if the last price is also the minimum, go short
        elif last == self.min:
            stop_distance = self.p.atrmultiplier * self.atr[0]
            self.order = self.sell()
            self.buy(exectype=bt.Order.StopTrail, trailamount=stop_distance)

            self.log('SELL CREATE, %.2f' % self.dataclose[0])

        else:
            return
