from configuration import ConfigurationFactory
from datetime import datetime


class StrategyFactory:

    def __init__(self):
        self._init_config()

    def _init_config(self):
        self._config = ConfigurationFactory.create_btest_config()
        self.start_date = self._config["backtest_config"]["start_date"]

    def create_strategies(self):
        print("{} - Initialising strategies".format(datetime.now()))
        #we need to read the correct year file first
        self.gen_first_trading_date()

    def gen_trading_dates(self):
        pass

    def gen_first_trading_date(self):
        yyyy = self.start_date[:4]


class Strategy:

    def __init__(self):
        self._init_config()
        self._parse_dates()

    def _init_config(self):
        pass

    def _parse_dates(self):
        pass

    def _init_legs(self):
        pass
