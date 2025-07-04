from asyncio import new_event_loop, run
from json import load
from os import listdir

from assistant import AP, Station, watch

ap: AP = AP(password="raspberry")
stations: list[Station] = []


async def connected(interface: Interface):
    print(f"Connected to {interface.ssid}!") if interface else None


async def disconnected(interface: Interface):
    print(f"Disconnected from {interface.ssid}!") if interface else None


try:
    print("Testing 'watch'")

    pause: int = 15
    roam: bool = False
    stations: list[Station] = []
    verbose: bool = True

    filenames: str = ["hotspot.json", "wlan.json"]

    for filename in filenames:
        if filename in listdir():
            with open(filename) as file:
                if credentials := load(file):
                    stations.append(
                        Station(
                            password=credentials["password"], ssid=credentials["ssid"]
                        )
                    )

    run(
        watch(
            stations=stations,
            connectedCallback=connected,
            disconnectedCallback=disconnected,
            fallback=ap,
            pause=pause,
            roam=roam,
            verbose=verbose,
        )
    )
finally:
    if ap:
        ap.deactivate()
    if stations:
        for station in stations:
            station.deactivate()
    new_event_loop()
    print("Goodbye!")
