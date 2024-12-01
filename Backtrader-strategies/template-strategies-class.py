# Created by LP
# Date: 2024-12-02
# Trade only the money you can't afford to lose
# Then go back to the mine
# And try again.
# This was coded with love <3

#TODO clarify correctedness
#TODO make templates for other kinds of tradings where I have more datasets

import backtrader as bt

class StrategyTemplate(bt.Strategy):
    params = (
        ('param1', 10),  # Example parameter, replace with your strategy-specific parameters
        ('param2', 20),
    )

    def __init__(self):
        # Placeholder for indicators
        self.indicator1 = None  # Replace with your indicators
        self.indicator2 = None
        self.order = None  # Tracks the current order
        self.trades = []  # Stores trade information
        self.equity_curve = []  # Tracks equity over time
        self.max_drawdown = 0  # Tracks max drawdown
        self.buy_signals = []
        self.sell_signals = []

    def log(self, txt, dt=None):
        """Logs any text with a timestamp."""
        dt = dt or self.datas[0].datetime.datetime(0)
        print(f'{dt.isoformat()} {txt}')

    def notify_order(self, order):
        """Logs order notifications."""
        if order.status in [order.Submitted, order.Accepted]:
            return  # Do nothing for Submitted/Accepted orders

        if order.status in [order.Completed]:
            if order.isbuy():
                self.log(f'BUY EXECUTED, Price: {order.executed.price}, Cost: {order.executed.value}, Comm: {order.executed.comm}')
                self.buy_signals.append((self.datas[0].datetime.datetime(0), order.executed.price))
            elif order.issell():
                self.log(f'SELL EXECUTED, Price: {order.executed.price}, Cost: {order.executed.value}, Comm: {order.executed.comm}')
                self.sell_signals.append((self.datas[0].datetime.datetime(0), order.executed.price))
                self.trades.append({
                    'date': self.datas[0].datetime.date(0).isoformat(),
                    'price': order.executed.price,
                    'pnl': order.executed.pnl
                })
            self.max_drawdown = max(self.max_drawdown, self.broker.getvalue() - order.executed.pnlcomm)

        elif order.status in [order.Canceled, order.Margin, order.Rejected]:
            self.log('Order Canceled/Margin/Rejected')

        self.order = None

    def notify_trade(self, trade):
        """Logs trade notifications."""
        if trade.isclosed:
            self.log(f'OPERATION PROFIT, GROSS {trade.pnl}, NET {trade.pnlcomm}')

    def next(self):
        """Defines logic for each new data point."""
        self.equity_curve.append(self.broker.getvalue())  # Track equity
        if self.order:
            return  # Skip if there is an active order

        # Placeholder for strategy logic
        # Example: if self.data.close[0] > self.indicator1[0]:
        #     self.order = self.buy()
