class OrderBlockDetector:

    def __init__(self, candles):
        self.candles = candles

    def detect_bullish_ob(self):

        for candle in reversed(self.candles[-10:]):
            if candle['close'] < candle['open']:
                return candle

        return None