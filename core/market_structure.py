class MarketStructure:

    def __init__(self, candles):
        self.candles = candles

    def detect_bos(self):
        highs = [c['high'] for c in self.candles]

        if highs[-1] > highs[-2]:
            return "bullish_bos"

        return None

    def detect_choch(self):
        lows = [c['low'] for c in self.candles]

        if lows[-1] < lows[-2]:
            return "bearish_choch"

        return None