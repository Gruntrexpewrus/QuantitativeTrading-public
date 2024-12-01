# Created by LP
# Date: 2024-12-02
# Trade only the money you can't afford to lose
# Then go back to the mine
# And try again.
# This was coded with love <3


#TODO make a stupid one so that I can backtest
#TODO make a stupid one with a ML model generating random stuff in future, check how to integrate with torch

class StrategyLogic:
    def __init__(self, param1=10, param2=20):
        self.param1 = param1
        self.param2 = param2
        self.previous_data = []

    def calculate_signals(self, data):
        """
        Calculate buy/sell/hold signals based on data.
        :param data: List or array of prices or other relevant data.
        :return: 'buy', 'sell', or 'hold'
        """
        # Replace with strategy
        if len(data) < self.param1:
            return 'hold'  # Not enough data
        if data[-1] > sum(data[-self.param1:]) / self.param1:
            return 'buy'
        elif data[-1] < sum(data[-self.param1:]) / self.param1:
            return 'sell'
        return 'hold'
