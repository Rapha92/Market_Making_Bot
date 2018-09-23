#### Kucoin / Binance Arbitrage Trading Bot

# Import Libraries
import pandas as pd
from kucoin.client import Client as KUC_Client
from binance.client import Client as BIN_Client

#### API Keys ####
#### Kucoin   ####
KUC_key = #insert key here
KUC_secret = #insert key here
KUC_client =  KUC_Client(KUC_key, KUC_secret)
KUC_trading_fee = 0.001

BIN_key = #insert key here
BIN_secret = #insert key here
BIN_client = BIN_Client(BIN_key, BIN_secret)
BIN_trading_fee = 0.001


### Setting up Artificial Account Balances
Account_BIN = {"NEO": 100,"ETC": 100,"EOS": 100 ,"LTC": 100, "NANO": 100 , "QSP": 100, "DASH": 100}
Account_KUC = {"NEO": 100,"ETC": 100,"EOS": 100 ,"LTC": 100, "NANO": 100 , "QSP": 100, "DASH": 100}

#### Kucoin - Get Orderbook
######IMPROVEMENT USE MORE VALUES TO CALCULATE ARBITRAGE PRICE ###############
def check_market():
    currencies = ["NEO-ETH","ETC-ETH","EOS-ETH","LTC-ETH", "NANO-ETH", "QSP-ETH", "DASH-ETH"]
    KUC_BUY_Repository = {}
    KUC_SELL_Repository = {}
    for i in currencies:
        KUC_depth = KUC_client.get_order_book(i, limit = 5)
        KUC_SELL = KUC_depth["BUY"]
        KUC_BUY = KUC_depth["SELL"]
        KUC_BUY_Repository[i] = KUC_BUY[0]
        KUC_SELL_Repository[i] = KUC_SELL[0]
        
    BIN_BUY_Repository = {}
    BIN_SELL_Repository = {}  
    for i in currencies:
        symbol = i.replace('-','')
        BIN_depth = BIN_client.get_order_book(symbol= symbol, limit = 5)
        BIN_SELL = BIN_depth["bids"]
        BIN_BUY = BIN_depth["asks"]
        BIN_BUY_Repository[i] = BIN_BUY[0]
        BIN_SELL_Repository[i] = BIN_SELL[0]
    # The bid price represents the maximum price that a buyer is willing to pay for a security. The ask price represents the minimum price that a seller is willing to receive.
        
    BIN_SELL_Repository = {key:[ float(i) for i in BIN_SELL_Repository[key][:2] ] for key in BIN_SELL_Repository}
    BIN_BUY_Repository = {key:[ float(i) for i in BIN_SELL_Repository[key][:2] ] for key in BIN_SELL_Repository}
    
    Exchange_1 = []
    Exchange_2 = []
    Currency = []
    Spread_abs = []
    Spread_perc = []
    pot_return = []
    volume_1 = []
    volume_2= []
    for j in ["BIN", "KUC"]:
        for x in ["BIN", "KUC"]:
            for y in currencies:
                Exchange_1.append( j)
                Exchange_2.append(x)
                Currency.append(y)
                fee_1 = globals()[j +'_trading_fee' ]
                fee_2 = globals()[x +'_trading_fee' ]
                Sell = globals()[j +'_SELL_Repository' ] [y][0]
                Buy = globals()[x +'_BUY_Repository' ] [y][0]
                spread_v =  Sell - Buy
                spread_p =  (Sell - Buy) / Sell
                volume_j = globals()[j +'_SELL_Repository' ] [y][1]
                volume_x = globals()[x +'_BUY_Repository' ] [y][1]
                volume_1.append(volume_j)
                volume_2.append(volume_x)
                Spread_abs.append(spread_v)
                Spread_perc.append(spread_p)
                r = spread_p - fee_1 - fee_2
                pot_return.append(r)
    spreads = pd.DataFrame({"Sell_Exchange_1": Exchange_1, "Buy_Exchange_2": Exchange_2,"Volume_1": volume_1, "Volume_2": volume_2, "Currency": Currency,"Spread_abs": Spread_abs,"Spread_perc": Spread_perc, "pot_return": pot_return }).sort_values("pot_return")
    best_spread = spreads[(len(spreads) - 1):len(spreads)]
    return(spreads, best_spread)

