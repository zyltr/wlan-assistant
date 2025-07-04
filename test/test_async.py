from random import randint

from asyncio import gather, new_event_loop, run, sleep
from json import load
from network import STAT_GOT_IP, WLAN
from os import chdir, listdir

from assistant import Station


def test_got_ip_async(password: str, ssid: str, verbose: bool = False):
    """
    Testing 'Got IP' Asynchronously
    """

    async def connecting() -> bool:
        return await station.aconnect(verbose=verbose)

    async def nothing() -> None:
        for _ in range(randint(4, 10)):
            print("." * randint(1, 8))
            if station.wlan.isconnected():
                break
            await sleep(1)

    print("Testing 'Got IP' Async")
    station: Station = Station(password=password, ssid=ssid)
    results: list = run(gather(connecting(), nothing()))
    wlan: WLAN = station.wlan
    print(f"ASYNC Results: {results}")
    assert wlan.status() == STAT_GOT_IP, "'Got IP' test has failed!"
    station.deactivate()
    print("Test 'Got IP' Async Passed")
    print(f"WLAN IFConfig : {wlan.ifconfig()}")


try:
    credentials: dict = {
        "password": "",
        "ssid": "",
    }

    chdir("/")
    filename: str = "wlan.json"

    if filename in listdir():
        with open(filename) as file:
            credentials = load(file)

    print(f"Loaded credentials: {credentials}")

    test_got_ip_async(
        password=credentials.get("password"), ssid=credentials.get("ssid"), verbose=True
    )
except OSError as error:
    print(f"OSError: {error}")
except Exception as exception:
    print(f"Unknown Exception: {exception}")
else:
    print("All tests passed!")
finally:
    new_event_loop()
    print("Goodbye!")
