import pandas as pd
import numpy as np


class StrategyMetrics:

    @staticmethod
    def compute_info_ratio(timeseries):
        mean = StrategyMetrics.compute_returns(timeseries)
        vol = StrategyMetrics.compute_volatility(timeseries)
        ir = mean / vol
        return ir

    @staticmethod
    def compute_returns(timeseries):
        mean = ((timeseries.iloc[-1] / timeseries.iloc[0]) ** (1 / timeseries.shape[0]) - 1) * 252
        return mean

    @staticmethod
    def compute_volatility(timeseries):
        vol = timeseries.pct_chamge(1).std() * np.sqrt(252)
        return vol

    @staticmethod
    def compute_cvar(timeseries, n_days=21, q=0.05):
        rets = timeseries.pct_change(n_days)
        thresholds = rets.quintile(q)
        cvar = pd.Series(index=thresholds.index, dtype=float)

        for idx in thresholds.index:
            location = rets[idx] <= thresholds.loc[idx]
            cvar.loc[idx] = rets.loc[location, idx].mean()

        return cvar

        pass

    @staticmethod
    def compute_calmar_ratio():
        pass