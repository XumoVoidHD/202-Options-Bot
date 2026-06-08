import os
import json
import asyncio
import time
import credentials

# Try importing OS-specific locking modules
try:
    import msvcrt
    is_windows = True
except ImportError:
    try:
        import fcntl
        is_windows = False
    except ImportError:
        fcntl = None
        is_windows = False

class CrossPlatformFileLock:
    def __init__(self, lock_path):
        self.lock_path = lock_path
        self.lock_file = None

    async def acquire(self, timeout=30):
        start_time = time.time()
        while time.time() - start_time < timeout:
            try:
                self.lock_file = open(self.lock_path, "a+")
                fd = self.lock_file.fileno()
                
                if is_windows:
                    msvcrt.locking(fd, msvcrt.LK_NBLCK, 1)
                else:
                    if fcntl is not None:
                        fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
                return True
            except (OSError, IOError):
                if self.lock_file:
                    try:
                        self.lock_file.close()
                    except Exception:
                        pass
                    self.lock_file = None
                await asyncio.sleep(0.1)
        return False

    def release(self):
        if self.lock_file:
            try:
                fd = self.lock_file.fileno()
                if is_windows:
                    self.lock_file.seek(0)
                    msvcrt.locking(fd, msvcrt.LK_UNLCK, 1)
                else:
                    if fcntl is not None:
                        fcntl.flock(fd, fcntl.LOCK_UN)
            except Exception:
                pass
            finally:
                try:
                    self.lock_file.close()
                except Exception:
                    pass
                self.lock_file = None

class StrikeCoordinator:
    @staticmethod
    async def check_and_register_strikes(strategy, strike_step):
        """
        Locks the strike tracker JSON, checks if strategy.call_target_price or strategy.put_target_price
        is already in use, shifts strikes if there is a conflict, registers the strikes,
        and releases the lock.
        """
        tracker_file = getattr(credentials, "strike_tracker_file", "strike_tracker.json")
        lock_file_path = tracker_file + ".lock"
        
        # Ensure target directory exists
        dir_name = os.path.dirname(tracker_file)
        if dir_name:
            os.makedirs(dir_name, exist_ok=True)
            
        lock = CrossPlatformFileLock(lock_file_path)
        await strategy.dprint("[STRIKE TRACKER] Attempting to acquire lock...")
        if not await lock.acquire(timeout=30):
            await strategy.dprint("[STRIKE TRACKER] ERROR: Timeout acquiring file lock.")
            raise RuntimeError("Could not acquire file lock for strike tracking.")
            
        try:
            # Load JSON content
            data = {}
            if os.path.exists(tracker_file):
                try:
                    with open(tracker_file, "r") as f:
                        data = json.load(f)
                except Exception as e:
                    await strategy.dprint(f"[STRIKE TRACKER] Warning: Failed to read tracker file ({e}). Initializing clean tracker.")
                    
            symbol = getattr(credentials, "instrument", "SPX")
            if symbol not in data:
                data[symbol] = {"calls": [], "puts": []}
                
            active_calls = data[symbol].get("calls", [])
            active_puts = data[symbol].get("puts", [])
            
            conflict_detected = False
            steps = getattr(credentials, "strike_shift_steps", 1)
            
            # Check for conflict loop
            while (strategy.call_target_price in active_calls) or (strategy.put_target_price in active_puts):
                conflict_detected = True
                await strategy.dprint(
                    f"[STRIKE TRACKER] Strike conflict! Call {strategy.call_target_price} "
                    f"or Put {strategy.put_target_price} is already in use. Shifting strikes..."
                )
                strategy.call_target_price += steps * strike_step
                strategy.otm_closest_call += steps * strike_step
                strategy.put_target_price -= steps * strike_step
                strategy.otm_closest_put -= steps * strike_step
                
            if conflict_detected:
                await strategy.dprint("[STRIKE TRACKER] Strikes were changed in strategy due to conflict. Final adjusted strikes:")
                await strategy.dprint(f"CALL POSITION STRIKE PRICE: {strategy.call_target_price}")
                await strategy.dprint(f"CALL HEDGE STRIKE PRICE: {strategy.otm_closest_call}")
                await strategy.dprint(f"PUT POSITION STRIKE PRICE: {strategy.put_target_price}")
                await strategy.dprint(f"PUT HEDGE STRIKE PRICE: {strategy.otm_closest_put}")
                
            # Register the finalized strikes
            active_calls.append(strategy.call_target_price)
            active_puts.append(strategy.put_target_price)
            
            data[symbol]["calls"] = active_calls
            data[symbol]["puts"] = active_puts
            
            with open(tracker_file, "w") as f:
                json.dump(data, f, indent=4)
                
            await strategy.dprint(
                f"[STRIKE TRACKER] Successfully registered active strikes for {symbol}: "
                f"Call={strategy.call_target_price}, Put={strategy.put_target_price}"
            )
            
        finally:
            lock.release()
            await strategy.dprint("[STRIKE TRACKER] Lock released.")

    @staticmethod
    async def remove_active_strike(strategy, strike_type, strike_val):
        """
        strike_type: "calls" or "puts"
        strike_val: the specific strike value to remove
        """
        tracker_file = getattr(credentials, "strike_tracker_file", "strike_tracker.json")
        lock_file_path = tracker_file + ".lock"
        
        if not os.path.exists(tracker_file):
            return
            
        lock = CrossPlatformFileLock(lock_file_path)
        if not await lock.acquire(timeout=30):
            await strategy.dprint(f"[STRIKE TRACKER] ERROR: Timeout acquiring lock to remove {strike_type} strike {strike_val}.")
            return
            
        try:
            data = {}
            try:
                with open(tracker_file, "r") as f:
                    data = json.load(f)
            except Exception as e:
                await strategy.dprint(f"[STRIKE TRACKER] Error reading tracker file for removal: {e}")
                return
                
            symbol = getattr(credentials, "instrument", "SPX")
            if symbol in data and strike_type in data[symbol]:
                active_list = data[symbol][strike_type]
                if strike_val in active_list:
                    active_list.remove(strike_val)
                    data[symbol][strike_type] = active_list
                    
                    with open(tracker_file, "w") as f:
                        json.dump(data, f, indent=4)
                    await strategy.dprint(f"[STRIKE TRACKER] Removed {strike_type[:-1]} strike {strike_val} from tracker for {symbol}.")
                else:
                    await strategy.dprint(f"[STRIKE TRACKER] Info: Strike {strike_val} was not in the {strike_type} list.")
        finally:
            lock.release()
