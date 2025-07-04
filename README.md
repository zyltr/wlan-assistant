# WLAN Assistant

## Overview

The module provides tiny, async-friendly helper methods built around MicroPython's network.WLAN class.
It aims to do the following:

- Connect to one or more Wi‑Fi stations using JSON files or hardcoded credentials.
- Configure an access point as a fallback when no known networks are reachable.
- Continuously monitor the environment and roam to the best available network.
- Notifications via async callbacks when connectivity changes, such as connecting or disconnecting from a known network
  or access point.

## Requirements

- Raspberry Pi Pico W
    - <ins>**Other devices have not been tested.**</ins>
- MicroPython 1.25 or later
    - <ins>**Earlier versions may work but are untested.**</ins>
- JSON files containing SSID and password for known networks.
    - <ins>**Optional, but recommended for simplicity.**</ins>

## Basic Usage

### AP (Access Point)

The AP class is used to configure and start an access point.
The only required parameter is the `password` while a `ssid` is optional.
If no ssid is provided, the microcontroller, a Pico W in this case, will generate a SSID.

An optional `timeout` and `verbose` parameter can be passed to the `configure` method.
When `timeout` is specified, the method will have `timeout` seconds to set up and configure the AP.
If `verbose` is set to True, the method will print connection state changes to the console.

#### Configuring and starting an AP synchronously

```python
from assistant import AP

# Fill in the placeholders with your own credentials.
ap: AP = AP(password="ap-password", ssid="ap-ssid")
ap.configure()
```

#### Configuring and starting an AP asynchronously

```python
from asyncio import run
from assistant import AP

# Fill in the placeholders with your own credentials.
ap: AP = AP(password="ap-password", ssid="ap-ssid")
run(ap.aconfigure())
```

<ins>This is not the best way to configure an AP asynchronously and is just for demonstration.
For a better example, see the **main.py** in the **example** directory.
</ins>

### Station

The Station class is used to connect to a local network.
The required parameters are password and ssid.
They are both case-sensitive.

Optional `retries`, `timeout`, and `verbose` parameter can be passed to the `connect` method.
`Retries` controls how many times the connection will be attempted before giving up.
`Timeout` controls the amount of time in seconds the method has to connect to the network.
`Verbose` allows additional information to be printed to the console.

#### Connecting to a local network synchronously.

```python
from assistant import Station

# Fill in the placeholders with your own credentials.
station: Station = Station(password="network-password", ssid="network-ssid")
station.connect()
```

#### Connecting to a local network asynchronously.

```python
from asyncio import run
from assistant import Station

# Fill in the placeholders with your own credentials.
station: Station = Station(password="network-password", ssid="network-ssid")
run(station.aconnect())
```

<ins>This is not the best way to connect a Station asynchronously and is just for demonstration.
For a better example, see the **main.py** in the **example** directory.
</ins>

## Monitoring and Watching

#### Monitoring a single network and using an access point for fallback.

```python
from asyncio import run
from assistant import Station, AP, monitor

# Fill in the placeholders with your own credentials.
ap: AP = AP(password="ap-password", ssid="ap-ssid")
station: Station = Station(password="network-password", ssid="network-ssid")


async def connectedCallback(interface: AP | Station):
    print(f"Connected to {interface.ssid}")


async def disconnectedCallback(interface: AP | Station):
    print(f"Disconnected from {interface.ssid}")


run(monitor(connectedCallback=connectedCallback, disconnectedCallback=disconnectedCallback, fallback=ap,
            station=station))
```

#### Watching a list of networks and using an access point for fallback.

```python
from asyncio import run
from assistant import Station, AP, watch

# Fill in the placeholders with your own credentials.
ap: AP = AP(password="ap-password", ssid="ap-ssid")
primary: Station = Station(password="network-password", ssid="network-ssid")
secondary: Station = Station(password="network-password", ssid="network-ssid")


async def connectedCallback(interface: AP | Station):
    print(f"Connected to {interface.ssid}")


async def disconnectedCallback(interface: AP | Station):
    print(f"Disconnected from {interface.ssid}")


run(watch(connectedCallback=connectedCallback, disconnectedCallback=disconnectedCallback, fallback=ap,
          stations=[primary, secondary]))
```

## Examples

An in-depth example is available in the **example** directory. It expects a **network.json** file to
exist at the root directory to function. The **network.json** file should be formatted as follows:

```json
[
  {
    "ssid": "ssid-1",
    "password": "password-1"
  },
  {
    "ssid": "ssid-2",
    "password": "password-2"
  },
  {
    "ssid": "ssid-n",
    "password": "password-n"
  }
]
```

This example will attempt to connect to the first network in the list, then the second, and so on.
If none of the networks are reachable, an access point will be started.
Depending on what interface is being used (AP or Station),
the onboard LED will blink once when configured as an AP and twice when connected to a local network.

## Tests

A few tests are available in the **tests** directory.
The tests are meant to isolate any potential bugs and test the functionality of the module.
Using them requires a **hotspot.json** and **wlan.json** to exist at the root directory.
**hotspot.json** ideally should contain the credentials to a hotspot, such as phone that can be
switched on and off the test the functionality and switching capability of
the `monitor` and `watch` modules.
These files should be formatted as follows:

```json
{
  "password": "your-password",
  "ssid": "your-ssid"
}
```

# Notes and limitations

- SSID matching is case-sensitive.
- This code focuses on MicroPython.

## Troubleshooting

- Nothing connects:
    - Confirm SSID and password are correct. Case sensitivity is important.
    - Try verbose=True to see connection state logs.
    - Restart the board by hard reset.
