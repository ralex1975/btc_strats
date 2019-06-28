import numpy as np
import pickle


def unpickle(file):
    infile = open(file, 'rb')
    data = pickle.load(infile)
    infile.close()

    return data

def dopickle(obj, file):
    with open(file, 'wb') as f:
        pickle.dump(obj, f)

def stride_axis(arr, window):
    """
    Takes a numpy array and creates multiple rolling arrays of size "window"
    :param arr: 1D Numpy Array
    :param window: Integer Size of desired arrays to return
    """

    shp = arr.shape
    strides = arr.strides

    nd0 = shp[0] - window + 1 # compute length of output array

    shp_in = (nd0, window) + shp[1:]
    strd_in = (strides[0],) + strides
    output = np.lib.stride_tricks.as_strided(arr, shape=shp_in, strides=strd_in)

    return output


def ATR(OHLC):
    """
    This function computes the Average True Range of the OHLC Data Passed into it.
    By design, this only returns the last value, but this could be changed.

    :param OHLC: Open-High-Low-Close Dataframe Time Series
    :return: Average True Range from the last 14 days.
    """

    # Series 1 is the current high minus the current low.
    series_1 = OHLC['high'] - OHLC['low']

    # Series 2 is the absolute value of the current high less the previous close
    series_2 = abs(OHLC['high'] - OHLC['close'].shift(1))

    # Series 3 is the absolute value of the current low less the previous close
    series_3 = abs(OHLC['low'] - OHLC['close'].shift(1))

    # The true range is the maximum of Series 1/2/3
    true_range = series_1.combine(series_2, max).combine(series_3, max)

    # The Average True Range is the 14-day mean of the true range
    atr = true_range.rolling(window=14).mean()
    last = float(atr[-1])

    return last