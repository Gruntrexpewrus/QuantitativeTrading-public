# Created by LP
# Date: 2024-12-02
# Trade only the money you can't afford to lose
# Then go back to the mine
# And try again.
# This was coded with love <3


import ccxt
import datetime
import signal
import sys
import time
import json
from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.triggers.cron import CronTrigger
from encrypted.encryption import load_keys

#TODO run one on testnet
#TODO clarify wtf is going on with the api data collection
#TODO make sure the both focuses its activity around the shift in timeframe like the data collection bot
#TODO in a future make a telegram interaction


# Load API keys
path_secret = "/path/to/your/encrypted_secret.key"
path_keys = "/path/to/your/encrypted_keys.txt"
APIKEY, SECRET = load_keys(path_secret, path_keys)

# Load configuration
with open('/path/to/your/config.json', 'r') as f:
    config = json.load(f)

SYMBOL = config["symbol"]
STRATEGY_PARAMS = config["strategy_parameters"]
public_wallet = config["public_wallet"]

# Initialize the exchange
#TODO I think this below is wrong, I need to check the local file on ccxt I did to setup leverage in particular!
exchange = ccxt.hyperliquid({
    'apiKey': APIKEY,
    'secret': SECRET,
    'privateKey': SECRET,
    'walletAddress': public_wallet,
    'options': {
        'defaultSlippage': 0.05,  # Default slippage percentage (5%)
        'leverage': {'type': 'isolated', 'value': '5'}
    },
})
exchange.set_sandbox_mode(True)  # Enable sandbox mode
exchange.enableRateLimit = True  # Enable rate-limiting

def calculate_since(timeframe, dataset_size):
    """
    Calculate the `since` timestamp aligned with the exact start of the current timeframe.
    
    :param timeframe: The timeframe string (e.g., '1m', '15m', '1h', '1d').
    :param dataset_size: The number of periods (candlesticks) to fetch.
    :return: The `since` timestamp in milliseconds.
    """
    timeframe_to_ms = {
        '1m': 60 * 1000,
        '5m': 5 * 60 * 1000,
        '15m': 15 * 60 * 1000,
        '1h': 60 * 60 * 1000,
        '4h': 4 * 60 * 60 * 1000,
        '1d': 24 * 60 * 60 * 1000,
    }
    
    if timeframe not in timeframe_to_ms:
        raise ValueError(f"Unsupported timeframe: {timeframe}")
    
    # Get the duration of one timeframe in milliseconds
    timeframe_ms = timeframe_to_ms[timeframe]
    
    # Get the current timestamp in milliseconds
    current_timestamp_ms = int(time.time() * 1000)
    
    # Align the current timestamp to the start of the current timeframe
    aligned_timestamp_ms = current_timestamp_ms - (current_timestamp_ms % timeframe_ms)
    
    # Calculate the `since` timestamp for the required dataset size
    since_timestamp_ms = aligned_timestamp_ms - (timeframe_ms * dataset_size)
    
    return since_timestamp_ms


# Strategy Logic Class
class StrategyLogic:
    def __init__(self, **params):
        self.params = params
    #import the strategy from the strategy reusable you backtested!

# Trading Bot Class
class TradingBot:
    def __init__(self, exchange, symbol, strategy_logic, timeframe, amount):
        self.exchange = exchange
        self.symbol = symbol
        self.strategy = strategy_logic
        self.timeframe = timeframe
        self.amount = amount
        self.data = self.fetch_historical_data()
        self.order = None

        # Handle graceful shutdown
        signal.signal(signal.SIGINT, self.signal_handler)
        signal.signal(signal.SIGTERM, self.signal_handler)

    def fetch_historical_data(self):
        since = calculate_since(self.timeframe, self.strategy.params['sma_period'])
        ohlcv = self.exchange.fetch_ohlcv(self.symbol, timeframe=self.timeframe, since=since)
        return [{'timestamp': x[0], 'open': x[1], 'high': x[2], 'low': x[3], 'close': x[4], 'volume': x[5]} for x in ohlcv]

    def fetch_new_data(self):
        try:
            ohlcv = self.exchange.fetch_ohlcv(self.symbol, timeframe=self.timeframe, limit=self.strategy.params['sma_period'])
            new_data = [{'timestamp': x[0], 'open': x[1], 'high': x[2], 'low': x[3], 'close': x[4], 'volume': x[5]} for x in ohlcv]
            self.data = new_data[-self.strategy.params['sma_period']:]
            return True
        except Exception as e:
            print(f"Error fetching new data: {e}")
            return False

    def execute_trade(self, side):
        try:
            order = self.exchange.create_order(self.symbol, 'market', side, self.amount)
            print(f'{datetime.datetime.now(datetime.timezone.utc)}: {side.upper()} ORDER EXECUTED: {order}')
        except Exception as e:
            print(f"Error executing trade: {e}")

    def run_strategy(self):
        #TODO this one sucks, make similar to dataset colelction bot
        print(f'{datetime.datetime.now(datetime.timezone.utc)}: Running strategy...')
        if self.fetch_new_data():
            #use strategy
            pass

    def close_all_positions(self):
        try:
            positions = self.exchange.fetch_positions()
            for position in positions:
                amt = float(position['info']['position']['positionValue'])
                side = 'sell' if amt > 0 else 'buy'
                self.execute_trade(side)
            print("All positions closed.")
        except Exception as e:
            print(f"Error closing positions: {e}")

    def signal_handler(self, signum, frame):
        print("Signal received, closing all positions...")
        self.close_all_positions()
        sys.exit(0)

# Initialize the bot
strategy_logic = StrategyLogic(**STRATEGY_PARAMS)
bot = TradingBot(exchange=exchange, symbol=SYMBOL, strategy_logic=strategy_logic, timeframe=config["timeframe"], amount=config["amount"])

# Scheduler
scheduler = BlockingScheduler()
scheduler.add_job(bot.run_strategy, CronTrigger(second='0/1'))
scheduler.start()
