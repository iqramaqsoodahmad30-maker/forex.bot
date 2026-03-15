import MetaTrader5 as mt5
import time
import pandas as pd

# -----------------------------
# CONNECT TO MT5
# -----------------------------
if not mt5.initialize():
    print("MT5 initialization failed")
    quit()

print("Connected to MT5")

symbol = "EURUSDm"
lot = 0.01
max_trades = 3
trade_count = 0

# enable symbol
if not mt5.symbol_select(symbol, True):
    print("Symbol not available")
    mt5.shutdown()
    quit()

# -----------------------------
# BOT LOOP
# -----------------------------
while True:

    print("Checking market...")

    # -----------------------------
    # CHECK OPEN POSITIONS
    # -----------------------------
    positions = mt5.positions_get(symbol=symbol)

    if positions is not None and len(positions) > 0:
        print("Trade already running")
        time.sleep(60)
        continue

    # -----------------------------
    # MAX TRADES LIMIT
    # -----------------------------
    if trade_count >= max_trades:
        print("Max trades reached today")
        time.sleep(300)
        continue

    # -----------------------------
    # GET LAST CANDLE (M5)
    # -----------------------------
    rates = mt5.copy_rates_from_pos(symbol, mt5.TIMEFRAME_M5, 0, 1)

    if rates is None:
        print("Failed to get candles")
        time.sleep(60)
        continue

    df = pd.DataFrame(rates)

    open_price = df['open'][0]
    close_price = df['close'][0]

    print("Open:", open_price)
    print("Close:", close_price)

    # -----------------------------
    # SIGNAL
    # -----------------------------
    if close_price > open_price:
        order_type = mt5.ORDER_TYPE_BUY
        print("BUY signal")

    elif close_price < open_price:
        order_type = mt5.ORDER_TYPE_SELL
        print("SELL signal")

    else:
        print("No signal")
        time.sleep(60)
        continue

    # -----------------------------
    # GET PRICE
    # -----------------------------
    tick = mt5.symbol_info_tick(symbol)

    if order_type == mt5.ORDER_TYPE_BUY:
        price = tick.ask
        sl = price - 0.0010
        tp = price + 0.0020

    else:
        price = tick.bid
        sl = price + 0.0010
        tp = price - 0.0020

    # -----------------------------
    # TRADE REQUEST
    # -----------------------------
    request = {
        "action": mt5.TRADE_ACTION_DEAL,
        "symbol": symbol,
        "volume": lot,
        "type": order_type,
        "price": price,
        "sl": sl,
        "tp": tp,
        "deviation": 20,
        "magic": 123456,
        "comment": "Auto Python Bot",
        "type_time": mt5.ORDER_TIME_GTC,
        "type_filling": mt5.ORDER_FILLING_IOC,
    }

    result = mt5.order_send(request)

    print("Trade Result:", result)

    trade_count += 1

    # -----------------------------
    # WAIT BEFORE NEXT CHECK
    # -----------------------------
    time.sleep(60)