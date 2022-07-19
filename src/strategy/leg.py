

class Leg:

    def __init__(self, params=None):
        self._init_params(params)

    def _init_params(self, params=None):
        #store the fixed strike option details in each leg
        self.exp_date = params.exdate
        self.strike = params.strike_price
        self.opt_type = params.cp_flag
        #store the initial delta strike and forward price
        self._initial_forward = params.forward_price
        self._initial_delta = params.bs_delta


    