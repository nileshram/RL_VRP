##mini application to apply the pricing to the existing datasets and append the greek computation to the csv


import pandas as pd
import numpy as np
from pricing.bs_model import BlackScholes
from configuration import ConfigurationFactory
from manager.data import DataManager
from os.path import dirname, join


class Application:

    def __init__(self):
        self._init_params()

    def _init_params(self):
        _root = dirname(dirname(dirname(__file__)))
        self.output_path = join(_root, "priced_data")

    def run(self):
        #test the pricing lib
        data = DataManager.load_exchange_data_and_apply_days_to_expiry_filter("2015",
                                                                              opt_expiry_filter=5)[:10000]
        #apply pricing
        data["bs_price"] = data.apply(lambda x: BlackScholes.compute_price(forward=x["forward_price"],
                                                                           strike=x["strike_price"],
                                                                           mty=x["dte"],
                                                                           vol=x["impl_volatility"],
                                                                           option_type=x["cp_flag"]),
                                                                           axis=1)
        data["bs_delta"] = data.apply(lambda x: BlackScholes.compute_delta(forward=x["forward_price"],
                                                                           strike=x["strike_price"],
                                                                           mty=x["dte"],
                                                                           vol=x["impl_volatility"],
                                                                           option_type=x["cp_flag"]),
                                                                           axis=1)
        data["bs_vega"] = data.apply(lambda x: BlackScholes.compute_vega(forward=x["forward_price"],
                                                                           strike=x["strike_price"],
                                                                           mty=x["dte"],
                                                                           vol=x["impl_volatility"],
                                                                           option_type=x["cp_flag"]),
                                                                           axis=1)
        print("stop")
        #data["bs_delta"] = pd.applu


if __name__ == "__main__":
    try:
        app = Application()
        app.run()
    except Exception as e:
        print(str(e))
