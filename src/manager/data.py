from os.path import dirname, join
import pandas as pd
import numpy as np
from datetime import datetime

class DataManager:

    @staticmethod
    def load_exchange_data(yyyy):
        root_dir = dirname(dirname(dirname(__file__)))
        _fname = "optionMetricsSpx{}.csv"
        data_path = join(root_dir, "raw_data", _fname.format(yyyy))
        print("{} - Loading exchange data {}".format(datetime.now(),
                                                     _fname.format(yyyy)))
        data = pd.read_csv(data_path)
        try:
            data.drop(columns=["secid", "optionid", "index_flag", "issuer", "exercise_style", "volume", "div_convention", "last_date"],
                      inplace=True)
        except Exception as e:
            try:
                data.drop(columns=["optionid", "index_flag", "issuer", "exercise_style", "volume", "last_date"],
                          inplace=True)
            except Exception as e:
                data.drop(columns=["optionid", "index_flag", "issuer", "exercise_style", "volume"],
                          inplace=True)
            print("{} - Successfully dropped redundant columns from {}".format(datetime.now(),
                                                                               _fname.format(yyyy)))
        data[["strike_price", "best_bid", "best_offer"]] /= 1000

        #create mid price
        data["mid_price"] = (data["best_bid"] + data["best_offer"]) / 2
        #parse dates
        data["date"] = pd.to_datetime(data["date"], format="%Y%m%d")
        data["exdate"] = pd.to_datetime(data["exdate"], format="%Y%m%d")
        #compute days to expiry
        data["dte"] = (data["exdate"] - data["date"]).astype('timedelta64[D]')

        return data


    @staticmethod
    def load_exchange_data_and_apply_days_to_expiry_filter(yyyy, opt_expiry_filter=None):
        data = DataManager.load_exchange_data(yyyy)
        # to reduce the data size we only preserve the data with expiry dates < option expiry
        # we also need to reset the index
        data = data[data["dte"] < opt_expiry_filter]
        data.reset_index(inplace=True, drop=True)
        return data

    @staticmethod
    def load_priced_exchange_data(yyyy, option_expiry_calendar="weeklies"):
        #filepaths
        root_dir = dirname(dirname(dirname(__file__)))
        _fname = "priced_{}_optionMetricsSpx{}.csv"
        data_path = join(root_dir, "priced_data", _fname.format(option_expiry_calendar, yyyy))

        print("{} - Loading exchange data {}".format(datetime.now(),
                                                     _fname.format(option_expiry_calendar, yyyy)))
        data = pd.read_csv(data_path)
        #parse dates
        data["date"] = pd.to_datetime(data["date"], format="%Y-%m-%d")
        data["exdate"] = pd.to_datetime(data["exdate"], format="%Y-%m-%d")

        return data

