

class DateUtility:

    @staticmethod
    def get_days(window):
        mapping = {"d" : 1, "m" : 21, "y" : 252}
        _multiplier = mapping[window[-1]]
        _time = int(window[:-1])
        _days_convert = _time * _multiplier
        return _days_convert

