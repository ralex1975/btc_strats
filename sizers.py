import backtrader as bt


class AllInSizer(bt.Sizer):
    """
    Sizer object that takes a position equal to 100% of the equity value at the time. If there is an existing
    position, this sizer reverses the position. For instance, if we are short 1 unit, and a long signal is generated
    and we calculate the size to be 1 unit, the sizer returns a quantity of 2.
    """

    def _getsizing(self, comminfo, cash, data, isbuy):
        position = abs(self.broker.getposition(data).size)

        market_price = self.strategy.datas[0]
        value        = self.strategy.stats.broker.value[0]

        ratio = value / market_price
        qty = ratio + position # Doesn't require rounding for BTC

        return qty


class pctSizer(bt.Sizer):
    """
    Size our positions based on a percent of assets, and the average true range
    """

    def __init__(self, riskPct=0.02):
        self.risk_pct = riskPct

    def _getsizing(self, comminfo, cash, data, isbuy):
        multiplier = self.strategy.p.atrmultiplier

        value       = self.strategy.stats.broker.value[0]
        dollar_risk = self.risk_pct * value
        stopsize    = self.strategy.atr[0] * multiplier

        qty = dollar_risk / stopsize

        return qty