from os.path import dirname, join
from configuration import ConfigurationFactory
from datetime import datetime
from manager.data import DataManager
import pandas as pd

class StrategyFactory:

    def __init__(self):
        self._init_config()

    def _init_config(self):
        self._config = ConfigurationFactory.create_btest_config()
        self.start_date = self._config["backtest_config"]["start_date"]


    def create_strategies(self):
        print("{} - Initialising strategies".format(datetime.now()))
        #we need to read the correct year file first
        self.gen_trading_dates()

    def gen_trading_dates(self):
        yyyy = self.start_date[:4]
        #read the first trade entry date
        print("{} - Loading first trade date from exchange data".format(datetime.now()))
        data = DataManager.load_exchange_data(yyyy)
        #get the nearest date to start date but first we need to set it as an index
        _tmp = pd.DataFrame(data["date"].unique(),
                            index=data["date"].unique())
        _first_available_date_idx = _tmp.index.get_loc(self.start_date,
                                                       method='nearest')
        _first_trade_date = data.iloc[_first_available_date_idx]["date"]
        self._trade_dates = data[data["date"] >= _first_trade_date]["date"].unique()
        print("{} - Successfully generated trading dates from start date of backtest".format(datetime.now()))



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
