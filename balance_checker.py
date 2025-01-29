from dotenv import load_dotenv
import os
from binance.client import Client
import time

# Load .env file
load_dotenv()

def check_balance(api_key, api_secret):
    try:
        # Connect to Binance
        print("\nConnecting to Binance...")
        client = Client(api_key, api_secret)
        
        try:
            # Test connection
            status = client.get_system_status()
            print("Connection successful!")
        except Exception as e:
            print(f"Connection test failed: {e}")
            return
            
        try:
            # Get account information
            print("Checking balance...")
            account = client.get_account()
            
            # Print all balances that are greater than 0
            print("\nYour current balances:")
            print("----------------------")
            found_balance = False
            for balance in account['balances']:
                free_balance = float(balance['free'])
                locked_balance = float(balance['locked'])
                if free_balance > 0 or locked_balance > 0:
                    found_balance = True
                    print(f"{balance['asset']}:")
                    print(f"  Free: {free_balance}")
                    print(f"  Locked: {locked_balance}")
                    print("----------------------")
            
            if not found_balance:
                print("No non-zero balances found.")
                
        except Exception as e:
            print(f"Error getting account info: {e}")

    except Exception as e:
        print(f"Failed to initialize client: {e}")

if __name__ == "__main__":
    print("===============================")
    print("   Binance Balance Checker    ")
    print("===============================")
    
    # Get API credentials
    api_key = os.getenv("API_KEY")
    api_secret = os.getenv("API_SECRET")
    
    print("\nStarting balance checker...")
    while True:
        check_balance(api_key, api_secret)
        print("\nWaiting 10 seconds before next update...")
        for i in range(10, 0, -1):
            print(f"Next update in {i} seconds...", end='\r')
            time.sleep(1)
    
   