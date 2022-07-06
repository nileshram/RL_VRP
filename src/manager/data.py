from os.path import dirname, join
import pandas as pd

class DataManager:

    @staticmethod
    def load_exchange_data(yyyy):
        root_dir = dirname(dirname(dirname(__file__)))
        data_path = join(root_dir, "data", "optionMetricsSpx{}.csv".format(yyyy))

        data = pd.read_csv(data_path)
        data.drop(columns=["secid", "optionid", "index_flag", "issuer", "exercise_style"],
                  inplace=True)
        data[["strike_price", "best_bid", "best_offer"]] /= 1000

        #parse dates
        data["date"] = pd.to_datetime(data["date"], format="%Y%m%d")
        data["exdate"] = pd.to_datetime(data["exdate"], format="%Y%m%d")

        return data


