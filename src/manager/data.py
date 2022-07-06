from os.path import dirname, join
import pandas as pd

class DataParser:

    @staticmethod
    def load_exchange_data():
        root_dir = dirname(dirname(__file__))
        data_path = join(root_dir, "data", "optionMetricsSpx2020.csv")

        data = pd.read_csv(data_path)
        data.drop(columns=["secid", "optionid", "index_flag", "issuer", "exercise_style"],
                  inplace=True)
        data[["strike_price", "best_bid", "best_offer"]] /= 1000

        #parse dates
        data["date"] = pd.to_datetime(data["date"], format="%Y%m%d")
        data["exdate"] = pd.to_datetime(data["exdate"], format="%Y%m%d")

        print(data.head())


