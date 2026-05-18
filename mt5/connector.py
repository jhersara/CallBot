import MetaTrader5 as mt5

class MT5Connector:

    def __init__(self):
        self.connected = False

    def connect(self):
        if not mt5.initialize():
            print("Error conectando MT5")
            return False

        self.connected = True
        print("MT5 conectado")
        return True

    def shutdown(self):
        mt5.shutdown()
        self.connected = False

    def get_account_info(self):
        return mt5.account_info()

    def get_symbol_data(self, symbol="XAUUSD", timeframe=mt5.TIMEFRAME_M1, bars=500):
        rates = mt5.copy_rates_from_pos(symbol, timeframe, 0, bars)
        return rates