### Setting up Artificial Account Balances
Account_BIN = {"NEO": 100,"ETC": 100,"EOS": 100 ,"LTC": 100, "NANO": 100 , "QSP": 100, "DASH": 100}
Account_KUC = {"NEO": 100,"ETC": 100,"EOS": 100 ,"LTC": 100, "NANO": 100 , "QSP": 100, "DASH": 100}

def execute_trade(sell_price, buy_price,symbol_KUC, sell_exchange, buy_exchange, sell_volume):             
        if ((sell_price - buy_price) / sell_price) - (BIN_trading_fee * KUC_trading_fee) > 0.00:
            #### Sell
            coins = symbol_KUC.split("-")
            sell_currency = coins[0]
            buy_currency  = coins[1]
            sell_ammount = sell_exchange[sell_currency]  if (sell_exchange[sell_currency] < sell_volume) else sell_volume
            sell_exchange[sell_currency] = sell_exchange[sell_currency] - sell_ammount
            sell_exchange[buy_currency] = sell_exchange[buy_currency] + (sell_ammount * sell_price * 0.999)           
            
            #####Buy
            coins_2 = symbol_KUC.split("-")
            buy_currency_2 = coins[0]
            sell_currency_2 = coins[1]
            buy_ammount_2 = sell_ammount
            buy_exchange[sell_currency_2] = sell_currency_2 - buy_amount_2
            buy_exchange[buy_currency_2] = buy_exchange[buy_currency_2] + (buy_ammount_2 * buy_price * 0.999)
            
            
            ### Equalize the exchanges
            buy_exchange[buy_currency] = buy_exchange[buy_currency] + sell_exchange[buy_currency]-100
            sell_exchange[buy_currency] = 100
            
            sell_exchange[buy_currency_2] = sell_exchange[buy_currency_2] + buy_exchange[buy_currency_2] - 100
            buy_exchange[buy_currency_2] = 100


        
def watch_stocks(best_spread):        
        sell_exchange = "Account_" + best_spread["Sell_Exchange_1"][0]
        buy_exchange = "Account_"  + best_spread["Buy_Exchange_2"][0]
        symbol_KUC = best_spread.loc[best_spread.index[0], 'Currency']
        symbol_BIN = best_spread.loc[best_spread.index[0], 'Currency'].replace('-','')       
        if sell_exchange == "Account_BIN":
            sell_price = float(BIN_client.get_order_book(symbol = symbol_BIN, limit = 5)["bids"][0][0])
            sell_volume = float(BIN_client.get_order_book(symbol = symbol_BIN, limit = 5)["bids"][0][1])
            
            if buy_exchange == "Account_BIN":
                buy_price = float(BIN_client.get_order_book(symbol = symbol_BIN, limit = 5)["asks"][0][0])
                buy_volume = float(BIN_client.get_order_book(symbol = symbol_BIN, limit = 5)["asks"][0][1])                
            else:
                buy_price = KUC_client.get_order_book(symbol = symbol_KUC, limit = 5)["SELL"][0][0]
                buy_volume = KUC_client.get_order_book(symbol = symbol_KUC, limit = 5)["SELL"][0][1] 

        else:
            sell_price = KUC_client.get_order_book(symbol = symbol_KUC, limit = 5)["BUY"][0][0]
            sell_volume = KUC_client.get_order_book(symbol = symbol_KUC, limit = 5)["BUY"][0][1]
            if buy_exchange == "Account_BIN":
                buy_price = float(BIN_client.get_order_book(symbol = symbol_BIN, limit = 5)["asks"][0][0])
                buy_volume = float(BIN_client.get_order_book(symbol = symbol_BIN, limit = 5)["asks"][0][1])                
            else:
                buy_price = KUC_client.get_order_book(symbol = symbol_KUC, limit = 5)["SELL"][0][0]
                buy_volume = KUC_client.get_order_book(symbol = symbol_KUC, limit = 5)["SELL"][0][1] 
        return(sell_price, buy_price_symbol_KUC, sell_exchange, buy_exchange, sell_volume)
    

import time
try:
    while True:
        start = time.time()
        check_market()
        if best_spread["pot_return"][0] > 0:
            watch_stocks()
            execute_trade(sell_price, buy_price,symbol_KUC, sell_exchange, buy_exchange)
            print("traded")
        else:
            print("continue")
        stop = time.time()
        print(stop-start)
except KeyboardInterrupt:
    print('Manual break by user')        
            
            
            
            
            
            
            
            
            
            
            
            
            
            
        
