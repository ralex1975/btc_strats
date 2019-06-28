import backtrader as bt

class EMACross(bt.Strategy):
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
        self.slowma  = self.p._ema(period=self.p.slow)
        self.filterma = self.p._ema(period=150)
        self.atr = bt.ind.AverageTrueRange(period=14)
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

        # Long signal
        if self.signal > 0:
            if self.getposition().size > 0: # if we are already long, return
                return
            if self.fastma > self.filterma: # otherwise if the MA is above our filter MA, take a position
                stop_distance = 8 * self.atr[0] # Calc stoploss distance
                self.order = self.buy_bracket(exectype=bt.Order.Market, stopexec=bt.Order.StopTrail,
                                                stopargs={'trailamount':stop_distance}, limitexec=None)
                self.log('BUY CREATE, %.2f' % self.dataclose[0])
            elif self.getposition().size < 0: # If we are short, we go neutral
                open_orders = self.broker.get_orders_open()
                for order in open_orders:
                    self.cancel(order)
                    self.log('Cancelling Order')
                self.order = self.close()
                self.log('BUY TO CLOSE, %.2f' % self.dataclose[0])

        # Short signal
        elif self.signal < 0:
            if self.getposition().size < 0: # if we are already short, return
                return
            if self.fastma < self.filterma: # otherwise if the MA is below our filter MA, take a position
                stop_distance = 8 * self.atr[0] # Calc stoploss distance
                self.order = self.sell_bracket(exectype=bt.Order.Market, stopexec=bt.Order.StopTrail,
                                                stopargs={'trailamount':stop_distance}, limitexec=None)
                self.log('SELL CREATE, %.2f' % self.dataclose[0])
            elif self.getposition().size > 0: # if we are long, we go neutral
                open_orders = self.broker.get_orders_open()
                for order in open_orders:
                    self.cancel(order)
                    self.log('Cancelling Order')
                self.order = self.close()
                self.log('SELL TO CLOSE, %.2f' % self.dataclose[0])

        else:
            return



