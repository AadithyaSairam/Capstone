import json
import os
import threading
import time
from collections import deque
from esp32_bluetooth import run_bluetooth_thread, send_command_sync
from utils import resource_path, writable_path

# Writable path for saving
CONFIG_FILE = writable_path("ideal_pressures.json")
# Bundled default to fall back on if no saved file exists yet
CONFIG_FILE_DEFAULT = resource_path("ideal_pressures.json")


class SocketSensor:

    def __init__(self, device_name="ESP32_LoadCells", num_sensors=4, threshold=20, sample_count=75):
        self.device_name = device_name
        self.num_sensors = num_sensors
        self.threshold = threshold
        self.sample_count = sample_count  # Number of samples to average

        self._lock = threading.Lock()
        self._latest   = [0.0] * num_sensors
        self._captured = [0.0] * num_sensors
        self._baseline = [0.0] * num_sensors
        self._has_capture = False
        self._connected = False
        self._using_real_data = False

        # Rolling buffer — stores last N readings per sensor
        self._sample_buffer = [deque(maxlen=sample_count) for _ in range(num_sensors)]

        self.load_baseline()

    # ── Connection ────────────────────────────────────────────
    def connect(self):
        t = threading.Thread(
            target=run_bluetooth_thread,
            args=(self.device_name, self._on_data),
            daemon=True
        )
        t.start()
        return t

    @property
    def is_connected(self):
        return self._connected

    @property
    def using_real_data(self):
        return self._using_real_data

    # ── Sampling ──────────────────────────────────────────────
    def _collect_samples(self, target_count, progress_callback=None):
        """
        Block until target_count fresh samples are collected,
        then return the averaged values.
        progress_callback(current, total) is optional for UI progress updates.
        """
        # Clear the buffer so we only average fresh readings
        with self._lock:
            for buf in self._sample_buffer:
                buf.clear()

        collected = 0
        while collected < target_count:
            with self._lock:
                collected = min(len(buf) for buf in self._sample_buffer)
            if progress_callback:
                progress_callback(collected, target_count)
            time.sleep(0.05)  # Check every 50ms

        # Average across all collected samples
        with self._lock:
            averaged = [
                sum(self._sample_buffer[i]) / len(self._sample_buffer[i])
                for i in range(self.num_sensors)
            ]

        print(f"✓ Averaged {target_count} samples: {[f'{v:.1f}' for v in averaged]}")
        return averaged

    # ── Live Data ─────────────────────────────────────────────
    def get_live(self):
        with self._lock:
            return self._latest.copy()

    def capture(self, progress_callback=None):
        """Collect and average samples for a READ/TEST snapshot"""
        print(f"Capturing {self.sample_count} samples...")
        averaged = self._collect_samples(self.sample_count, progress_callback)
        with self._lock:
            self._captured = averaged
            self._has_capture = True
        return self._captured.copy()

    def get_captured(self):
        return self._captured.copy() if self._has_capture else None

    @property
    def has_capture(self):
        return self._has_capture

    def get_display(self):
        if self._has_capture:
            return self._captured.copy()
        return self.get_live()

    # ── Baseline ──────────────────────────────────────────────
    def set_baseline(self, values=None, progress_callback=None):
        """
        Collect and average samples then save as baseline.
        If values are explicitly passed, skip sampling and use those directly.
        """
        if values is None:
            print(f"Collecting {self.sample_count} samples for baseline...")
            values = self._collect_samples(self.sample_count, progress_callback)

        with self._lock:
            self._baseline = values.copy()
        try:
            with open(CONFIG_FILE, 'w') as f:
                json.dump({'ideal_pressures': self._baseline}, f, indent=2)
            print(f"✓ Saved baseline: {[f'{v:.1f}' for v in self._baseline]}")
            return True
        except Exception as e:
            print(f"Error saving baseline: {e}")
            return False

    def load_baseline(self):
        try:
            # Try writable path first (user's saved baseline)
            if os.path.exists(CONFIG_FILE):
                with open(CONFIG_FILE, 'r') as f:
                    data = json.load(f)
                    self._baseline = data.get('ideal_pressures', [0.0] * self.num_sensors)
                print(f"✓ Loaded saved baseline: {self._baseline}")

            # Fall back to bundled default if no saved file yet
            elif os.path.exists(CONFIG_FILE_DEFAULT):
                with open(CONFIG_FILE_DEFAULT, 'r') as f:
                    data = json.load(f)
                    self._baseline = data.get('ideal_pressures', [0.0] * self.num_sensors)
                print(f"✓ Loaded default baseline: {self._baseline}")

            else:
                print("No baseline found, using zeros")

        except Exception as e:
            print(f"Error loading baseline: {e}")


    def get_baseline(self):
        return self._baseline.copy()

    # ── Commands ──────────────────────────────────────────────
    def tare(self):
        try:
            success = send_command_sync("TARE")
            print("✓ Tare sent" if success else "✗ BLE not connected")
            return success
        except Exception as e:
            print(f"✗ Tare failed: {e}")
            return False

    # ── Analysis ──────────────────────────────────────────────
    def get_deviation(self, sensor_index):
        return self._captured[sensor_index] - self._baseline[sensor_index]

    def get_recommendation(self, sensor_index):
        dev = self.get_deviation(sensor_index)
        if dev > self.threshold:
            return "↻ LOOSEN",  (1.0, 0.2, 0.2)
        elif dev < -self.threshold:
            return "↺ TIGHTEN", (0.2, 0.2, 1.0)
        else:
            return "✓ OK",      (0.2, 1.0, 0.2)

    # ── Manual Override (Simulation Panel) ────────────────────
    def set_manual(self, index, value):
        if not self._using_real_data:
            with self._lock:
                self._latest[index] = value
                self._sample_buffer[index].append(value)

    # ── Internal ──────────────────────────────────────────────
    def _on_data(self, raw_data):
        values = self._parse(raw_data)
        if values:
            with self._lock:
                self._latest = values
                self._connected = True
                self._using_real_data = True
                # Push each sensor value into its rolling buffer
                for i, v in enumerate(values):
                    self._sample_buffer[i].append(v)

    @staticmethod
    def _parse(raw_data):
        try:
            if isinstance(raw_data, bytes):
                raw_data = raw_data.decode('utf-8').strip()
            parts = raw_data.strip().split(',')
            if len(parts) >= 5:
                return [float(parts[1]), float(parts[2]),
                        float(parts[3]), float(parts[4])]
        except Exception as e:
            print(f"Parse error: {e} | Raw: {raw_data}")
        return None
    
    def start_manual_stream(self, interval=0.1):
        """
        Continuously push current manual values into the buffer.
        Called when running in simulation mode (no BLE).
        """
        def pump():
            while not self._using_real_data:
                with self._lock:
                    for i in range(self.num_sensors):
                        self._sample_buffer[i].append(self._latest[i])
                time.sleep(interval)

        t = threading.Thread(target=pump, daemon=True)
        t.start()
        return t

