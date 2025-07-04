from asyncio import new_event_loop, run
from json import load
from os import listdir

from assistant import AP, Station, monitor

ap: AP = None
station: Station = None


async def connected(interface: Interface):
    print(f"Connected Callback was called using {interface}!") if interface else None


async def disconnected(interface: Interface):
    print(f"Disconnected Callback was called using {interface}!") if interface else None


async def test_station_fallback_async(
    primary: Station,
    fallback: AP,
    pause: int = 30,
    verbose: bool = False,
):
    """
    Testing 'Station Fallback' Asynchronously
    """
    print("Testing 'Station Fallback' Async")
    await monitor(
        station=primary,
        connectedCallback=connected,
        disconnectedCallback=disconnected,
        fallback=fallback,
        pause=pause,
        verbose=verbose,
    )
    print("Test 'Got IP' Async Passed")


try:
    credentials: dict = {"password": "", "ssid": ""}
    filename: str = "hotspot.json"

    if filename in listdir():
        with open(filename) as file:
            credentials = load(file)

    print(f"Loaded credentials: {credentials}")

    ap: AP = AP(password="raspberry")
    station: Station = Station(
        password=credentials["password"], ssid=credentials["ssid"]
    )
    run(
        test_station_fallback_async(
            primary=station, fallback=ap, pause=10, verbose=True
        )
    )
    print("All tests passed!")
finally:
    if ap:
        ap.deactivate()
    if station:
        station.deactivate()
    new_event_loop()
    print("Goodbye!")
