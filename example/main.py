"""
This example demonstrates the use of the monitor/watch function.
It is meant to be used alongside a Raspberry Pi Pico W.
"""

from asyncio import Task, create_task, gather, new_event_loop, run, sleep
from json import load
from machine import Pin
from os import chdir, listdir

from assistant import AP, Interface, Station, watch

ap: AP = AP(password="raspberry")
blinker: Task = None
led: Pin = Pin("LED", mode=Pin.OUT, value=0)
stations: list[Station] = []


async def blink(frequency: int, target: Pin, pause: int = 1):
    print(f"Blinking {target} {'once' if frequency == 1 else 'twice'} every {pause}s")
    while True:
        for counter, integer in enumerate(range(frequency)):
            target.on()
            await sleep(0.1)
            target.off()
            if counter <= frequency - 1:
                await sleep(0.1)
        await sleep(pause)


async def connected(interface: Interface):
    global blinker
    if interface:
        print(f"Joined {interface.ssid}!")
        blinker = create_task(
            blink(frequency=1 if isinstance(interface, AP) else 2, target=led)
        )


async def disconnected(interface: Interface):
    global blinker
    if interface:
        print(f"Left {interface.ssid}!")
        if blinker:
            blinker.cancel()


async def main(awaitables: list) -> list:
    return await gather(*awaitables)


async def stall(seconds: int):
    await sleep(seconds)


try:
    print("main.py")

    chdir("/")
    filename: str = "networks.json"

    if filename in listdir():
        with open(filename) as file:
            if data := load(file):
                for credentials in data:
                    stations.append(
                        Station(
                            password=credentials.get("password"),
                            ssid=credentials.get("ssid"),
                        )
                    )

    run(
        main(
            awaitables=[
                watch(
                    connectedCallback=connected,
                    disconnectedCallback=disconnected,
                    fallback=ap,
                    pause=15,
                    roam=False,
                    stations=stations,
                    verbose=True,
                ),
            ]
        )
    )
except KeyboardInterrupt:
    pass
finally:
    ap.deactivate()
    led.off()
    [station.deactivate() for station in stations]
    new_event_loop()
    print("Goodbye!")
