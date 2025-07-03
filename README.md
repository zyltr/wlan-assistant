# WLAN Assistant

This assistant provides an easy-to-use interface for handling wireless network
connections on MicroPython-enabled devices.

## Installation

1. Copy `assistant.py`, or compile `assistant.mpy`, to your MicroPython device root or lib/ directory. The `.mpy` file
   consumes less storage
   space.
2. (Optional) Create a `wlan.json` file with and fill with your desired network ***ssid*** and ***password***. It should
   contain a properly formatted JSON object. It should exist at the root.

```json
{
  "password": "",
  "ssid": ""
}
```

## Generating assistant.mpy

***For Pico W devices***

You can install ***mpy-cross*** using ***pip***

```
mpy-cross -march=armv6m assistant.py
```

## Usage

```python
from assistant import Station

filename: str = "wlan.json"

if filename in listdir():
    with open(filename) as file:
        data = load(file)

station: Station = Station(password=data.get("password"), ssid=data.get("ssid"))
wlan: WLAN = station.connect()

if wlan.isconnected():
    print(wlan.ifconfig())
```
