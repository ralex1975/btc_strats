from binance.client import Client
import pandas as pd
import numpy as np

class Binance:
    def __init__(self):
        self.client = Client(api_key="D9azBLv8IbJlbXonWEIpdo0m3xl3pL1PFMR9XR1N6MS76rHM1V3gyXQ0PilwoKiY",
                             api_secret="l75AQwSKycSa64xZVOYRcPPodp4h27du8LrgVM0LcYsll2o0U89X3vHqR8rTmjmd")

    def getPrice(self, symbol, interval, nWeeks=104):

        price = self.client.get_historical_klines(symbol=symbol, interval=eval('Client.KLINE_INTERVAL_' + interval),
                                                  start_str=str(nWeeks) + ' weeks ago')

        compiled_price = self.compilePrice(price)

        return compiled_price

    @staticmethod
    def compilePrice(prices):
        price_matrix = np.row_stack(prices)
        price_series = pd.DataFrame(price_matrix)
        price_series = price_series.set_index(0)
        price_series.index = pd.to_datetime(price_series.index, unit='ms')
        price_series = price_series.iloc[:, 0:5]
        price_series = price_series.apply(pd.to_numeric)
        price_series.columns = ['open', 'high', 'low', 'close', 'volume']

        return price_series

if __name__ == '__main__':
    import pickle
    interval = '1DAY'

    binance = Binance()
    price = binance.getPrice(symbol='BTCUSDT', interval=interval, nWeeks=65)
    outfile = open('btc_' + interval, 'wb')
    pickle.dump(price, outfile)
    outfile.close()