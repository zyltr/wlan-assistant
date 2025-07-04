from asyncio import new_event_loop
from json import load
from network import (
    STAT_CONNECT_FAIL,
    STAT_GOT_IP,
    STAT_NO_AP_FOUND,
    STAT_WRONG_PASSWORD,
    WLAN,
)
from os import chdir, listdir

from assistant import Interface, Station


def test_connect_failed(password: str, ssid: str, verbose: bool = False):
    """
    Testing 'Connect Failed'
    """
    print("Testing 'Connect Failed'")
    station: Station = Station(password=password, ssid=ssid)
    _: bool = station.connect(verbose=verbose)
    wlan: WLAN = station.wlan
    assert wlan.status() == STAT_CONNECT_FAIL, "'Connect Fail' test has failed!"
    station.deactivate()
    print("Test 'Connect Failed' Passed", "", sep="\n")


def test_got_ip(password: str, ssid: str, verbose: bool = False):
    """
    Testing 'Got IP'
    """
    print("Testing 'Got IP'")
    station: Station = Station(password=password, ssid=ssid)
    _: bool = station.connect(verbose=verbose)
    wlan: WLAN = station.wlan
    assert wlan.status() == STAT_GOT_IP, "'Got IP' test has failed!"
    station.deactivate()
    print("Test 'Got IP' Passed")
    print(f"WLAN IFConfig : {wlan.ifconfig()}", "", sep="\n")


def test_interface_validation(password: str, ssid: str):
    """
    Testing 'interface' validation
    """
    print("Testing 'interface' validation")

    try:
        _: Interface = Interface(interface="AP", password=password, ssid=ssid)
    except TypeError as _:
        print(f"Caught error: {_}")
        print("Test 1 of 2 of 'interface' Passed")

    try:
        _: Interface = Interface(interface=-1, password=password, ssid=ssid)
    except ValueError as _:
        print(f"Caught error: {_}")
        print("Test 2 of 2 of 'interface' Passed")

    print("Test 'interface' Passed", "", sep="\n")


def test_no_ap_found(password: str, ssid: str, verbose: bool = False):
    """
    Testing 'No AP Found' (Incorrect SSID)
    """
    print("Testing 'No AP Found'")
    station: Station = Station(password=password, ssid=ssid)
    _: bool = station.connect(verbose=verbose)
    wlan: WLAN = station.wlan
    assert wlan.status() == STAT_NO_AP_FOUND, "'No AP Found' test has failed!"
    station.deactivate()
    print("Test 'No AP Found' Passed", "", sep="\n")


def test_timeout(password: str, ssid: str, verbose: bool = False):
    """
    Testing 'Timeout'
    """
    print("Testing 'Timeout'")
    station: Station = Station(password=password, ssid=ssid)
    _: bool = station.connect(timeout=1, verbose=verbose)
    wlan: WLAN = station.wlan
    assert not wlan.isconnected(), "'Timeout' test has failed!"
    station.deactivate()
    print("Test 'Timeout' Passed", "", sep="\n")


def test_verbose_validation(password: str, ssid: str, verbose: bool = False):
    """
    Testing 'verbose' validation
    """
    print("Testing 'verbose' validation")
    station: Station = None
    try:
        station = Station(password=password, ssid=ssid)
        _: bool = station.connect(verbose=verbose)
    except TypeError as _:
        print(f"Caught error: {_}")
        print("Test 'verbose' Passed", "", sep="\n")
    finally:
        if station:
            station.deactivate()


def test_wrong_password(password: str, ssid: str, verbose: bool = False):
    """
    Testing 'Wrong Password'
    """
    print("Testing 'Wrong Password'")
    station: Station = Station(password=password, ssid=ssid)
    _: bool = station.connect(verbose=verbose)
    wlan: WLAN = station.wlan
    assert wlan.status() == STAT_WRONG_PASSWORD, "'Wrong Password' test has failed!"
    station.deactivate()
    print("Test 'Wrong Password' Passed", "", sep="\n")


def test_wrong_password_with_retries(
    password: str, ssid: str, retries: int, verbose: bool = False
):
    """
    Testing 'Wrong Password with Retries'
    """
    print("Testing 'Wrong Password with Retries'")
    station: Station = Station(password=password, ssid=ssid)
    _: bool = station.connect(retries=retries, verbose=verbose)
    wlan: WLAN = station.wlan
    assert wlan.status() == STAT_WRONG_PASSWORD, "'Wrong Password' test has failed!"
    station.deactivate()
    print("Test 'Wrong Password' Passed", "", sep="\n")


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

    test_interface_validation(
        password=credentials.get("password"),
        ssid=credentials.get("ssid"),
    )
    test_verbose_validation(
        password=credentials.get("password"),
        ssid=credentials.get("ssid"),
        verbose="True",
    )

    test_no_ap_found(
        password=credentials.get("password"),
        ssid=credentials.get("ssid") + "*",
        verbose=True,
    )

    test_connect_failed(
        password=str(),
        ssid=str(),
        verbose=True,
    )

    test_wrong_password(
        password=credentials.get("password") + "*",
        ssid=credentials.get("ssid"),
        verbose=True,
    )

    test_wrong_password_with_retries(
        password=credentials.get("password") + "*",
        ssid=credentials.get("ssid"),
        retries=1,
        verbose=True,
    )

    test_timeout(
        password=credentials.get("password"),
        ssid=credentials.get("ssid"),
        verbose=True,
    )

    test_got_ip(
        password=credentials.get("password"),
        ssid=credentials.get("ssid"),
        verbose=True,
    )
except OSError as error:
    print(f"OSError: {error}")
else:
    print("All tests passed!")
finally:
    _: WLAN = WLAN(WLAN.IF_STA)
    _.disconnect()
    _.active(False)
    new_event_loop()
    print("Goodbye!")
