import requests
import time
import json
from timer import Timer


MA_1 = 9  

WMA_1 = 120
WMA_2 = 13 

MACD_SIGNAL = 9
MACD_FAST = 12
MACD_SLOW = 26

MAX_CANDLESTICKS = 130  #kolichestvo svechey  500
CANDLESTICK_INTERVAL = '1m' #size of candlestick


def attempt_to_make_trade(current_price):  #only buy or sell and current price
    print(current_price, weighted_moving_average_line_1, macd_line_1, macd_signal_line_1)
    if next_operation_buy is None:
        try_to_buy(current_price)
        try_to_sell(current_price)
    elif next_operation_buy:
        try_to_buy(current_price, 1) 
    else: 
        try_to_sell(current_price, 1)


def moving_average(ma_size, lst=None):  #done
    lst = price_candlesticks if lst is None else lst
    return sum(lst[MAX_CANDLESTICKS-ma_size:])/ma_size

    
def weighted_moving_average(wma_size, lst=None): #done
    lst = price_candlesticks if lst is None else lst
    sum_weight_values, sum_weight = 0, 0
    for weight in range(1, wma_size+1):
        sum_weight_values += weight * lst[MAX_CANDLESTICKS-wma_size-1+weight]
        sum_weight += weight 
    return sum_weight_values / sum_weight

def macd():  #done
    macd_value = moving_average(MACD_FAST) - moving_average(MACD_SLOW)
    if t.is_ready():
        macd_buf.pop(0)
        macd_buf.append(macd_value)
        t.start()
        return moving_average(MACD_SIGNAL, macd_buf), macd_value
    return moving_average(MACD_SIGNAL, macd_buf[1:]+[macd_value]), macd_value 

""" def macd():  #done
    macd_value = weighted_moving_average(MACD_FAST) - weighted_moving_average(MACD_SLOW)
    if t.is_ready():
        macd_buf.pop(0)
        macd_buf.append(macd_value)
        t.start()
        return weighted_moving_average(MACD_SIGNAL, macd_buf), macd_value
    return moving_average(MACD_SIGNAL, macd_buf[1:]+[macd_value]), macd_value  """

def macd_start():
    for numb in range(MACD_SIGNAL,0,-1):
        macd_value = moving_average(MACD_FAST, [0]*numb+price_candlesticks[:-numb]) - moving_average(MACD_SLOW, [0]*numb+price_candlesticks[:-numb])
        macd_buf.pop(0)
        macd_buf.append(macd_value)

def try_to_buy(current_price, resol=None): #condition buy 
    global next_operation_buy 
    global last_price
    if resol is None:
        if current_price > weighted_moving_average_line_1 and macd_line_1 < 0 and macd_signal_line_1 < 0 and abs(macd_line_1 - macd_signal_line_1)  < 0.03:  
            place_buy_order(current_price)
            next_operation_buy = False 
            last_price = current_price
    else:
        if current_price - last_price > 6: #1 condition - stoploss
            place_buy_order(current_price, False)
            next_operation_buy = None
        if current_price > weighted_moving_average_line_2:  # profit
            place_buy_order(current_price, False)
            next_operation_buy = None 
  

def try_to_sell(current_price, resol=None):
    global next_operation_buy
    global last_price
    if resol is None:
        if current_price < weighted_moving_average_line_1 and macd_line_1 > 0 and macd_signal_line_1 > 0 and abs(macd_line_1 - macd_signal_line_1)  < 0.03: 
            place_sell_order(current_price)
            next_operation_buy = True
            last_price = current_price
    else:
        if last_price - current_price > 6 :    #1 condition - stoploss
            place_sell_order(current_price, False)
            next_operation_buy = None
        if current_price < weighted_moving_average_line_2:  # profit
            place_sell_order(current_price, False)
            next_operation_buy = None


def get_request(symb):
    url = 'https://api.binance.com'
    if symb == 'price':
        path =  '/api/v3/ticker/price'
        params = {'symbol': 'ETHUSDT'}
        return requests.get(url+path, params=params).json()['price']
    elif symb == 'price_candlesticks':
        path = '/api/v3/klines'
        params = {
            'symbol': 'ETHUSDT',
            'interval': f'{CANDLESTICK_INTERVAL}',
            'limit':f'{MAX_CANDLESTICKS}'
            }
        res = requests.get(url+path, params=params).json()
        return [float(res[numb][4]) for numb in range(MAX_CANDLESTICKS)]


def place_buy_order(current_price, first_step=True):
    print('Buy')
    with open('scalp_bot/journal.txt', 'a') as f:
        if first_step:
            f.write(f'{time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime())} Buy  - {current_price}$\n')
        else:
            f.write(f'{time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime())} Buy  - {current_price}$      {round((current_price-last_price)/last_price*100, 2)  if next_operation_buy is not None else 0}%\n')

def place_sell_order(current_price, first_step=True):
    print('sell')
    with open('scalp_bot/journal.txt', 'a') as f:
        if first_step:
            f.write(f'{time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime())} Sell - {current_price}$\n')
        else:
            f.write(f'{time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime())} Sell - {current_price}$      {round((last_price-current_price)/last_price*100, 2) if next_operation_buy is not None else 0}%\n')

def main():
    global price_candlesticks
    global moving_average_line_1
    global macd_line_1
    global macd_signal_line_1
    global weighted_moving_average_line_1
    global weighted_moving_average_line_2
    price_candlesticks = get_request('price_candlesticks')
    macd_start()   #counting previous values  
    while True:
        current_price = round(float(get_request('price')), 2)
        price_candlesticks = get_request('price_candlesticks')

        macd_signal_line_1, macd_line_1 = [round(x, 2) for x in macd()]
        weighted_moving_average_line_1 = round(weighted_moving_average(WMA_1), 2)    
        weighted_moving_average_line_2 = round(weighted_moving_average(WMA_2), 2)  

        attempt_to_make_trade(current_price)



next_operation_buy = None
last_price = 0
price_candlesticks = [0] * MAX_CANDLESTICKS
macd_buf = [0] * MAX_CANDLESTICKS
t = Timer(60)

macd_signal_line_1 = 0 
macd_line_1 = 0
moving_average_line_1 = 0 
weighted_moving_average_line_1 = 0 


if __name__ == '__main__':
    main()