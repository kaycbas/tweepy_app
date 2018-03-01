
class Coin :

    def __init__(self, new_symbol):
        self.symbol = new_symbol
        self.dates = []
        self.vels = []
        self.mkt_caps = []
        self.prices = []


    def add_data(self, new_date, new_mkt_cap, new_vel):
        self.dates.append(new_date)
        self.mkt_caps.append(new_mkt_cap)
        self.vels.append(new_vel)

    def get_dates(self):
        return self.dates

    def get_vels(self):
        return self.vels

    def get_prices(self):
        return self.prices

    def get_mkt_caps(self):
        return self.mkt_caps

