import asyncio
import importlib.util
import logging
import os
import subprocess
import sys
from datetime import datetime
from pathlib import Path

import nest_asyncio
from pytz import timezone

from new_broker import IBTWSAPI


def load_key_config():
    config_path = Path(__file__).with_name("key-config.py")
    spec = importlib.util.spec_from_file_location("key_config", config_path)
    key_config = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(key_config)
    return key_config


def setup_logging():
    os.makedirs("logs", exist_ok=True)
    eastern = timezone("US/Eastern")
    current_date = datetime.now(eastern).strftime("%Y-%m-%d")

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s: %(message)s",
        handlers=[
            logging.FileHandler(f"logs/key_monitor_log_{current_date}.txt", mode="w"),
            logging.StreamHandler(),
        ],
    )
    return logging.getLogger(__name__)


class KeyMonitor:
    def __init__(self):
        self.key_config = load_key_config()
        self.logger = setup_logging() if self.key_config.enable_logging else None
        self.creds = {
            "host": self.key_config.host,
            "port": self.key_config.port,
            "client_id": self.key_config.client_id,
        }
        self.broker = IBTWSAPI(creds=self.creds)
        self.call_monitor_strike = None
        self.put_monitor_strike = None
        self.start_call_bid = None
        self.start_put_bid = None

    async def dprint(self, message):
        tagged_message = f"[KEY-MONITOR] {message}"
        print(tagged_message)
        if self.logger:
            self.logger.info(tagged_message)

    async def get_bid(self, strike, right):
        premium_data = await self.broker.get_latest_premium_price(
            symbol=self.key_config.instrument,
            expiry=self.key_config.date,
            strike=strike,
            right=right,
            exchange=self.key_config.exchange,
        )
        return premium_data.get("bid")

    @staticmethod
    def pct_change(start, current):
        if start is None or current is None or start <= 0:
            return None
        return ((current - start) / start) * 100

    @staticmethod
    def round_to_nearest_step(price, strike_step):
        return int(round(price / strike_step) * strike_step)

    async def compute_monitor_strikes(self):
        current_price = await self.broker.current_price(
            self.key_config.instrument
        )
        current_price = float(current_price)
        strike_step = self.key_config.XSP_SPX_STRIKE
        closest_strike = self.round_to_nearest_step(current_price, strike_step)

        self.call_monitor_strike = closest_strike + (self.key_config.OTM_CALL * strike_step)
        self.put_monitor_strike = closest_strike - (self.key_config.OTM_PUT * strike_step)

        await self.dprint(f"Current SPX Price: {current_price}")
        await self.dprint(f"Closest Strike: {closest_strike}")
        await self.dprint(
            f"Monitoring OTM Call Strike (C): {self.call_monitor_strike} | "
            f"Monitoring OTM Put Strike (P): {self.put_monitor_strike}"
        )

    async def disconnect_ibkr(self):
        try:
            if self.broker and self.broker.client and self.broker.client.isConnected():
                self.broker.client.disconnect()
                await self.dprint("Disconnected from IBKR.")
        except Exception as exc:
            await self.dprint(f"IBKR disconnect warning: {exc}")

    async def launch_main(self, reason, is_forced=True):
        if is_forced and not getattr(self.key_config, "force_run", True):
            await self.dprint(f"Skipping launch of main.py. Reason: {reason} (force_run is False)")
            await self.disconnect_ibkr()
            return
        await self.dprint(f"Launching main.py. Reason: {reason}")
        await self.disconnect_ibkr()
        main_path = Path(__file__).with_name("main.py")
        subprocess.Popen([sys.executable, str(main_path)], cwd=str(Path(__file__).parent))

    async def wait_for_entry_time(self):
        eastern = timezone("US/Eastern")
        now = datetime.now(eastern)
        entry_time = now.replace(
            hour=self.key_config.entry_hour,
            minute=self.key_config.entry_minute,
            second=self.key_config.entry_second,
            microsecond=0,
        )
        force_run_time = now.replace(
            hour=self.key_config.force_run_hour,
            minute=self.key_config.force_run_minute,
            second=self.key_config.force_run_second,
            microsecond=0,
        )

        await self.dprint(f"Entry time (US/Eastern): {entry_time}")
        await self.dprint(f"Force-run time (US/Eastern): {force_run_time}")

        if now >= force_run_time:
            await self.launch_main("force-run time already passed.")
            return False

        if entry_time >= force_run_time:
            await self.dprint(
                "Entry time is at/after force-run time. Skipping monitor and launching main.py."
            )
            await self.launch_main("entry time at/after force-run time")
            return False

        while datetime.now(eastern) < entry_time:
            remaining = int((entry_time - datetime.now(eastern)).total_seconds())
            await self.dprint(f"Waiting for entry time. Remaining: {remaining} seconds")
            await asyncio.sleep(min(10, max(1, remaining)))

        await self.dprint("Entry time reached. Starting strike selection and monitoring.")
        return True

    async def monitor_and_trigger(self):
        eastern = timezone("US/Eastern")
        now = datetime.now(eastern)
        force_run_time = now.replace(
            hour=self.key_config.force_run_hour,
            minute=self.key_config.force_run_minute,
            second=self.key_config.force_run_second,
            microsecond=0,
        )

        # If already past force-run time, run right away.
        if now >= force_run_time:
            await self.launch_main("force-run time already passed.")
            return

        await self.dprint(f"Stop monitoring at (US/Eastern): {force_run_time}")
        await self.dprint(
            f"Trigger thresholds => Call bid increase: {self.key_config.call_bid_increase_pct}% | "
            f"Put bid increase: {self.key_config.put_bid_increase_pct}%"
        )

        self.start_call_bid = await self.get_bid(self.call_monitor_strike, "C")
        self.start_put_bid = await self.get_bid(self.put_monitor_strike, "P")

        await self.dprint(
            f"Start bids => Call({self.call_monitor_strike}): {self.start_call_bid} | "
            f"Put({self.put_monitor_strike}): {self.start_put_bid}"
        )

        if not self.start_call_bid and not self.start_put_bid:
            await self.dprint("No valid start bids found. Running main.py immediately.")
            await self.launch_main("missing start bids")
            return

        while True:
            current_time = datetime.now(eastern)
            if current_time >= force_run_time:
                await self.launch_main("force-run time reached without trigger")
                return

            call_bid = await self.get_bid(self.call_monitor_strike, "C")
            put_bid = await self.get_bid(self.put_monitor_strike, "P")

            call_move = self.pct_change(self.start_call_bid, call_bid)
            put_move = self.pct_change(self.start_put_bid, put_bid)

            await self.dprint(
                f"Live bids => Call: {call_bid} ({call_move}%), Put: {put_bid} ({put_move}%)"
            )

            call_triggered = (
                call_move is not None and call_move >= self.key_config.call_bid_increase_pct
            )
            put_triggered = (
                put_move is not None and put_move >= self.key_config.put_bid_increase_pct
            )

            if call_triggered or put_triggered:
                reasons = []
                if call_triggered:
                    reasons.append(
                        f"Call {self.call_monitor_strike} bid +{round(call_move, 2)}%"
                    )
                if put_triggered:
                    reasons.append(
                        f"Put {self.put_monitor_strike} bid +{round(put_move, 2)}%"
                    )
                await self.launch_main(" / ".join(reasons), is_forced=False)
                return

            await asyncio.sleep(self.key_config.poll_seconds)

    async def main(self):
        await self.dprint("Starting key.py monitor script.")
        await self.broker.connect()
        await self.dprint(f"IBKR connected: {self.broker.is_connected()}")
        can_monitor = await self.wait_for_entry_time()
        if not can_monitor:
            return
        await self.compute_monitor_strikes()
        await self.monitor_and_trigger()


if __name__ == "__main__":
    nest_asyncio.apply()
    monitor = KeyMonitor()
    asyncio.run(monitor.main())
