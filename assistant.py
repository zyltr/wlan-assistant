from time import sleep, ticks_diff, ticks_ms

from network import (
    STAT_CONNECTING,
    STAT_CONNECT_FAIL,
    STAT_GOT_IP,
    STAT_IDLE,
    STAT_NO_AP_FOUND,
    STAT_WRONG_PASSWORD,
    WLAN,
)


class Assistant:
    """
    Base class for WLAN Assistant
    """

    def __init__(self, password: str, ssid: str) -> None:
        self._password: str = password
        self._ssid: str = ssid

    @property
    def password(self) -> str:
        return self._password

    @password.setter
    def password(self, value: str) -> None:
        self._password = value

    @property
    def ssid(self) -> str:
        return self._ssid

    @ssid.setter
    def ssid(self, value: str) -> None:
        self._ssid = value

    def _create(self, interface: int, timeout: int, verbose: bool) -> WLAN:
        """
        Creates and initializes a WLAN object based on the provided parameters.

        This method configures a WLAN interface, attempts to establish, or create, a connection,
        and provides details about the connection status during the process.
        It supports both Access Point (AP) and Station (STA) modes.

        Arguments:
            interface (int): Specifies the WLAN interface.
            Must be either WLAN.IF_AP for Access Point mode or WLAN.IF_STA for Station mode.
            password (str): The password for the WLAN.
            Required for secured networks.
            ssid (str): The SSID of the WLAN.
            Required for connecting in STA mode or setting up in AP mode.
            timeout (int): The maximum duration (in seconds) to attempt the WLAN connection before timing out.
            Must be a positive value greater than 0.
            verbose (bool): Indicates whether to display detailed output of the connection process.

        Returns:
            WLAN: A potentially configured and initialized WLAN object.

        Raises:
            TypeError: If the type of 'interface' or 'verbose' is incorrect.
            ValueError: If 'interface' does not match valid WLAN interface modes,
            or if 'timeout' is less than or equal to 0.
        """
        if type(interface) is not int:
            raise TypeError(f"'interface' must be {int} not {type(interface)}")

        if interface not in (WLAN.IF_AP, WLAN.IF_STA):
            raise ValueError(
                f"'interface' must be either IF_AP ({WLAN.IF_AP}) or IF_STA ({WLAN.IF_STA})"
            )

        if timeout <= 0:
            raise ValueError("Timeout must be positive and greater than 0")

        if type(verbose) is not bool:
            raise TypeError(f"'verbose' must be {bool} and not {type(verbose)}")

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
        wlan: WLAN = WLAN(interface)

        if interface == WLAN.IF_AP:
            if password:
                wlan.config(password=self.password)
            if ssid:
                wlan.config(ssid=self.ssid)

        wlan.active(True)

        if interface == WLAN.IF_STA and wlan.status() != STAT_IDLE:
            wlan.connect(self.ssid, self.password)

        while delta < timeout:
            status: int = wlan.status()

            if verbose:
                description: str = statuses.get(status, f"Unknown Status ({status})")
                print(
                    f"WLAN",
                    f"Counter: {delta} ms",
                    f"Status: {description}",
                    sep=f"\n{' ' * 2}",
                )

            if status == STAT_IDLE:
                if interface is WLAN.IF_STA:
                    wlan.connect(self.ssid, self.password)
                sleep(pause)
            elif status == STAT_CONNECTING:
                sleep(pause)
            elif status == STAT_GOT_IP:
                break
            elif status in (STAT_CONNECT_FAIL, STAT_NO_AP_FOUND, STAT_WRONG_PASSWORD):
                break
            else:
                sleep(pause)

            delta = ticks_diff(ticks_ms(), reference)

        if verbose and delta >= timeout:
            print(f"Timeout reached!")

        if not wlan.isconnected():
            wlan.active(False)

        return wlan


class AP(Assistant):

    # TODO - Asynchronous method for configuring as AP
    def aconfigure(self, timeout: int = 15, verbose: bool = False) -> WLAN:
        pass

    def configure(self, timeout: int = 15, verbose: bool = False) -> WLAN:
        """
        Configures and starts the WLAN interface as an Access Point.

        Args:
            timeout: An integer defining the timeout duration in seconds for the operation.
            verbose: A boolean determining whether to output verbose logs.

        Returns:
            WLAN: An instance of the WLAN class configured as an Access Point.
        """
        return self._create(
            interface=WLAN.IF_AP,
            timeout=timeout,
            verbose=verbose
        )


class Station(Assistant):
    """
    A class to help with connecting to a network using a WLAN interface in station mode.
    """

    # TODO - Asynchronous method for connecting to AP
    def aconnect(self, retries: int = 0, timeout: int = 15, verbose: bool = False) -> WLAN:
        pass

    def connect(self, retries: int = 0, timeout: int = 15, verbose: bool = False) -> WLAN:
        """
        Tries to connect to a network using a WLAN interface in station mode.

        Args:
            retries (int): The number of times to retry connecting to the network.
            timeout (int): The timeout duration in seconds for the connection attempt.
            Defaults to 15 seconds.
            verbose (bool): Flag to enable verbose output during the connection process.
            Defaults to False.

        Returns:
            WLAN: A WLAN object configured in Station mode and potentially connected to the specified network.
        """
        if retries < 0:
            raise ValueError("Retries must be positive and greater than 0")

        wlan: WLAN = self._create(
            interface=WLAN.IF_STA,
            timeout=timeout,
            verbose=verbose
        )

        if wlan.isconnected() or (retries - 1) < 0:
            return wlan
        else:
            if verbose: print(f"Retry {retries - (retries - 1)}/{retries}")
            return self.connect(retries=retries - 1, timeout=timeout, verbose=verbose)
