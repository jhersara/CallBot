from mt5.connector import MT5Connector
from core.market_structure import MarketStructure
from core.fibonacci import Fibonacci
from core.risk_manager import RiskManager


def main():

    connector = MT5Connector()

    if not connector.connect():
        return

    account = connector.get_account_info()

    print(account)

    candles = connector.get_symbol_data()

    market = MarketStructure(candles)

    bos = market.detect_bos()
    choch = market.detect_choch()

    print("BOS:", bos)
    print("CHOCH:", choch)

    risk = RiskManager(balance=account.balance)

    print("Risk Amount:", risk.calculate_risk_amount())


if __name__ == "__main__":
    main()