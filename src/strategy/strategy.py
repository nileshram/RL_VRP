from os.path import dirname, join
from configuration import ConfigurationFactory
from datetime import datetime
from manager.data import DataManager
import pandas as pd

class StrategyFactory:

    def __init__(self):
        #initialise strategies container
        self._init_params()
        #load the configuration but purely for dates
        self._init_date_config()
        #step 1: initialise the filtered set of trading dates based on leg entry frequency
        self.create_strategy_trading_dates()
        #step 2: for each of the trading dates, we need to trade the correct set of expiries

    def _init_params(self):
        self.strategies = {}

    def _init_date_config(self):
        self._config = ConfigurationFactory.create_btest_config()
        #initialise start and end dates
        self.start_date = self._config["backtest_config"]["start_date"]
        self.end_date = self._config["backtest_config"]["end_date"]
        #create the list of years as keys based on the data year files
        _years = pd.date_range(start=pd.to_datetime(self.start_date, format="%Y-%m-%d"),
                               end=pd.to_datetime(self.end_date, format="%Y-%m-%d"),
                               freq="1Y")
        _year_start = pd.date_range(start=pd.to_datetime(self.start_date, format="%Y-%m-%d"),
                               end=pd.to_datetime(self.end_date, format="%Y-%m-%d"),
                               freq="1YS")
        #we also create the start and end dates for each of the years so that we can generate the trading dates
        #inbetween the start and end date
        self._year_start = _year_start.to_list()
        self._year_end = _years.to_list()
        self._years = [str(y.year) for y in _years]

    def create_strategy_trading_dates(self):
        """
        We generate the list of trading dates based on the entry frequency
        of each leg using pandas date range
        :return: A list of trading dates based on the trading parameters
        """
        self._leg_freq = self._config["backtest_config"]["trading_params"]["entry_freq"]
        for idx, year in enumerate(self._years):
            #first we create the range of dates based on entry frequency
            _trading_date_range = pd.date_range(start=self._year_start[idx],
                                               end=self._year_end[idx],
                                               freq=self._leg_freq)
            #next we load the correct csv data and use this to filter the trading date range we created above
            #incase some of the data doesnt exist for those trading dates
            data = DataManager.load_exchange_data(year)
            # get the nearest date to start date but first we need to set it as an index
            _tmp = pd.DataFrame(data["date"].unique(),
                                index=data["date"].unique())
            _first_available_date_idx = _tmp.index.get_loc(self.start_date,
                                                           method='nearest')
            _first_trade_date = data.iloc[_first_available_date_idx]["date"]
            _data_trade_dates = data[data["date"] >= _first_trade_date]["date"].unique()

            #Finally apply the _data_trade_dates as a filter to _trading_date_range
            _mask = _trading_date_range.isin(_data_trade_dates)
            _final_trading_dates = _trading_date_range[_mask].to_list()
            #we now append these to self.strategies for each year
            self.strategies[year] = dict.fromkeys(_final_trading_dates)
        print("stop")

    def create_strategies(self):
        print("{} - Initialising strategies".format(datetime.now()))

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
