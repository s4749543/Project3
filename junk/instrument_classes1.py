
class Instrument:
    def __init__(self, face_value, maturity, price):
        self.face_value = face_value
        self.maturity = maturity
        self.price = price
        self.cash_flows = []

    def add_cash_flow(self, time, amount):
        self.cash_flows.append((time, amount))

    def get_cash_flows(self):
        return self.cash_flows
    
    def get_price(self):
        return self.price
    
    def get_face_value(self):
        return self.face_value


class Bank_bill(Instrument):
    def set_cash_flows(self):
        self.add_cash_flow(0, -self.price)
        self.add_cash_flow(self.maturity, self.face_value)


class Bond(Instrument):
    def __init__(self, face_value, maturity, coupon, frequency, price):
        super().__init__(face_value, maturity, price)
        self.coupon = coupon
        self.frequency = frequency

    def set_cash_flows(self):
        self.add_cash_flow(0, -self.price)
        num_periods = int(round(self.maturity * self.frequency))
        for i in range(1, num_periods):
            self.add_cash_flow(i / self.frequency, self.face_value * self.coupon / self.frequency)
        self.add_cash_flow(self.maturity, self.face_value + self.face_value * self.coupon / self.frequency)


class Portfolio:
    def __init__(self):
        self.bills = []
        self.bonds = []
        self.cash_flows = []

    def add_bank_bill(self, bill):
        self.bills.append(bill)

    def add_bond(self, bond):
        self.bonds.append(bond)

    def set_cash_flows(self):
        self.cash_flows = []
        for bill in self.bills:
            self.cash_flows.extend(bill.get_cash_flows())
        for bond in self.bonds:
            self.cash_flows.extend(bond.get_cash_flows())

    def get_cash_flows(self):
        return self.cash_flows
    
    def get_bank_bills(self):
        return self.bills

    def get_bonds(self):
        return self.bonds

