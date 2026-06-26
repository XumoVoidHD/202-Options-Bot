"""
Configuration for key.py monitor launcher.
"""

# IBKR connection creds for key.py
host = "127.0.0.1"
port = 7497
client_id = 114

# Contract details
instrument = "SPX"
exchange = "SMART"
currency = "USD"
tradingClass = "SPXW"
date = "20260428"  # YYYYMMDD

# Strike discovery settings (same style as main.py)
# Strike increment:
# - SPX: 5 (or 1 if desired)
# - XSP: 1
XSP_SPX_STRIKE = 5
OTM_CALL = 5
OTM_PUT = 5

# Trigger thresholds from monitor start bid
call_bid_increase_pct = 0
put_bid_increase_pct = 0

# Monitoring loop controls
poll_seconds = 3

# Start monitoring time (US/Eastern)
entry_hour = 1
entry_minute = 30
entry_second = 0

# Force run main.py even if no triggers occur
force_run = True
# Force-run time (US/Eastern). If no trigger by this time, run main.py anyway.
force_run_hour = 12
force_run_minute = 35
force_run_second = 0

# Logging
enable_logging = True
