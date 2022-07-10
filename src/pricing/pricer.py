##mini application to apply the pricing to the existing datasets and append the greek computation to the csv


import pandas as pd
import numpy as np
from pricing.bs_model import BlackScholes
from configuration import ConfigurationFactory
from manager.data import DataManager
from os.path import dirname, join
from datetime import datetime

class Application:

    def __init__(self):
        self._init_params()

    def _init_params(self):
        _root = dirname(dirname(dirname(__file__)))
        self.output_path = join(_root, "priced_data")

        self.filename = "priced_weeklies_optionMetricsSpx{}.csv"

    def run(self):
        years = [str(i) for i in range(2003, 2020)]
        for yy in years:
            #run the pricing
            self._run_pricing_and_risk(yy)
            #output to csv
            self._output_to_csv(yy)

    def _run_pricing_and_risk(self, yy):
        #test the pricing lib
        data = DataManager.load_exchange_data_and_apply_days_to_expiry_filter(yy,
                                                                              opt_expiry_filter=5)

        #WE REQUIRE THE MULTIPLIER HERE
        data["bs_vol"] = data.apply(lambda x: BlackScholes.compute_vol_from_price(forward=x["forward_price"],
                                                                                  strike=x["strike_price"],
                                                                                  mty=x["dte"],
                                                                                  opt_price=x["mid_price"] * 1000,
                                                                                  option_type=x["cp_flag"]),
                                                                                  axis=1)
        #apply pricing AND APPLY MULTIPLIER
        data["bs_price"] = data.apply(lambda x: BlackScholes.compute_price(forward=x["forward_price"],
                                                                           strike=x["strike_price"],
                                                                           mty=x["dte"],
                                                                           vol=x["bs_vol"],
                                                                           option_type=x["cp_flag"]),
                                                                           axis=1) / 1000

        # OBSERVER WE HAD TO RUN THIS AS A TEST TO RECONCILE THE VOLS WE HAD IN THE ORIGINAL DATA FILE
        #IT TURNS OUT THAT WE WERE ABLE TO GET THE SAME VOL ONLY ONCE WE MULTIPLY PRICES BY 1000
        #THIS IS THE MULTIPLIER IN THE CONTRACT

        #FINALLY NOTE THAT END OF MONTHLYS ALSO BECOME WEEKLIES SO ITS FINE TO SET A HARD CUT OFF LIMIT
        #TO THE OPTIONS WITH LESS THAN 5 DAYS TO EXPIRY

        # data["bs_price_spxvol"] = data.apply(lambda x: BlackScholes.compute_price(forward=x["forward_price"],
        #                                                                    strike=x["strike_price"],
        #                                                                    mty=x["dte"],
        #                                                                    vol=x["impl_volatility"],
        #                                                                    option_type=x["cp_flag"]),
        #                                                                    axis=1) / 1000

        data["bs_delta"] = data.apply(lambda x: BlackScholes.compute_delta(forward=x["forward_price"],
                                                                           strike=x["strike_price"],
                                                                           mty=x["dte"],
                                                                           vol=x["bs_vol"],
                                                                           option_type=x["cp_flag"]),
                                                                           axis=1)

        data["bs_vega"] = data.apply(lambda x: BlackScholes.compute_vega(forward=x["forward_price"],
                                                                           strike=x["strike_price"],
                                                                           mty=x["dte"],
                                                                           vol=x["bs_vol"],
                                                                           option_type=x["cp_flag"]),
                                                                           axis=1)

        self.data = data
        print("{} - Finished running pricing and risk for {}".format(datetime.now(),
                                                                     self.filename.format(yy)))

    def _output_to_csv(self, yy):
        output_path = join(self.output_path, self.filename.format(yy))
        self.data.to_csv(output_path, index=False)
        print("{} - Successfully output file to csv {}".format(datetime.now(),
                                                               self.filename.format(yy)))


if __name__ == "__main__":
    try:
        app = Application()
        app.run()
    except Exception as e:
        print(str(e))
