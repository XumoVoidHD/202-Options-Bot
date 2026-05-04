from ib_insync import *

ib = IB()
ib.connect('127.0.0.1', 7497, clientId=1)

# -----------------------------
# GET UNDERLYING CL FUTURES PRICE
# -----------------------------
future = Future(
    symbol='CL',
    lastTradeDateOrContractMonth='202606',
    exchange='NYMEX',
    currency='USD'
)

ib.qualifyContracts(future)

ib.reqMarketDataType(1)
fut_ticker = ib.reqMktData(future)

# wait for price
for _ in range(10):
    ib.sleep(1)
    if fut_ticker.last and fut_ticker.last > 0:
        break

underlying_price = fut_ticker.last

if underlying_price is None:
    raise ValueError("No underlying price")

print("Underlying CL price:", underlying_price)

option = FuturesOption(
    symbol='CL',
    lastTradeDateOrContractMonth='20260504',
    strike=100,
    right='C',
    exchange='NYMEX',
    currency='USD',
    tradingClass='ML1'
)

ib.qualifyContracts(option)

ticker = ib.reqMktData(option, '', False, False)
ib.sleep(2)

entry_price = ticker.ask
qty = 1

# -----------------------------
# BUY ORDER
# -----------------------------
buy_order = MarketOrder('BUY', qty)
buy_order.tif = 'DAY' 
trade = ib.placeOrder(option, buy_order)

# Wait for fill
while not trade.isDone():
    ib.sleep(1)

print("BUY FILLED")

# -----------------------------
# STOP ORDER
# -----------------------------
stop_price = round(entry_price * 0.8, 2)

stp_order = StopOrder('SELL', qty, stop_price)
ib.placeOrder(option, stp_order)

print("STOP PLACED at:", stop_price)

ib.disconnect()