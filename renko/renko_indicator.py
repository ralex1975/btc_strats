import pandas as pd
from candlestick_chart import candlestick_chart
import numpy as np
from utils import unpickle
import backtrader as bt
import talib


class RenkoBars(bt.Indicator):
    lines = ('renko',)
    plotinfo = dict(subplot=True)

    def __init__(self, brick_size):
        bt.Indicator.__init__(self)

        self.dataclose = self.datas[0].close
        self.brick_size = brick_size
        self.uptrend = True
        self.bricks = []
        #self.dates = []
        self.direction = []
        self.current_mid_price = self.dataclose[0]
        self.bricks.append(self.current_mid_price)

        # Initial threshold values only, later is set by the calc_.. function
        self.upper_threshold = self.current_mid_price + self.brick_size
        self.lower_threshold = self.current_mid_price - self.brick_size


    def next(self):

        close = self.dataclose[0]

        if close > self.upper_threshold:
            if self.uptrend:
                self.lines.renko[0] = 1
            else:
                self.lines.renko[0] = 1# -1

            dif = int((close - self.upper_threshold) / self.brick_size)
            for d in range(dif + 1):  # if price moved more than one brick, +1 bc range doesnt print range(0)
                self.bricks.append(self.upper_threshold)
                self.current_mid_price = self.upper_threshold
                self.uptrend = True  # needs to be in between calcs
                self.upper_threshold = self.calc_upper_threshold()
                self.lower_threshold = self.calc_lower_threshold()

        elif close < self.lower_threshold:
            if not self.uptrend: # todo changed the signs below to test for trade entry in strategy (logic was wrong)
                self.lines.renko[0] = -1 #1
            else:
                self.lines.renko[0] = -1

            dif = int(abs(close - self.lower_threshold) / self.brick_size)
            for d in range(dif + 1):  # if price moved more than one brick, +1 bc range doesnt print range(0)
                self.bricks.append(self.lower_threshold)
                self.current_mid_price = self.lower_threshold
                self.uptrend = False  # needs to be in between calcs
                self.lower_threshold = self.calc_lower_threshold()
                self.upper_threshold = self.calc_upper_threshold()

        else:
            self.lines.renko[0] = 0


    def run(self):
        self.find_bricks()
        df = self.create_df()
        score = self.evaluate()

        return df, score

    def find_bricks(self):
        """
        Recursively loop through the close df and find Renko bars.

        :return:
        """

        # Initialize the starting point of the series
        self.current_mid_price = float(self.df['close'].head(1))
        self.bricks.append(self.current_mid_price) # start the series
        self.dates.append(self.df.index[0])
        self.direction.append(0)

        # Initial threshold values only, later is set by the calc_.. function
        upper_threshold = self.current_mid_price + self.brick_size
        lower_threshold = self.current_mid_price - self.brick_size

        for i in range(len(self.df)):
            #high = self.df['high'][i]
            #low  = self.df['low'][i]
            high = self.df['close'][i]
            low = self.df['close'][i]

            if high > upper_threshold:
                if self.uptrend:
                    self.direction.append(1) # continuation # fucks up on first bar todo
                else:
                    self.direction.append(-1) # reversal

                dif = int((high-upper_threshold) / self.brick_size)
                for d in range(dif + 1): # if price moved more than one brick, +1 bc range doesnt print range(0)
                    self.bricks.append(upper_threshold)
                    self.dates.append(self.df.index[i])
                    self.current_mid_price = upper_threshold
                    self.uptrend = True  # needs to be in between calcs
                    upper_threshold = self.calc_upper_threshold()
                    lower_threshold = self.calc_lower_threshold()


            if low < lower_threshold:
                if not self.uptrend:
                    self.direction.append(1) # continuation
                else:
                    self.direction.append(-1) # reversal

                dif = int(abs(low - lower_threshold) / self.brick_size)
                for d in range(dif + 1):  # if price moved more than one brick, +1 bc range doesnt print range(0)
                    self.bricks.append(lower_threshold)
                    self.dates.append(self.df.index[i])
                    self.current_mid_price = lower_threshold
                    self.uptrend = False # needs to be in between calcs
                    lower_threshold = self.calc_lower_threshold()
                    upper_threshold = self.calc_upper_threshold()

            else:
                self.direction.append(0)

        return


    def calc_upper_threshold(self):
        if self.uptrend or self.uptrend is None:
            upper_threshold = self.current_mid_price + self.brick_size
        else: # else its False and our threshold should be twice as far away before we act
            upper_threshold = self.current_mid_price + (2 * self.brick_size)


        return upper_threshold

    def calc_lower_threshold(self):
        if not self.uptrend or self.uptrend is None:
            lower_threshold = self.current_mid_price - self.brick_size
        else: # else its True and our threshold should be twice as far away
            lower_threshold = self.current_mid_price - (2 * self.brick_size)

        return lower_threshold

    def create_df(self):
        df = pd.DataFrame(self.bricks[:-1], index=self.dates[:-1])
        df.columns = ['open']

        df['close'] = self.bricks[1:]  # remove the first element

        df['high'] = df[['open', 'close']].max(axis=1)
        df['low'] = df[['open', 'close']].min(axis=1)

        return df

    def evaluate(self):
        balance = 0
        sign_changes = 0
        price_ratio = len(self.df) / len(self.direction)

        for i in range(2, len(self.direction)):
            if self.direction[i] == self.direction[i - 1]:
                balance = balance + 1
            else:
                balance = balance - 2
                sign_changes = sign_changes + 1

            if sign_changes == 0:  # if there are no sign changes set it equal to 1 to avoid div/0 error
                sign_changes = 1

            score = balance / sign_changes
            if score >= 0 and price_ratio >= 1:
                score = np.log(score + 1) * np.log(price_ratio)
            else:
                score = -1.0

            return {'balance'    : balance, 'sign_changes:': sign_changes,
                    'price_ratio': price_ratio, 'score': score}


def renko_plot(bricks_df):
    df = bricks_df
    candlestick_chart(df)

    return



if __name__ == '__main__':

    price = unpickle('data/test_data/btc_daily')

    # Make df object - we only have a "close" in column 0
    data = bt.feeds.PandasData(dataname=price, open=0, high=1, low=2, close=3, openinterest=None)

    # Initialize Cerebro Engine and add strategy
    cerebro = bt.Cerebro()
    cerebro.adddata(data)

    bricks = cerebro.strat_list[0].renko_obj.bricks












