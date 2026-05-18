class RiskManager:

    def __init__(self, balance, risk_percent=1):
        self.balance = balance
        self.risk_percent = risk_percent

    def calculate_risk_amount(self):
        return self.balance * (self.risk_percent / 100)

    def calculate_lot_size(self, stop_loss_pips, pip_value):
        risk_amount = self.calculate_risk_amount()

        lot_size = risk_amount / (stop_loss_pips * pip_value)

        return round(lot_size, 2)