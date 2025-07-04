from time import ticks_diff, ticks_ms

from asyncio import get_event_loop, sleep
from network import (
    STAT_CONNECTING,
    STAT_CONNECT_FAIL,
    STAT_GOT_IP,
    STAT_IDLE,
    STAT_NO_AP_FOUND,
    STAT_WRONG_PASSWORD,
    WLAN,
)


class Interface:
    """
    Interface base class for distinguishing a type of WLAN
    """

    def __init__(self, interface: int, password: str, ssid: str) -> None:
        if type(interface) is not int:
            raise TypeError(f"'interface' must be {int} not {type(interface)}")

        if interface not in (WLAN.IF_AP, WLAN.IF_STA):
            raise ValueError(
                f"'interface' must be either IF_AP ({WLAN.IF_AP}) or IF_STA ({WLAN.IF_STA})"
            )

        self._interface: int = interface
        self._password: str = password
        self._ssid: str = ssid
        self._wlan: WLAN = WLAN(interface)

        if interface == WLAN.IF_AP:
            if password:
                self._wlan.config(password=self.password)
            if ssid:
                self._wlan.config(ssid=self.ssid)
            else:
                self._ssid = self._wlan.config("ssid")

    @property
    def alive(self) -> bool:
        return self.wlan.status() == STAT_GOT_IP

    @property
    def interface(self) -> int:
        return self._interface

    @property
    def password(self) -> str:
        return self._password

    @property
    def ssid(self) -> str:
        return self._ssid

    @property
    def wlan(self) -> WLAN:
        return self._wlan

    async def _attempt(self, timeout: int = 15, verbose: bool = False) -> bool:
        if timeout <= 0:
            raise ValueError("'timeout' must be positive and greater than 0")

        if type(verbose) is not bool:
            raise TypeError(f"'verbose' must be {bool} and not {type(verbose)}")

        if self.wlan.status() == STAT_GOT_IP:
            return True

        delta: int = 0
        pause: int = 1
        reference: int = ticks_ms()
        statuses: dict = {
            STAT_CONNECT_FAIL: f"Connection Failed ({STAT_CONNECT_FAIL})",
            STAT_CONNECTING: f"Connecting ({STAT_CONNECTING})",
            STAT_GOT_IP: f"Got IP ({STAT_GOT_IP})",
            STAT_IDLE: f"Idle ({STAT_IDLE})",
            STAT_NO_AP_FOUND: f"No AP found ({STAT_NO_AP_FOUND})",
            STAT_WRONG_PASSWORD: f"Wrong Password ({STAT_WRONG_PASSWORD})",
        }
        timeout *= 1000
        wlan: WLAN = self.wlan

        wlan.active(True)

        if self.interface == WLAN.IF_STA and wlan.status() != STAT_IDLE:
            wlan.connect(self.ssid, self.password)

        while delta < timeout:
            status: int = wlan.status()

            if verbose:
                description: str = statuses.get(status, f"Unknown Status ({status})")
                print(
                    f"WLAN {wlan}",
                    f"Counter: {delta} ms, Status: {description}",
                    sep=f"\n{' ' * 2}",
                )

            if status == STAT_IDLE:
                if self.interface == WLAN.IF_STA:
                    wlan.connect(self.ssid, self.password)
                await sleep(pause)
            elif status == STAT_CONNECTING:
                await sleep(pause)
            elif status == STAT_GOT_IP:
                break
            elif status in (STAT_CONNECT_FAIL, STAT_NO_AP_FOUND, STAT_WRONG_PASSWORD):
                wlan.active(False)
                break
            else:
                await sleep(pause)

            delta = ticks_diff(ticks_ms(), reference)

        if verbose and delta >= timeout:
            print(f"Timeout reached!")

        return wlan.status() == STAT_GOT_IP

    def deactivate(self) -> None:
        self.disconnect()
        self.wlan.active(False)

    def disconnect(self) -> None:
        if self.wlan.status() == STAT_GOT_IP:
            self.wlan.disconnect()


class AP(Interface):
    """
    AP WLAN Interface
    """

    def __init__(self, password: str, ssid: str = None):
        super().__init__(interface=WLAN.IF_AP, password=password, ssid=ssid)

    async def aconfigure(self, timeout: int = 15, verbose: bool = True) -> bool:
        return await self._attempt(timeout=timeout, verbose=verbose)

    def configure(self, timeout: int = 15, verbose: bool = False) -> bool:
        return get_event_loop().run_until_complete(
            self.aconfigure(timeout=timeout, verbose=verbose)
        )


class Station(Interface):
    """
    STA WLAN Interface
    """

    def __init__(self, password: str, ssid: str):
        super().__init__(interface=WLAN.IF_STA, password=password, ssid=ssid)

    async def aconnect(
        self, retries: int = 0, timeout: int = 15, verbose: bool = False
    ) -> bool:
        if retries < 0:
            raise ValueError("Retries must be positive and greater than 0")

        connected: bool = await self._attempt(timeout=timeout, verbose=verbose)

        if not connected and retries > 0:
            if verbose:
                print(f"Retry {retries - (retries - 1)}/{retries}")
            return await self.aconnect(
                retries=retries - 1, timeout=timeout, verbose=verbose
            )
        else:
            return connected

    def connect(
        self, retries: int = 0, timeout: int = 15, verbose: bool = False
    ) -> bool:
        return get_event_loop().run_until_complete(
            self.aconnect(retries=retries, timeout=timeout, verbose=verbose)
        )
