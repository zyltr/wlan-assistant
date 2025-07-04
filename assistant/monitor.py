from binascii import hexlify
from random import randint

from asyncio import sleep
from collections import namedtuple
from network import WLAN

from assistant.interface import AP, Interface, Station

ConnectedCallback: str = "Coroutine[[Interface | None], None]"
DisconnectedCallback: str = "Coroutine[[Interface | None], None]"


# NOTE - Case sensitivity matters when trying to connect to a network.


class _Monitor:
    """"""

    _Scanned = namedtuple("_Scanned", "ssid bssid channel rssi security hidden")

    @classmethod
    async def _callback(
        cls,
        joined: Interface,
        left: Interface,
        connectedCallback: ConnectedCallback = None,
        disconnectedCallback: DisconnectedCallback = None,
    ) -> None:
        await disconnectedCallback(left) if disconnectedCallback and left else None
        await connectedCallback(joined) if connectedCallback and joined else None

    @classmethod
    async def _join(
        cls,
        network: AP | None | Station,
        timeout: int,
        retries: int = 0,
        verbose: bool = False,
    ) -> bool:
        if network:
            if isinstance(network, AP):
                return await network.aconfigure(timeout=timeout, verbose=verbose)
            else:
                return await network.aconnect(
                    retries=retries, timeout=timeout, verbose=verbose
                )
        else:
            return False

    @classmethod
    async def _leave(cls, network: AP | None | Station) -> None:
        if network:
            if isinstance(network, AP):
                network.deactivate()
            else:
                network.disconnect()

    @classmethod
    async def _log(cls, message: str, verbose: bool = False) -> bool:
        if verbose:
            print(message)

    @classmethod
    async def _scan(cls, decode: bool = False) -> list[cls._Scanned]:
        scanner: WLAN = WLAN(WLAN.IF_STA)
        active: bool = scanner.active()
        if not active:
            scanner.active(True)
        available: list[cls._Scanned] = [
            cls._Scanned(*device) for device in scanner.scan()
        ]
        if decode:
            transformation = lambda device: cls._Scanned(
                ssid=device.ssid.decode() if decode else device.ssid,
                bssid=(hexlify(device.bssid).decode() if decode else device.bssid),
                channel=device.channel,
                rssi=device.rssi,
                security=device.security,
                hidden=device.hidden,
            )
            available = list(map(transformation, available))
        if not active:
            scanner.active(False)
        return available

    @classmethod
    async def _stall(cls, seconds: int) -> None:
        await sleep(seconds)

    @classmethod
    async def monitor(
        cls,
        station: Station,
        connectedCallback: ConnectedCallback = None,
        disconnectedCallback: DisconnectedCallback = None,
        fallback: AP = None,
        pause: int = 30,
        retries: int = 0,
        timeout: int = 15,
        verbose: bool = False,
    ) -> None:
        return await cls.watch(
            connectedCallback=connectedCallback,
            disconnectedCallback=disconnectedCallback,
            fallback=fallback,
            pause=pause,
            stations=[station],
            verbose=verbose,
            retries=retries,
            timeout=timeout,
        )

    # NOTE - WLAN instances seem to work as singletons, which means if you try to configure
    #        an AP/STA twice, it might reference the first instance.
    @classmethod
    async def watch(
        cls,
        stations: list[Station],
        connectedCallback: ConnectedCallback = None,
        disconnectedCallback: DisconnectedCallback = None,
        fallback: AP = None,
        pause: int = 30,
        roam: bool = False,
        retries: int = 0,
        timeout: int = 15,
        verbose: bool = False,
    ):
        if (_ := WLAN(WLAN.IF_AP)).active():
            _.disconnect()
            _.active(False)

        if (_ := WLAN(WLAN.IF_STA)).active():
            _.disconnect()
            _.active(False)

        active: Interface = None

        while True:
            networks: list[cls._Scanned] = await cls._scan(decode=True)

            if roam:
                networks.sort(key=lambda _: _.rssi, reverse=True)
                reachable: list[Station] = [
                    station
                    for network in networks
                    for station in stations
                    if network.ssid == station.ssid
                ]
            else:
                reachable: list[Station] = [
                    station
                    for station in stations
                    for network in networks
                    if network.ssid == station.ssid
                ]

            await cls._log(
                message=f"Networks: {[(network.ssid, network.rssi) for network in networks]}",
                verbose=verbose,
            )
            await cls._log(
                message=f"Reachable: {[station.ssid for station in reachable]}",
                verbose=verbose,
            )
            await cls._log(
                message=f"Stations: {[station.ssid for station in stations]}",
                verbose=verbose,
            )

            for station in reachable:
                if await cls._join(
                    network=station, retries=retries, timeout=timeout, verbose=verbose
                ):
                    message: str = (
                        f"{'Joined STA' if active != station else 'Watching STA'} {station.ssid} {station.wlan}"
                    )

                    await cls._log(
                        message=message,
                        verbose=verbose,
                    )

                    if active != station:
                        await cls._leave(network=active)
                        await cls._callback(
                            connectedCallback=connectedCallback,
                            disconnectedCallback=disconnectedCallback,
                            joined=station,
                            left=active,
                        )
                        active = station

                    break
            else:
                if await cls._join(
                    network=fallback, retries=retries, timeout=timeout, verbose=verbose
                ):
                    message: str = (
                        f"{'Configured AP' if active != fallback else 'Watching AP'} {fallback.ssid} {fallback.wlan}"
                    )

                    await cls._log(
                        message=message,
                        verbose=verbose,
                    )

                    if active != fallback:
                        await cls._leave(network=active)
                        await cls._callback(
                            connectedCallback=connectedCallback,
                            disconnectedCallback=disconnectedCallback,
                            joined=fallback,
                            left=active,
                        )
                        active = fallback

            await cls._stall(seconds=pause)
            await cls._log(message="." * randint(1, 10), verbose=verbose)


monitor = _Monitor.monitor
watch = _Monitor.watch
