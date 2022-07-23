from os.path import dirname, join
from configuration import ConfigurationFactory
from datetime import datetime
from manager.data import DataManager
import pandas as pd
from strategy.leg import Leg
from pricing.bs_model import BlackScholes
from utility.date_utility import DateUtility

class StrategyFactory:

    def __init__(self):
        #initialise strategies container
        self._init_params()
        #load the configuration but purely for dates
        self._init_date_config()
        #step 1: initialise the filtered set of trading dates based on leg entry frequency
        self.create_strategies()
        #clean the strategies container removing redundant trade dates
        self._clean_strategies()


    def _init_params(self):
        self.strategies = {}

    def _init_date_config(self):
        self._config = ConfigurationFactory.create_btest_config()

        #initialise start and end dates
        self.start_date = self._config["backtest_config"]["start_date"]
        self.end_date = self._config["backtest_config"]["end_date"]

        #this initialises whether the strategy is multileg_delta_strike_strategy or
        self._strat_type = self._config["backtest_config"]["trading_params"]["strat_type"]["method"]

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

    def create_strategies(self):
        """
        We generate the list of trading dates based on the entry frequency
        of each leg using pandas date range

        Observe that we have an option expiry filter based on the options that we are trading
        This reduces the amount of memory we consume when reading data as a filter

        :return: A list of trading dates based on the trading parameters
        """
        print("{} - Initialising strategies".format(datetime.now()))
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

            #We initialise the configuration based on the strategy type (whether this is multileg or outright)
            self._strat_config = self._config["backtest_config"][self._strat_type]

            #we now need to collect the list of options that are in the delta strike range and create strategy
            #objects assuming there are all 4 days to expiry in the weeklys
            for trade_date in self.strategies[year]:
                #we omit the trading day if there is no 4 dte option (i.e. max of dte)
                new_leg_mty = data["dte"].max()
                #step 1: first get all of the new weeklys that we trade on this date
                #i.e. if we dont have any new weeklys to trade on this date then we skip this from the data
                if (data[data["date"] == trade_date]["dte"] == new_leg_mty).value_counts().index[0] is True:
                    print("{} - Creating strategies for trade date: {}".format(datetime.now(),
                                                                               trade_date))
                    self.strategies[year][trade_date] = Strategy(config_params=self._strat_config,
                                                                 trade_date=trade_date,
                                                                 data=data,
                                                                 strat_type=self._strat_type)
                    print("{} - Finished creating strategies for trade date: {}".format(datetime.now(),
                                                                                        trade_date))
                else:
                    print("{} - Skipping trade date: {} as there is no leg data".format(datetime.now(),
                                                                                        trade_date))
    def _clean_strategies(self):
        """
        We clean the strategies object removing redundant dates
        :return:
        """
        print("{} - Cleaning Strategies".format(datetime.now()))
        for yyyy in list(self.strategies.keys()):
            _tmp = {}
            for t_stamp, strat in list(self.strategies[yyyy].items()):
                if strat is not None:
                    _tmp[t_stamp] = strat
            #reassign back to strategies
            self.strategies[yyyy] = _tmp


