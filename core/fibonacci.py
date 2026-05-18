class Fibonacci:

    def __init__(self, high, low):
        self.high = high
        self.low = low
        self.range = high - low

    def calculate_levels(self):

        return {
            "0": self.high,
            "0.5": self.high - self.range * 0.5,
            "0.705": self.high - self.range * 0.705,
            "0.79": self.high - self.range * 0.79,
            "0.886": self.high - self.range * 0.886,
            "1": self.low,
            "-0.27": self.high + self.range * 0.27,
            "-0.618": self.high + self.range * 0.618,
        }