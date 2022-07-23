from strategy.strategy import StrategyFactory
from datetime import datetime
from pnl.pnl_calculation import PnLEngine
from configuration import ConfigurationFactory
import pandas as pd
import matplotlib.pyplot as plt


class BacktestingEngine:

    def __init__(self):
        #initialise configuration
        self._init_conf()
        #initialise backtest components
        self._init_components()

    def _init_components(self):
        self.strategies = StrategyFactory().strategies
        self.pnl = PnLEngine()
        self.config = ConfigurationFactory.create_btest_config()["backtest_config"]["multi_leg_strategy"]

    def _init_conf(self):
        pass

    def _run_call_pnl(self):
        call_pnl = []
        for yyyy in self.strategies:
            for trade_entry in self.strategies[yyyy]:
                #compute the call leg pnl and the dh pnl in separate column
                _strat = self.strategies[yyyy][trade_entry]
                for _leg in _strat.call_legs:
                    #compute the pnl here
                    _leg_data = _strat.call_legs[_leg].leg_data
                    _leg_data["opt_pnl"] = self.config["call_legs"]["long_short"] * _leg_data["bs_price"].diff()
                    _leg_data["delta_pnl"] = - self.config["call_legs"]["long_short"] * _leg_data["forward_price"].diff() * _leg_data["bs_delta"].shift()
                    _leg_data["dh_pnl"] = _leg_data["opt_pnl"] + _leg_data["delta_pnl"]
                    #now we just need to store the filtered dataframe in a res container (note this is tick pnl)
                    #_leg_data["opt_pnl_usd"] =_leg_data["opt_pnl"]
                    #_leg_data["delta_pnl_usd"] = _leg_data["delta_pnl"]
                    _tmp = _leg_data.filter(["date", "opt_pnl", "dh_pnl"])
                    _tmp.set_index("date", drop=True, inplace=True)
                    call_pnl.append(_tmp)
        return pd.concat(call_pnl, axis=0).dropna().groupby("date").sum()

    def _run_put_pnl(self):
        put_pnl = []
        for yyyy in self.strategies:
            for trade_entry in self.strategies[yyyy]:
                #compute the put leg pnl and the dh pnl in separate column
                _strat = self.strategies[yyyy][trade_entry]
                for _leg in _strat.put_legs:
                    #compute the pnl here
                    _leg_data = _strat.put_legs[_leg].leg_data
                    _leg_data["opt_pnl"] = self.config["put_legs"]["long_short"] * _leg_data["bs_price"].diff()
                    _leg_data["delta_pnl"] = - self.config["put_legs"]["long_short"] * _leg_data["forward_price"].diff() * _leg_data["bs_delta"].shift()
                    _leg_data["dh_pnl"] = _leg_data["opt_pnl"] + _leg_data["delta_pnl"]
                    #now we just need to store the filtered dataframe in a res container (note this is tick pnl)
                    #_leg_data["opt_pnl_usd"] =_leg_data["opt_pnl"]
                    #_leg_data["delta_pnl_usd"] = _leg_data["delta_pnl"]
                    _tmp = _leg_data.filter(["date", "opt_pnl", "dh_pnl"])
                    _tmp.set_index("date", drop=True, inplace=True)
                    put_pnl.append(_tmp)
        return pd.concat(put_pnl, axis=0).dropna().groupby("date").sum()

    def run(self):
        print("{} - Running backtesting engine".format(datetime.now()))
        call_pnl = self._run_call_pnl()
        put_pnl = self._run_put_pnl()
        total_pnl = pd.concat([call_pnl, put_pnl],
                              axis=0).groupby("date").sum()

        # we build the index here starting at 100
        strat_index = pd.DataFrame(index=total_pnl.index,
                                   columns=total_pnl.columns)
        index_start = 100
        #insert starting value of strat
        strat_index.iloc[:1] = index_start
        #now we iterate through the total_pnl and we append the result to the strat index
        for pnl_type in total_pnl.columns:
            for i in range(1, len(strat_index)):
                strat_index[pnl_type].iloc[i] = strat_index[pnl_type].iloc[i - 1] + total_pnl[pnl_type].iloc[i - 1]

        plt.plot(strat_index["opt_pnl"],
                 label="Unhedged")
        plt.plot(strat_index["dh_pnl"],
                 label="Daily delta-hedged")

        #add chart formatting
        ax1 = plt.gca()
        plt.minorticks_on()
        plt.xlabel('Time')
        plt.ylabel('Strategy Index')
        plt.title("SPX Weeklys Call/Put Strip Backtest")
        ax1.set_facecolor(color='whitesmoke')
        plt.grid(b=True, which='minor', color='#999999', linestyle='-', alpha=0.2)
        plt.legend()
        plt.show()

        print("{} - Finished running backtesting engine".format(datetime.now()))
