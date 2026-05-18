class LiquidityDetector:

    def __init__(self, candles):
        self.candles = candles

    def detect_liquidity_grab(self):

        highs = [c['high'] for c in self.candles]

        if highs[-1] > max(highs[-10:-1]):
            return True

        return False