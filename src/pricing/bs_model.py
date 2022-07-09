import numpy as np
from scipy.stats import norm
from scipy.special import ndtri
from scipy import optimize



class BlackScholes:
    """
    Static Black Pricing Library to compute Black Price/Vega/Delta
    """

    @staticmethod
    def compute_d1(forward, strike, mty, vol, ann_factor=365):

        return(np.log(forward/strike) + vol**2 / 2 * mty / ann_factor) / (vol * np.sqrt(mty/ann_factor))

    @staticmethod
    def compute_price(forward, strike, mty, vol, r=0, ann_factor=365, option_type=None):

        #if option has expired give instrinsic
        if mty == 0:
            if option_type.lower() in ["c", "call"]:
                if max(forward - strike, 0) > 0:
                    return (forward - strike) / 1000
                else:
                    return 0
            elif option_type.lower() in ["p", "put"]:
                if max(strike - forward, 0) > 0:
                    return (strike - forward) / 1000
                else:
                    return 0

        #compute d1, d2
        d1 = BlackScholes.compute_d1(forward, strike, mty, vol)
        d2 = d1 - vol * np.sqrt(mty/ann_factor)

        if option_type.lower() in ["c", "call"]:
            return np.exp(-r * mty/ann_factor) * (forward * norm.cdf(d1) - strike * norm.cdf(d2))

        if option_type.lower() in ["p", "put"]:
            return np.exp(-r * mty/ann_factor) * (strike * norm.cdf(-d2) - forward * norm.cdf(-d1))



    @staticmethod
    def compute_delta(forward, strike, mty, vol, r=0, ann_factor=365, option_type=None):

        #if option has expired give 100 delta
        if mty == 0:
            if option_type.lower() in ["c", "call"]:
                if max(forward - strike, 0) > 0:
                    return 1
                else:
                    return 0
            elif option_type.lower() in ["p", "put"]:
                if max(strike - forward, 0) > 0:
                    return -1
                else:
                    return 0

        d1 = BlackScholes.compute_d1(forward, strike, mty, vol)

        if option_type.lower() in ["c", "call"]:
            return np.exp(-r * mty/ann_factor) * norm.cdf(d1)

        if option_type.lower() in ["p", "put"]:
            return np.exp(-r * mty/ann_factor) * (norm.cdf(d1) - 1)



    @staticmethod
    def compute_vega(forward, strike, mty, vol, r=0, ann_factor=365, option_type=None):

        d1 = BlackScholes.compute_d1(forward, strike, mty, vol)

        if mty != 0:
            vega = forward * np.exp(-r * mty/ann_factor) * np.exp(-0.5 * d1 ** 2) / np.sqrt(2 * np.pi * ann_factor/mty)
        else:
            vega = 0
        return vega

