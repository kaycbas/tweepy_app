
class Coin :

    def __init__(self, new_symbol):
        self.symbol = new_symbol
        self.dates = []
        self.vels = []
        self.mkt_caps = []
        self.prices = []

    #def setSymbol(self, new_symbol):
    #    self.symbol = new_symbol

    def add_data(self, new_date, new_mkt_cap, new_vel):
        self.dates.append(new_date)
        self.mkt_caps.append(new_mkt_cap)
        self.vels.append(new_vel)


