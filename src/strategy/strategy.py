from os.path import dirname, join
from configuration import ConfigurationFactory
from datetime import datetime
from manager.data import DataManager
import pandas as pd
from utility.date_utility import DateUtility

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

    def _gen_trading_dates(self, data_trading_dates, pd_trading_dates):
        """
        From the raw data we create the list of final trading dates and return the output as a list
        :return:
        """

        # get the nearest date to start date but first we need to set it as an index
        _tmp = pd.DataFrame(data_trading_dates["date"].unique(),
                            index=data_trading_dates["date"].unique())
        _first_available_date_idx = _tmp.index.get_loc(self.start_date,
                                                       method='nearest')
        _first_trade_date = data_trading_dates.iloc[_first_available_date_idx]["date"]
        _data_trade_dates = data_trading_dates[data_trading_dates["date"] >= _first_trade_date]["date"].unique()

        # Finally apply the _data_trade_dates as a filter to _trading_date_range
        _mask = pd_trading_dates.isin(_data_trade_dates)
        _final_trading_dates = pd_trading_dates[_mask].to_list()
        return _final_trading_dates

    def create_strategy_trading_dates(self):
        """
        We generate the list of trading dates based on the entry frequency
        of each leg using pandas date range

        Observe that we have an option expiry filter based on the options that we are trading
        This reduces the amount of memory we consume when reading data as a filter

        :return: A list of trading dates based on the trading parameters
        """

        #load frequencies and expiries from config
        self._leg_freq = self._config["backtest_config"]["trading_params"]["entry_freq"]
        self._opt_expiry_calendar = self._config["backtest_config"]["trading_params"]["option_expiry_calendar"]

        for idx, year in enumerate(self._years):
            #first we create the range of dates based on entry frequency
            _trading_date_range = pd.date_range(start=self._year_start[idx],
                                               end=self._year_end[idx],
                                               freq=self._leg_freq)
            #next we load the correct csv data
            data = DataManager.load_priced_exchange_data(year,
                                                         option_expiry_calendar=self._opt_expiry_calendar)
            ##########
            # step 1 #
            ##########
            #step 1: filter the trading date range we created above
            #incase some of the data doesnt exist for those trading dates
            _final_trading_dates = self._gen_trading_dates(data, _trading_date_range)
            #end step 1: append these to self.strategies per year
            self.strategies[year] = dict.fromkeys(_final_trading_dates)

            ##########
            # step 2 #
            ##########
            #step 2: from the clean list of trading dates we have we now need to create the strategy and leg
            #objects from the leg data

            #multileg strategy
            self._multileg_config = self._config["backtest_config"]["multi_leg_strategy"]
            #we now need to collect the list of options that are in the delta strike range and create strategy
            #objects assuming there are all 4 days to expiry in the weeklys

            for trade_date in self.strategies[year]:
                #we omit the trading day if there is no 4 dte option (i.e. max of dte)
                new_leg_mty = data["dte"].max()
                #step 1: first get all of the new weeklys that we trade on this date
                #i.e. if we dont have any new weeklys to trade on this date then we skip this from the data
                if (data[data["date"] == trade_date]["dte"] == new_leg_mty).value_counts().index[0] is True:
                    #then we construct the strategy here
                    _tmp = data[data["date"] == trade_date].copy()
                    #we now filter for the delta strikes
                    _tmp
                    self.strategies[year][trade_date] = Strategy(config_params=self._multileg_config,
                                                                 trade_date=trade_date,
                                                                 data=data)
                #iterate through each of the rows in the trading date and we need to check

                #if the delta strike is in the bucket and filter for these strikes



            print("stop")




    def create_strategies(self):
        print("{} - Initialising strategies".format(datetime.now()))

class Strategy:

    def __init__(self, config_params=None, data=None, trade_date=None):

        #filter the data fpr legs
        _filtered_data = data[data["date"] == trade_date]


        self._init_config()
        self._parse_dates()

    def _init_config(self):
        pass

    def _parse_dates(self):
        pass

    def _init_legs(self):
        pass
