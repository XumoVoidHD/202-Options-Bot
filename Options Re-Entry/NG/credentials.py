# Default Values
port = 7497
host = "127.0.0.1"
data_type = 4
instrument = "NG"
tradingClass = "LNE"
exchange = "NYMEX"
currency = "USD"
option_multiplier = "10000"
close_positions = False
enable_logging = False
calc_values = True
active_close_hedges = True
close_hedges = False
# if active_close_hedges is false then don't open the hedges at all if true
# And close_hedges is true then close and open hedges accordingly
# And if close_hedges is False then just open the hedges but don't close them
WEBHOOK_URL = "https://discord.com/api/webhooks/1338574580876447907/0oLw18E0PXFac0-1Q1c9e4KYaloESxRCJDt81s1fZTpEfoWBkiodRGlN12RZVNTiIjbn"

# Changeable Values
date = "20260526"                   # Date of contract (YYYY-MM-DD)
future_date = "202606"
number_of_re_entry = 1              # Specifies the number of re-entries allowed
OTM_CALL_HEDGE = 5                # How far away the call hedge is (10 means that its $50 away from current price)
OTM_PUT_HEDGE = 5                 # How far away the put hedge is (10 means that its $50 away from current price)
ATM_CALL = 1                        # How far away call position is (2 means that its $10 away from current price)
ATM_PUT = 1                         # How far away put position is (2 means that its $10 away from current price)
call_sl = 30                        # From where the call stop loss should start from (15 here means 15% of entry price)
call_entry_price_changes_by = 10     # What % should call entry premium price should change by to update the trailing %
call_change_sl_by = 10               # What % of entry price should call sl change when trailing stop loss updates
put_sl = 30                         # From where the put stop loss should start from (15 here means 15% of entry price)
put_entry_price_changes_by = 10      # What % should put entry premium price should change by to update the trailing %
put_change_sl_by = 10                # What % of entry price should put sl change when trailing stop loss updates
conversion_time = 10                # Deprecated (No use)
entry_hour = 9                      # Entry time in hours
entry_minute = 30                   # Entry time in minutes
entry_second = 59                    # Entry time in seconds
exit_hour = 14                     # Exit time in hours
exit_minute = 30                    # Exit time in minutes
exit_second = 00                     # Exit time in seconds
call_hedge_quantity = 1             # Quantity for call hedge
put_hedge_quantity = 1              # Quantity for put hedge
call_position = 1                   # Quantity for call position
put_position = 1                    # Quantity for put position
call_hedge = 2.95
call_strike = 2.75
put_hedge = 2.45
put_strike = 2.65
call_check_time = 1
call_reentry_time = 5
put_check_time = 1
put_reentry_time = 5
