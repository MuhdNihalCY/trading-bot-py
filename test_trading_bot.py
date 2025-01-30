from dotenv import load_dotenv
import os
import pandas as pd
import numpy as np
import time
from datetime import datetime
import logging
import json

# Load .env file
load_dotenv()

class CryptoTradingBot:
    def __init__(self, symbol='BTCUSDT', interval='1h', simulation_mode=True, initial_balance=10000):
        """
        Initialize the trading bot with Binance credentials and trading parameters
        """
        # Set up logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('trading_bot_simulation.log'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
        
        # Simulation settings
        self.simulation_mode = simulation_mode
        self.symbol = symbol
        self.interval = interval
        self.quantity = 0.001  # Simulated trading quantity
        self.moving_avg_short = 20
        self.moving_avg_long = 50

        # Digital account simulation
        self.digital_balance = {"USDT": initial_balance, self.symbol.replace("USDT", ""): 0}  # e.g., {"USDT": 10000, "BTC": 0}
        self.trade_log = []  # Track all trades
        
        # Create results directory
        if not os.path.exists('simulation_results'):
            os.makedirs('simulation_results')
            
    def save_trade_log(self):
        """
        Save trade logs to a JSON file
        """
        filename = f'simulation_results/trade_log_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json'
        with open(filename, 'w') as f:
            json.dump(self.trade_log, f, indent=4)
        self.logger.info(f"Trade log saved to {filename}")
        
    def get_historical_data(self):
        """
        Simulate fetching historical klines/candlestick data
        """
        self.logger.info(f"Fetching simulated historical data for {self.symbol}...")
        # Simulate historical price data
        timestamp = pd.date_range(end=datetime.now(), periods=self.moving_avg_long + 10, freq='h')
        close = np.random.normal(loc=30000, scale=1000, size=len(timestamp))  # Simulate BTC price ~30k
        df = pd.DataFrame({"timestamp": timestamp, "close": close})
        self.logger.info("Simulated historical data generated successfully")
        return df
    
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
            
            return df
            
        except Exception as e:
            self.logger.error(f"Error calculating signals: {e}")
            return None

        def place_order_simulation(self, side, quantity, price):
            """
            Simulate placing a market order
            """
            base_asset = self.symbol.replace('USDT', '')
            self.logger.info(f"Simulating {side} order for {quantity} {self.symbol} at price {price}...")

            if side == "BUY":
                cost = quantity * price
                if self.digital_balance["USDT"] >= cost:
                    self.digital_balance["USDT"] -= cost
                    self.digital_balance[base_asset] += quantity
                    self.trade_log.append({"type": "BUY", "quantity": quantity, "price": price, "balance": dict(self.digital_balance)})
                    self.logger.info(f"Simulated BUY order completed.")
                else:
                    self.logger.warning("Not enough USDT for the simulated BUY order.")

            elif side == "SELL":
                if self.digital_balance[base_asset] >= quantity:
                    self.digital_balance[base_asset] -= quantity
                    self.digital_balance["USDT"] += quantity * price
                    self.trade_log.append({"type": "SELL", "quantity": quantity, "price": price, "balance": dict(self.digital_balance)})
                    self.logger.info(f"Simulated SELL order completed.")
                else:
                    self.logger.warning("Not enough BTC for the simulated SELL order.")

            # Log updated balance after every order
            self.log_current_balance()
    def log_current_balance(self):
        """
        Log the current simulated balance
        """
        self.logger.info("Current Balance:")
        for asset, balance in self.digital_balance.items():
            self.logger.info(f"{asset}: {balance:.6f}")
            
    def run_bot(self):
        """
        Main bot loop in simulation mode
        """
        self.logger.info(f"""
Starting Simulation Trading Bot
-------------------
Symbol: {self.symbol}
Interval: {self.interval}
Short MA Period: {self.moving_avg_short}
Long MA Period: {self.moving_avg_long}
Trading Quantity: {self.quantity}
Initial Balance: {self.digital_balance}
        """)
        
        while True:
            try:
                # Get historical data and calculate signals
                df = self.get_historical_data()
                if df is not None:
                    df = self.calculate_signals(df)
                    
                    # Log current balance
                    self.log_current_balance()

                    # Get latest signal
                    current_signal = df['signal'].iloc[-1]
                    previous_signal = df['signal'].iloc[-2]
                    
                    self.logger.info(f"Previous Signal: {previous_signal}, Current Signal: {current_signal}")
                    
                    # Check if signal changed
                    if current_signal != previous_signal:
                        # Get current price
                        current_price = df['close'].iloc[-1]
                        
                        if current_signal == 1 and previous_signal == -1:  # Buy signal
                            self.logger.info("BUY SIGNAL DETECTED!")
                            self.place_order_simulation("BUY", self.quantity, current_price)
                                
                        elif current_signal == -1 and previous_signal == 1:  # Sell signal
                            self.logger.info("SELL SIGNAL DETECTED!")
                            self.place_order_simulation("SELL", self.quantity, current_price)
                
                # Save trade log and wait
                self.save_trade_log()
                self.logger.info("Waiting for next simulation interval...")
                time.sleep(60)  # Simulate interval (in seconds)
                
            except Exception as e:
                self.logger.error(f"Error in simulation loop: {e}")
                time.sleep(60)  # Wait before retrying
                

# Example usage
if __name__ == "__main__":
    print("""
╔════════════════════════════════════════╗
║      Crypto Trading Bot (Simulation)   ║
╚════════════════════════════════════════╝
    """)
    
    # Initialize and run bot
    bot = CryptoTradingBot(
        symbol="BTCUSDT",
        interval='1h',
        simulation_mode=True,
        initial_balance=10000
    )
    bot.run_bot()