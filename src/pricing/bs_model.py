import numpy as np
from scipy.stats import norm
from scipy.special import ndtri as norm_inv
from scipy import optimize
from py_vollib.black_scholes.implied_volatility import implied_volatility as iv
from py_vollib.helpers.exceptions import PriceIsAboveMaximum, PriceIsBelowIntrinsic

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
                    return (forward - strike)
                else:
                    return 0
            elif option_type.lower() in ["p", "put"]:
                if max(strike - forward, 0) > 0:
                    return (strike - forward)
                else:
                    return 0

        #compute d1, d2
        d1 = BlackScholes.compute_d1(forward, strike, mty, vol)
        d2 = d1 - vol * np.sqrt(mty/ann_factor)

        if option_type.lower() in ["c", "call"]:
            price = np.exp(-r * mty/ann_factor) * (forward * norm.cdf(d1) - strike * norm.cdf(d2))
        elif option_type.lower() in ["p", "put"]:
            price = np.exp(-r * mty/ann_factor) * (strike * norm.cdf(-d2) - forward * norm.cdf(-d1))

        return price



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

    @staticmethod
    def compute_vol_from_price(forward, strike, mty, opt_price, r=0, ann_factor=365, option_type=None):

        if mty == 0:
            return 0
        else:
            def func(vol, opt_type, forward, strike, mty, r, ann_factor):
                return BlackScholes.compute_price(forward=forward, strike=strike, mty=mty, vol=vol, option_type=option_type) - opt_price
            try:
                res = optimize.brentq(func, -0.001, 2, args=(option_type, forward, strike, mty, r, ann_factor),
                                   xtol=0.0000001,
                                   maxiter=100000)
            except Exception as e:
                return 0
            return res

    @staticmethod
    def get_vol(forward, strike, mty, opt_price, r=0, ann_factor=365, option_type=None):
        if mty == 0:
            return 0
        else:
            try:
                impl_vol = iv(opt_price, forward, strike, mty/365, r, option_type.lower())
            except Exception as e:
                return 0
            return impl_vol

    @staticmethod
    def get_vol_from_price_newton_method(forward, strike, mty, opt_price, r=0, ann_factor=365, option_type=None):
        """
        As a sanity check we use the brute force method because the solver doesnt always work
        """
        if mty == 0:
            return 0
        else:
            max_iter = 1000
            precision = 1.0e-4
            ivol = 0.01
            for i in range(0, max_iter):
                new_price = BlackScholes.compute_price(forward=forward, strike=strike, mty=mty,
                                                       vol=ivol, option_type=option_type)
                vega = BlackScholes.compute_vega(forward=forward, strike=strike, mty=mty,
                                                       vol=ivol, option_type=option_type)
                diff = opt_price - new_price
                if abs(diff) < precision:
                    return ivol
                ivol += diff/vega
            if ivol <= 0:
                return 0
            return ivol

    @staticmethod
    def invert_bs_delta_get_strike(forward, delta_strike, mty, vol, r=0, ann_factor=365, option_type=None):
        #see the math appendix to invert delta strikes
        if mty == 0:
            return 0
        else:
            if option_type.lower() in ["c", "call"]:
                return forward / np.exp((vol * np.sqrt(mty/ann_factor) * norm_inv(delta_strike)) - (r + (0.5 * vol**2) * np.sqrt(mty/ann_factor)))
            elif option_type.lower() in ["p", "put"]:
                return forward / np.exp((vol * np.sqrt(mty/ann_factor) * norm_inv(delta_strike + 1)) - (r + (0.5 * vol**2) * np.sqrt(mty/ann_factor)))



