import threading
import time
import json
import numpy as np
from collections import deque
from scipy.signal import butter, filtfilt
from esp32_serial import run_bluetooth_thread, send_command
from esp32_serial import is_connected as _serial_is_connected
from utils import resource_path

BASELINE_FILE = "baseline.json"

class SerialSensor:
    """
    Drop-in replacement for SocketSensor that uses USB serial instead of BLE.
    Public API is identical so visualizer_usb.py needs zero sensor-logic changes.
    """

    def __init__(self, device_name="ESP32_LoadCells", threshold=3, sample_count=1):
        self.device_name   = device_name
        self.threshold     = threshold
        self.sample_count  = sample_count

        self._lock         = threading.Lock()
        self._buffer       = deque(maxlen=25)
        self._ema          = [0.0, 0.0, 0.0, 0.0]
        self._alpha        = 0.2
        self._baseline     = [0.0, 0.0, 0.0, 0.0]
        self._capture_vals = None
        self._manual_vals  = [0.0, 0.0, 0.0, 0.0]
        self._use_manual   = False
        self._connected    = False

    # ── Internal data callback ────────────────────────────────────────────
    def _on_data(self, values):
        """Called by serial transport on each new packet."""
        with self._lock:
            # Z-score spike rejection (same as BLE SDK)
            if len(self._buffer) >= 5:
                arr = np.array(list(self._buffer))
                means = arr.mean(axis=0)
                stds  = arr.std(axis=0) + 1e-9
                z     = np.abs((np.array(values) - means) / stds)
                if np.any(z > 3):
                    return   # discard spike

            self._buffer.append(values)

            # EMA for live display
            for i in range(4):
                self._ema[i] = self._alpha * values[i] + (1 - self._alpha) * self._ema[i]

    # ── Public API ────────────────────────────────────────────────────────
    def connect(self):
        run_bluetooth_thread(self.device_name, self._on_data)
        # Give the serial thread a moment to open the port
        for _ in range(20):
            if _serial_is_connected():
                self._connected = True
                self._use_manual = False
                return True
            time.sleep(0.25)
        print("⚠ Serial not connected after timeout")
        return False

    @property
    def is_connected(self):
        return _serial_is_connected()

    @property
    def using_real_data(self):
        return not self._use_manual

    @property
    def has_capture(self):
        return self._capture_vals is not None

    def get_display(self):
        if self._use_manual:
            return list(self._manual_vals)
        with self._lock:
            return list(self._ema)

    def _collect_samples(self, n=None, progress_callback=None):
        """Block until n clean samples are buffered, apply Butterworth, return mean."""
        n = n or self.sample_count * 3  # collect 3× for filter stability
        self._buffer.clear()
        collected = []
        target    = n + 10
        while len(collected) < target:
            with self._lock:
                if len(self._buffer) > len(collected):
                    new = list(self._buffer)[len(collected):]
                    collected.extend(new)
            if progress_callback:
                progress_callback(min(len(collected), target), target)
            time.sleep(0.05)

        arr  = np.array(collected[:target])
        b, a = butter(4, 1.0 / (0.5 * (1000 / 10)), btype='low')  # 1Hz cutoff at 10Hz
        try:
            filtered = filtfilt(b, a, arr, axis=0)
        except Exception:
            filtered = arr
        return filtered.mean(axis=0).tolist()

    def capture(self, progress_callback=None):
        vals = self._collect_samples(progress_callback=progress_callback)
        self._capture_vals = vals
        return vals

    def set_baseline(self, progress_callback=None):
        vals = self._collect_samples(progress_callback=progress_callback)
        self._baseline     = vals
        self._capture_vals = vals
        try:
            with open(resource_path(BASELINE_FILE), "w") as f:
                json.dump(vals, f)
            return True
        except Exception as e:
            print(f"Baseline save error: {e}")
            return False

    def load_baseline(self):
        try:
            with open(resource_path(BASELINE_FILE), "r") as f:
                self._baseline = json.load(f)
            print(f"Baseline loaded: {[f'{v:.1f}' for v in self._baseline]}")
        except FileNotFoundError:
            print("No baseline file found — using zeros")

    def get_baseline(self):
        return list(self._baseline)

    def get_deviation(self, index):
        if self._capture_vals is None:
            return 0.0
        return self._capture_vals[index] - self._baseline[index]

    def get_recommendation(self, index):
        """Returns (action_str, (r, g, b)) matching SocketSensor output."""
        dev = self.get_deviation(index)
        if dev > self.threshold:
            return "Too Tight ▲", (1.0, 0.2, 0.2)
        elif dev < -self.threshold:
            return "Too Loose ▼", (0.2, 0.2, 1.0)
        else:
            return "Ideal ✓", (0.2, 1.0, 0.2)

    def tare(self):
        send_command("TARE")
        return True

    # Simulation stubs (keep control panel working without changes)
    def set_manual(self, index, value):
        self._manual_vals[index] = value

    def start_manual_stream(self):
        self._use_manual = True
