from dotenv import load_dotenv
import os
from binance.client import Client
from binance.enums import *
import pandas as pd
import numpy as np
import time
from datetime import datetime
import logging
import json

# Load .env file
load_dotenv()

class CryptoTradingBot:
    def __init__(self, api_key, api_secret, symbol='BTCUSDT', interval='1h'):
        """
        Initialize the trading bot with Binance credentials and trading parameters
        """
        # Set up logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('trading_bot.log'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
        
        # Connect to Binance
        self.logger.info("Connecting to Binance...")
        self.client = Client(api_key, api_secret)
        self.symbol = symbol
        self.interval = interval
        
        # Trading parameters
        self.quantity = 0.001  # Minimum BTC trading quantity
        self.moving_avg_short = 20
        self.moving_avg_long = 50
        
        # Create results directory
        if not os.path.exists('trading_results'):
            os.makedirs('trading_results')
            
    def save_market_data(self, df):
        """
        Save market data to CSV file
        """
        filename = f'trading_results/market_data_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv'
        df.to_csv(filename)
        self.logger.info(f"Market data saved to {filename}")
        
    def get_historical_data(self):
        """
        Fetch historical klines/candlestick data
        """
        self.logger.info(f"Fetching historical data for {self.symbol}...")
        try:
            klines = self.client.get_historical_klines(
                self.symbol,
                self.interval,
                f"{self.moving_avg_long} hours ago UTC"
            )
            
            df = pd.DataFrame(klines, columns=[
                'timestamp', 'open', 'high', 'low', 'close',
                'volume', 'close_time', 'quote_volume', 'trades',
                'taker_buy_base', 'taker_buy_quote', 'ignore'
            ])
            
            df['close'] = pd.to_numeric(df['close'])
            df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
            
            self.logger.info("Historical data fetched successfully")
            return df
            
        except Exception as e:
            self.logger.error(f"Error fetching historical data: {e}")
            return None
    
    def calculate_signals(self, df):
        """
        Calculate trading signals based on moving average crossover
        """
        self.logger.info("Calculating trading signals...")
        try:
            df['MA_short'] = df['close'].rolling(window=self.moving_avg_short).mean()
            df['MA_long'] = df['close'].rolling(window=self.moving_avg_long).mean()
            
            df['signal'] = 0
            df.loc[df['MA_short'] > df['MA_long'], 'signal'] = 1
            df.loc[df['MA_short'] < df['MA_long'], 'signal'] = -1
            
            # Print current market conditions
            current_price = df['close'].iloc[-1]
            current_ma_short = df['MA_short'].iloc[-1]
            current_ma_long = df['MA_long'].iloc[-1]
            
            self.logger.info(f"""
Current Market Conditions:
------------------------
Price: {current_price:.2f}
Short MA ({self.moving_avg_short}): {current_ma_short:.2f}
Long MA ({self.moving_avg_long}): {current_ma_long:.2f}
            """)
            
            return df
            
        except Exception as e:
            self.logger.error(f"Error calculating signals: {e}")
            return None
    
    def check_account_balance(self):
        """
        Check account balance for both USDT and the trading asset
        """
        self.logger.info("Checking account balance...")
        try:
            account = self.client.get_account()
            balances = {
                asset['asset']: {
                    'free': float(asset['free']),
                    'locked': float(asset['locked'])
                }
                for asset in account['balances']
                if float(asset['free']) > 0 or float(asset['locked']) > 0
            }
            
            # Log balances
            self.logger.info("Current Balances:")
            for asset, balance in balances.items():
                self.logger.info(f"{asset}: Free = {balance['free']}, Locked = {balance['locked']}")
                
            return balances
            
        except Exception as e:
            self.logger.error(f"Error checking balance: {e}")
            return None
    
    def place_order(self, side, quantity):
        """
        Place a market order
        """
        self.logger.info(f"Attempting to place {side} order for {quantity} {self.symbol}...")
        try:
            order = self.client.create_order(
                symbol=self.symbol,
                side=side,
                type=ORDER_TYPE_MARKET,
                quantity=quantity
            )
            
            # Save order details
            order_filename = f'trading_results/order_{order["orderId"]}.json'
            with open(order_filename, 'w') as f:
                json.dump(order, f, indent=4)
            
            self.logger.info(f"""
Order Placed Successfully:
------------------------
Order ID: {order['orderId']}
Type: {side}
Quantity: {quantity}
Symbol: {self.symbol}
Status: {order['status']}
Details saved to: {order_filename}
            """)
            return order
            
        except Exception as e:
            self.logger.error(f"Error placing order: {e}")
            return None
    
    def run_bot(self):
        """
        Main bot loop
        """
        self.logger.info(f"""
Starting Trading Bot
-------------------
Symbol: {self.symbol}
Interval: {self.interval}
Short MA Period: {self.moving_avg_short}
Long MA Period: {self.moving_avg_long}
Trading Quantity: {self.quantity}
        """)
        
        while True:
            try:
                # Get historical data and calculate signals
                df = self.get_historical_data()
                if df is not None:
                    df = self.calculate_signals(df)
                    self.save_market_data(df)
                    
                    # Get latest signal
                    current_signal = df['signal'].iloc[-1]
                    previous_signal = df['signal'].iloc[-2]
                    
                    self.logger.info(f"""
Signal Analysis:
---------------
Previous Signal: {previous_signal}
Current Signal: {current_signal}
                    """)
                    
                    # Check if signal changed
                    if current_signal != previous_signal:
                        balances = self.check_account_balance()
                        
                        if current_signal == 1 and previous_signal == -1:  # Buy signal
                            self.logger.info("BUY SIGNAL DETECTED!")
                            if balances and 'USDT' in balances:
                                self.place_order(SIDE_BUY, self.quantity)
                                
                        elif current_signal == -1 and previous_signal == 1:  # Sell signal
                            self.logger.info("SELL SIGNAL DETECTED!")
                            base_asset = self.symbol.replace('USDT', '')
                            if balances and base_asset in balances:
                                self.place_order(SIDE_SELL, self.quantity)
                
                # Wait for next interval
                self.logger.info("Waiting for next check...")
                time.sleep(60)  # Check every minute
                
            except Exception as e:
                self.logger.error(f"Error in main loop: {e}")
                time.sleep(60)  # Wait before retrying

# Example usage
if __name__ == "__main__":
    print("""
╔════════════════════════════════════════╗
║        Crypto Trading Bot v1.0         ║
╚════════════════════════════════════════╝
    """)
    
    # Get API credentials from 
    api_key = os.getenv("API_KEY")
    api_secret = os.getenv("API_SECRET")
     
    # Get trading pair from user
    symbol = input("Enter trading pair (default BTCUSDT): ") or "BTCUSDT"
    
    # Initialize and run bot
    bot = CryptoTradingBot(
        api_key=api_key,
        api_secret=api_secret,
        symbol=symbol,
        interval='1h'
    )
    bot.run_bot()
