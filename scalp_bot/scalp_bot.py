import requests
import time
import json
from config import host, port, user, password,  db_name


MA_1 = 75 #125 and 500 good   
MA_2 = 330



on_wma = False
on_ma = True



def attempt_to_make_trade(numb):
    global last_price
    
    current_price = get_market_prices()
    if on_ma:
        moving_average(current_price, numb)
#    elif on_wma:
 #       weighted_moving_average(current_price, numb)  

    try_to_buy(current_price) if next_operation_buy else try_to_sell(current_price)
    last_price = current_price


def moving_average(current_price, numb):
    global moving_average_1_greather
    last_prices[numb] = current_price
    if numb > MA_1-1:
        average_1 = sum(last_prices[numb-MA_1:numb])/MA_1   
    else:
        average_1 = (sum(last_prices[:numb])+sum(last_prices[MA_2-MA_1+numb:]))/MA_1

    average_2 = sum(last_prices)/MA_2
    moving_average_1_greather = True if average_1 > average_2 else False 
    print(average_1, average_2)
    #with open('scalp_bot/grafics.txt', 'a') as f:
       # f.write(f'{current_price}   {average_1}   {average_2}   {numb}\n')

#def  weighted_moving_average(current_price, numb):
 #   global weighted_moving_average_1_greather
  #  last_prices[numb] = current_price
   # if numb > MA_1-1:
    #    average_1 = [for x in range(MA_1)]

def getting_ready():
    while last_prices[-1] == 0:
        for num in range(MA_2):
            current_price = get_market_prices()
            moving_average(current_price, num)
            print("waiting")

def try_to_sell(current_price):
    if not moving_average_1_greather:
        global next_operation_buy
        next_operation_buy = True
        place_sell_order(current_price)


def try_to_buy(current_price):
    if moving_average_1_greather:
        global next_operation_buy
        next_operation_buy = False
        place_buy_order(current_price)
        
def get_request(symb):
    url = 'https://api.binance.com'
    if symb == 'price':
        path =  '/api/v3/ticker/price'
        params = {'symbol': 'ETHUSDT'}
    requests.get(url+path, params=params).json()

def get_market_prices():
    res = get_request('price')
    print(res['price'])
    return float(res['price'])


def place_buy_order(current_price):
    global last_buy_price
    print('Buy')
    last_buy_price = current_price
    with open('scalp_bot/journal.txt', 'a') as f:
        f.write(f'{time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime())} Buy  - {current_price}$\n')


def place_sell_order(current_price):
    print('sell')
    with open('scalp_bot/journal.txt', 'a') as f:
        f.write(f'{time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime())} Sell - {current_price}$  --- {(current_price-last_buy_price)*100/last_buy_price}%\n')


def main():
    getting_ready()
    while True:
        for numb in range(MA_2):   #moving average
            attempt_to_make_trade(numb)
            time.sleep(0.9)

last_price = get_market_prices()
moving_average_1_greather = False
weighted_moving_average_1_greather = False
next_operation_buy = True
last_prices = [0] * MA_2
last_buy_price = 0
count_lst = list(range(MA_2))

if __name__ == '__main__':
    main() 