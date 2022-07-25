import pandas as pd
from configuration import ConfigurationFactory
from datetime import datetime

class PnLEngine:

    def __init__(self):
        #initialise config
        self._init_config()
        #initialise params
        self._init_params()

    def _init_config(self):
        print("{} - Initialising pnl engine".format(datetime.now()))
        self._config = ConfigurationFactory.create_btest_config()["backtest_config"]
        self._strat_type = self._config["trading_params"]["strat_type"]["method"]
        self.config = self._config[self._strat_type]

    def _init_params(self):
        self._options = ["call", "put"]

    def compute_total_leg_pnl(self, strategies):
        """
        Computes the leg pnl for both call and put legs
        """
        pnl = []
        for yyyy in strategies:
            for trade_entry in strategies[yyyy]:
                #compute the leg pnl and the dh pnl in separate column
                _strat = strategies[yyyy][trade_entry]
                for _leg_type in self._options:
                    try:
                        _leg_id = "{}_legs".format(_leg_type)
                        _strat_legs = getattr(_strat, _leg_id)
                        for _leg in _strat_legs:
                            #compute the pnl here
                            _leg_data = _strat_legs[_leg].leg_data
                            _leg_data["opt_pnl"] = self.config[_leg_id]["long_short"] * _leg_data["bs_price"].diff()
                            _leg_data["delta_pnl"] = -self.config[_leg_id]["long_short"] * _leg_data["forward_price"].diff() * _leg_data["bs_delta"].shift()
                            _leg_data["dh_pnl"] = _leg_data["opt_pnl"] + _leg_data["delta_pnl"]
                            #now we just need to store the filtered dataframe in a res container (note this is tick pnl)
                            _tmp = _leg_data.filter(["date", "opt_pnl", "dh_pnl"])
                            _tmp.set_index("date", drop=True, inplace=True)
                            pnl.append(_tmp)
                    except AttributeError as e:
                        print("{} - strategy object does not contain {} legs; removing from possible options".format(datetime.now(),
                                                                                                                     _leg_type))
                        #in which case we remove it from self._options list
                        self._options.remove(_leg_type)

        return pd.concat(pnl, axis=0).dropna().groupby("date").sum()

    def create_strategy_index(self, total_pnl):
        index_start = 100
        # we build the index here starting at 100
        strat_index = pd.DataFrame(index=total_pnl.index,
                                   columns=total_pnl.columns)
        #insert starting value of strat
        strat_index.iloc[:1] = index_start
        #now we iterate through the total_pnl and we append the result to the strat index
        for pnl_type in total_pnl.columns:
            for i in range(1, len(strat_index)):
                strat_index[pnl_type].iloc[i] = strat_index[pnl_type].iloc[i - 1] + total_pnl[pnl_type].iloc[i - 1]

        return strat_index

    def run(self, strategies=None):
        total_pnl = self.compute_total_leg_pnl(strategies)
        strat_index = self.create_strategy_index(total_pnl)

        return strat_index


