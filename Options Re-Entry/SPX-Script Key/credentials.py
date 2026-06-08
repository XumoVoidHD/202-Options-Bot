# Connection
port = 7497
host = "127.0.0.1"
data_type = 4

# Instrument
instrument = "SPX"
tradingClass = "SPXW"  # SPXW is for weekly (regular) and SPX is for AM
exchange = "SMART"
currency = "USD"

# General flags
close_positions = False
enable_logging = True
calc_values = True
active_close_hedges = False
close_hedges = True

# If active_close_hedges is false then don't open the hedges at all if true
# And close_hedges is true then close and open hedges accordingly
# And if close-hedges is False then just open the hedges but don't close them

# Alerts
WEBHOOK_URL = "https://discord.com/api/webhooks/1479071097134649496/P4FPegjWst-GJJbbl6ULBwZP1o1FQOwNDmK6thSHOXfnOfJf9vEpJEWF10dCAEoVAU4y"

# Changeable Values

# Contract
date = "20260501"  # Date of contract (YYYY-MM-DD)

# Strike increment:
# - SPX: 5 (or 1 if desired)
# - XSP: 1
XSP_SPX_STRIKE = 5

# Re-entry behavior
restrict_reentry_to_first_stopped_leg = True  # If True, only the first SL-hit leg can re-enter; if False, Call/Put re-enter independently
number_of_re_entry = 0  # Re-entry attempts allowed for the first stopped leg (set >1 for multiple re-entries)
call_check_time = 1
call_reentry_time = 5
put_check_time = 1
put_reentry_time = 5

# Opposite leg move-to-cost behavior
opposite_leg_move_to_cost = 1.5  # Multiplier for moving opposite leg's stop (e.g. 1.5 for 1.5x entry price, <= 0 to disable)
# If True, skip move-to-cost when the opposite leg's trailing SL has tightened at least once
opposite_leg_move_to_cost_respect_trailing = True
# If True, stop trailing updates on a leg after its stop is moved to cost by opposite leg SL-hit flow
trailing_sl_respecting_opposite_move_to_cost = True

# Strike distance configuration
OTM_CALL_HEDGE = 20  # How far away the call hedge is (10 means that its $50 away from current price)
OTM_PUT_HEDGE = 40  # How far away the put hedge is (10 means that its $50 away from current price)
ATM_CALL = 2  # How far away call position is (2 means that its $10 away from current price)
ATM_PUT = 2  # How far away put position is (2 means that its $10 away from current price)

# Stop loss and trailing
call_sl = 70  # From where the call stop loss should start from (15 here means 15% of entry price)
call_entry_price_changes_by = 50  # What % should call entry premium price should change by to update the trailing %
call_change_sl_by = 50  # What % of entry price should call sl change when trailing stop loss updates
put_sl = 70  # From where the put stop loss should start from (15 here means 15% of entry price)
put_entry_price_changes_by = 50  # What % should put entry premium price should change by to update the trailing %
put_change_sl_by = 50  # What % of entry price should put sl change when trailing stop loss updates

# Timing
conversion_time = 10  # Deprecated (No use)
entry_hour = 9  # Entry time in hours
entry_minute = 31  # Entry time in minutes
entry_second = 00  # Entry time in seconds
exit_hour = 15  # Exit time in hours
exit_minute = 55  # Exit time in minutes
exit_second = 00  # Exit time in seconds

# Quantities
call_hedge_quantity = 1  # Quantity for call hedge
put_hedge_quantity = 1  # Quantity for put hedge
call_position = 1  # Quantity for call position
put_position = 1  # Quantity for put position

# Fixed strikes
call_hedge = 5400
call_strike = 5415
put_hedge = 5350
put_strike = 5405

# Strike Tracker Configuration (SPX only)
strike_tracker_file = "C:/Users/vedan/Desktop/projects/202-Options-Bot/Options Re-Entry/SPX-Script Key/strike_tracker.json"
strike_shift_steps = 1

