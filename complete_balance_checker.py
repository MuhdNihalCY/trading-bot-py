from dotenv import load_dotenv
import os
from binance.client import Client
import time
from datetime import datetime, timedelta

# Load .env file
load_dotenv()

def print_section(title):
    print("\n" + "="*50)
    print(title)
    print("="*50)

def check_all_balances(api_key, api_secret):
    try:
        print("\nConnecting to Binance...")
        client = Client(api_key, api_secret)

        # 1. Check Spot Wallet
        print_section("SPOT WALLET BALANCES")
        account = client.get_account()
        for balance in account['balances']:
            free = float(balance['free'])
            locked = float(balance['locked'])
            if free > 0 or locked > 0:
                print(f"\n{balance['asset']}:")
                print(f"  Available: {free}")
                print(f"  Locked: {locked}")

        # 2. Check Funding Wallet -
        print_section("RECENT DEPOSITS (Last 7 days)")
        coins = client.get_all_coins_info()
        end_time = int(time.time() * 1000)
        start_time = end_time - (7 * 24 * 60 * 60 * 1000)  # 7 days ago
        
        for coin in coins:
            try:
                history = client.get_deposit_history(coin=coin['coin'], startTime=start_time, endTime=end_time)
                for deposit in history:
                    if deposit['status'] == 1:  # Completed deposits
                        timestamp = datetime.fromtimestamp(deposit['insertTime']/1000)
                        print(f"\nCoin: {deposit['coin']}")
                        print(f"Amount: {deposit['amount']}")
                        print(f"Date: {timestamp}")
                        print(f"Status: Completed")
            except:
                continue

        # 3. Check Open Orders
        print_section("OPEN ORDERS")
        open_orders = client.get_open_orders()
        if open_orders:
            for order in open_orders:
                print(f"\nSymbol: {order['symbol']}")
                print(f"Type: {order['type']}")
                print(f"Side: {order['side']}")
                print(f"Quantity: {order['origQty']}")
        else:
            print("No open orders found")

        # 4. Check Recent Trades
        print_section("RECENT TRADES (Last 24 hours)")
        symbols = ['BTCUSDT', 'ETHUSDT', 'BNBUSDT']  # Add more pairs if needed
        for symbol in symbols:
            try:
                trades = client.get_my_trades(symbol=symbol, limit=5)
                for trade in trades:
                    trade_time = datetime.fromtimestamp(trade['time']/1000)
                    if trade_time > datetime.now() - timedelta(days=1):
                        print(f"\nSymbol: {symbol}")
                        print(f"Price: {trade['price']}")
                        print(f"Quantity: {trade['qty']}")
                        print(f"Time: {trade_time}")
            except:
                continue

    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    print("\n🔷 Binance Complete Balance Checker 🔷")
    
    # Replace with your API keys
    api_key = os.getenv("API_KEY")
    api_secret = os.getenv("API_SECRET")
    
    while True:
        check_all_balances(api_key, api_secret)
        print("\nRefreshing in 30 seconds...")
        time.sleep(30)