class Strategy:

    def __init__(self, config_params=None, data=None, trade_date=None, strat_type=None):
        #initialise config
        self._init_config(config_params)
        #create the data filter for the trade date
        self._tmp = data[data["date"] == trade_date]

        #if we have a multileg strategy we need to create the legs from the delta strike
        if strat_type == "multi_leg_strategy":
            self._gen_multileg_strategy(data=data)
        elif strat_type == "outright_strategy":
            #need to call initialise call/put legs
            self._gen_outright_strategy(data=data)

        print("{} - Successfully created strategies".format(datetime.now()))

    def _init_config(self, config_params):
        self._strat_config = config_params

    def _gen_outright_strategy(self, data=None):
        for call_put_legs in self._strat_config:
            #create the self.call_legs = {} / self.put_legs = {} container
            setattr(self, call_put_legs, {})
            for _leg_id in self._strat_config[call_put_legs]:
                _leg_params = self._strat_config[call_put_legs][_leg_id]
                #get the fixed strike here
                fixed_strike = self._get_fixed_strike(data=data, leg_params=_leg_params)
                fixed_strike_leg_params = self._tmp.loc[(self._tmp["strike_price"] == fixed_strike) & \
                                                        (self._tmp["cp_flag"] == _leg_params["call_put"].upper())]
                #create the leg object
                _leg = Leg(params=fixed_strike_leg_params)
                _leg.leg_data = data.loc[(data["exdate"] == _leg.exp_date) & \
                                         (data["strike_price"] == _leg.strike) & \
                                         (data["cp_flag"] == _leg.opt_type)]
                # the data has duplicate rows which is annoying - we drop them here
                # note we had dte 4,4,3,3,2,2,1,1,0 so we drop these for the same fixed strike to expiry
                _leg.leg_data.drop_duplicates(subset="dte", keep="last", inplace=True)
                # add to the leg collection
                getattr(self, call_put_legs)[_leg_id] = _leg

    def _get_fixed_strike(self, data=None, leg_params=None):
        # for each trade entry date we need to compute the fixed strike of the option
        # pseudo method means we should be using the atm vol with the forward

        # step 1: get the forward price
        _fwd = self._tmp["forward_price"].iloc[0]
        # step 2: get the atm vol by finding the fixed strike nearest to the forward price
        # spx strikes round every 5 as the min increment
        base = 5
        _atm_strike = int(base * round(_fwd / base))
        _atm_vol = self._tmp.loc[(self._tmp["strike_price"] == _atm_strike) & \
                                 (self._tmp["cp_flag"] == leg_params["call_put"].upper())]["bs_vol"].values[0]
        # step 3 compute the fixed strike option that we trade and create the leg
        _fixed_strike = BlackScholes.invert_bs_delta_get_strike(forward=_fwd,
                                                                delta_strike=leg_params["delta_strike"],
                                                                mty=data["dte"].max(),
                                                                vol=_atm_vol,
                                                                option_type=leg_params["call_put"])
        # step 4 round the fixed strike to nearest tradeable strike
        fixed_strike = int(base * round(_fixed_strike / base))
        return fixed_strike

    def _gen_multileg_strategy(self, data=None):
        # apply delta strike range
        self._apply_delta_strike_filter()
        # initialise call and put legs
        self._init_multi_call_legs(data=data)
        self._init_multi_put_legs(data=data)

    def _apply_delta_strike_filter(self):
        self._call_delta_strikes = self._tmp.loc[(self._tmp['bs_delta'] >= self._strat_config["call_legs"]["delta_strike_range"][1]) \
                                                 & (self._tmp['bs_delta'] <= self._strat_config["call_legs"]["delta_strike_range"][0])]
        self._put_delta_strikes = self._tmp.loc[(self._tmp['bs_delta'] >= self._strat_config["put_legs"]["delta_strike_range"][1]) \
                                                 & (self._tmp['bs_delta'] <= self._strat_config["put_legs"]["delta_strike_range"][0])]

    def _init_multi_call_legs(self, data=None):
        self.call_legs = {}
        for idx in range(len(self._call_delta_strikes)):
            leg_id = "leg_{}".format(str(idx + 1))
            _leg = Leg(params=self._call_delta_strikes.iloc[idx])
            _leg.leg_data = data.loc[(data["exdate"] == _leg.exp_date) & \
                                     (data["strike_price"] == _leg.strike) & \
                                     (data["cp_flag"] == _leg.opt_type)]
            #the data has duplicate rows which is annoying - we drop them here
            #note we had dte 4,4,3,3,2,2,1,1,0 so we drop these for the same fixed strike to expiry
            _leg.leg_data.drop_duplicates(subset="dte", keep="last", inplace=True)

            #add to the leg collection
            self.call_legs[leg_id] = _leg

    def _init_multi_put_legs(self, data=None):
        self.put_legs = {}
        for idx in range(len(self._put_delta_strikes)):
            leg_id = "leg_{}".format(str(idx + 1))
            _leg = Leg(params=self._put_delta_strikes.iloc[idx])
            _leg.leg_data = data.loc[(data["exdate"] == _leg.exp_date) & \
                                     (data["strike_price"] == _leg.strike) & \
                                     (data["cp_flag"] == _leg.opt_type)]
            #the data has duplicate rows which is annoying - we drop them here
            #note we had dte 4,4,3,3,2,2,1,1,0 so we drop these for the same fixed strike to expiry
            _leg.leg_data.drop_duplicates(subset="dte", keep="last", inplace=True)

            #add to the leg collection
            self.put_legs[leg_id] = _leg

