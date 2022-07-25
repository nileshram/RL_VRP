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
        self.config = ConfigurationFactory.create_btest_config()

    def _init_conf(self):
        pass

    def run(self):
        print("{} - Running backtesting engine".format(datetime.now()))
        strat_index = self.pnl.run(strategies=self.strategies)

        #tmp plottiing engine
        plt.plot(strat_index["opt_pnl"],
                 label="Unhedged")
        plt.plot(strat_index["dh_pnl"],
                 label="Daily delta-hedged")

        #add chart formatting
        ax1 = plt.gca()
        plt.minorticks_on()
        plt.xlabel('Time')
        plt.ylabel('Strategy Index (Total Ret)')
        plt.title("SPX Weeklys - Synthetic Variance")
        ax1.set_facecolor(color='whitesmoke')
        plt.grid(b=True, which='minor', color='#999999', linestyle='-', alpha=0.2)
        plt.legend()
        plt.show()

        print("{} - Finished running backtesting engine".format(datetime.now()))
