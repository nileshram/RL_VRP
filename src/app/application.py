from strategy.strategy import StrategyFactory
from datetime import datetime

class BacktestingEngine:

    def __init__(self):
        #initialise configuration
        self._init_conf()
        #initialise backtest parameters
        self._init_params()

    def _init_params(self):
        self.strategies = StrategyFactory()

    def _init_conf(self):
        pass

    def _run(self):
        pass

    def run(self):
        print("{} - Running backtesting engine".format(datetime.now()))
