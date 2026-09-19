# Adjustable paediatric prosthetic socket: pressure sensing and visualisation

A children's prosthetic socket has a hard problem that an adult's does not:
the limb it fits is still growing, and a socket that fit last month can be
causing a pressure ulcer this month. This is the instrumentation side of an
adjustable socket, load cells inside the socket, streamed over Bluetooth LE,
mapped onto a 3D model of the residual limb so that a clinician can see where
the pressure actually is rather than asking a child to describe it.

## What it does

- Reads four load cells from an ESP32 over BLE, at the rate the firmware
  pushes them.
- Holds a rolling window per sensor and averages it, so a single noisy sample
  does not move the display.
- Tares against a stored baseline, so readings are pressure *changes* from a
  fitted reference rather than absolute values that include the socket's own
  preload.
- Maps each sensor to a region of a 3D leg mesh and colours it by deviation
  from the target pressure profile in `ideal_pressures.json`.

## Layout

```
NanoFiles/
  SensorsWithBT/SensorsWithBT.ino    ESP32 firmware: reads the cells, serves BLE
  PythonIntegration/
    esp32_bluetooth.py               BLE discovery, connect, notify, write
    sensor_sdk.py                    SocketSensor: buffering, averaging, baseline
    visualizer.py                    PyVista rendering of the mesh + pressure map
HelperScripts/
  coordinateMapper.py                locate sensor positions on the leg model
leg.STL                              the limb mesh
ideal_pressures.json                 target pressure profile per region
```

`sensor_sdk.py` is the piece to read first, it is the boundary between "bytes
arriving over BLE" and "a pressure value you can trust", and everything above
it depends on the buffering and baseline logic there.

## Setup

```bash
conda env create -f environment.yml
conda activate capstone
pip install -e .
```

Then flash `NanoFiles/SensorsWithBT/SensorsWithBT.ino` to the ESP32 and run:

```bash
python NanoFiles/PythonIntegration/visualizer.py
```

The BLE device name defaults to `ESP32_LoadCells` and the characteristic UUID
is set in `esp32_bluetooth.py`; both must match the firmware.

## Notes

- **Baseline before use.** Readings are relative to a stored baseline. Capture
  one with the socket donned and unloaded, or every region will read as
  over-pressure.
- **BLE pairing.** The ESP32 holds one connection. Disconnect any phone app
  before running.
- **Not a clinical device.** This is a capstone prototype for visualising
  relative pressure distribution, not a validated instrument, and nothing here
  should be used to make a fitting decision on its own.

## License

MIT, see [LICENSE](LICENSE).
