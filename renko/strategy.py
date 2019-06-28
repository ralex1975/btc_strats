from renko.renko_indicator import RenkoBars
from strategy import Strategy

class Renko(Strategy):
    params = (
        ('brick_size', 150),
    )

    def __init__(self):
        self.order   = None
        self.dataclose = self.datas[0]
        self.renko_obj = RenkoBars(brick_size=self.p.brick_size)


    def next(self):

        last = self.renko_obj[0]
        position = self.position.size

        # If current close is above the previous, we should be long
        if last > 0:
            if position < 0: # we are short, need to reverse
                self.order = self.buy()
                self.log('BUY CREATE, %.2f' % self.dataclose[0])
            elif position > 0: # already long, do nothing
                pass

            # This only runs in the beginning before we establish a position
            elif position == 0:
                self.order = self.buy()
                self.log('BUY CREATE, %.2f' % self.dataclose[0])

        # If current close is below the previous, we should be short
        elif last < 0:
            if position > 0: # we are long, need to reverse
                self.order = self.sell()
                self.log('SELL CREATE, %.2f' % self.dataclose[0])
            elif position < 0: # already short, do nothing
                pass

            # This only runs in the beginning before we establish a position
            elif position == 0:
                self.order = self.sell()
                self.log('SELL CREATE, %.2f' % self.dataclose[0])

        else:
            return