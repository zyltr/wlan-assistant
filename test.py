from json import load
from network import (
    STAT_CONNECT_FAIL,
    STAT_GOT_IP,
    STAT_NO_AP_FOUND,
    STAT_WRONG_PASSWORD,
    WLAN,
)
from os import chdir, listdir

from assistant import Station


def test_connect_failed(password: str, ssid: str, verbose: bool = False):
    """
    Testing 'Connect Failed'
    """
    print("Testing 'Connect Failed'")
    interface: Station = Station(password=password, ssid=ssid)
    wlan: WLAN = interface.connect(verbose=verbose)
    assert wlan.status() == STAT_CONNECT_FAIL, "'Connect Fail' test has failed!"
    print("Test 'Connect Failed' Passed")


def test_got_ip(password: str, ssid: str, verbose: bool = False):
    """
    Testing 'Got IP'
    """
    print("Testing 'Got IP'")
    interface: Station = Station(password=password, ssid=ssid)
    wlan: WLAN = interface.connect(verbose=verbose)
    assert wlan.status() == STAT_GOT_IP, "'Got IP' test has failed!"
    print("Test 'Got IP' Passed")
    print(f"WLAN IFConfig : {wlan.ifconfig()}")


def test_interface_validation(password: str, ssid: str, verbose: bool = False):
    """
    Testing 'interface' validation
    """
    print("Testing 'interface' validation")

    try:
        interface: Station = Station(password=password, ssid=ssid)
        _: WLAN = interface._create(
            interface="AP", timeout=15, verbose=verbose
        )
    except TypeError as _:
        print(f"Caught error: {_}")
        print("Test 1 of 2 of 'interface' Passed")

    try:
        interface: Station = Station(password=password, ssid=ssid)
        _: WLAN = interface._create(
            interface=-1, timeout=15, verbose=verbose
        )
    except ValueError as _:
        print(f"Caught error: {_}")
        print("Test 2 of 2 of 'interface' Passed")

    print("Test 'interface' Passed")


def test_no_ap_found(password: str, ssid: str, verbose: bool = False):
    """
    Testing 'No AP Found' (Incorrect SSID)
    """
    print("Testing 'No AP Found'")
    interface: Station = Station(password=password, ssid=ssid)
    wlan: WLAN = interface.connect(verbose=verbose)
    assert wlan.status() == STAT_NO_AP_FOUND, "'No AP Found' test has failed!"
    print("Test 'No AP Found' Passed")


def test_timeout(password: str, ssid: str, verbose: bool = False):
    """
    Testing 'Timeout'
    """
    print("Testing 'Timeout'")
    interface: Station = Station(password=password, ssid=ssid)
    wlan: WLAN = interface.connect(timeout=1, verbose=verbose)
    assert not wlan.isconnected(), "'Timeout' test has failed!"
    print("Test 'Timeout' Passed")


def test_verbose_validation(password: str, ssid: str, verbose: bool = False):
    """
    Testing 'verbose' validation
    """
    print("Testing 'verbose' validation")
    try:
        interface: Station = Station(password=password, ssid=ssid)
        _: WLAN = interface.connect(verbose=verbose)
    except TypeError as _:
        print(f"Caught error: {_}")
        print("Test 'verbose' Passed")


def test_wrong_password(password: str, ssid: str, retries: int, verbose: bool = False):
    """
    Testing 'Wrong Password'
    """
    print("Testing 'Wrong Password'")
    interface: Station = Station(password=password, ssid=ssid)
    wlan: WLAN = interface.connect(retries=retries, verbose=verbose)
    assert wlan.status() == STAT_WRONG_PASSWORD, "'Wrong Password' test has failed!"
    print("Test 'Wrong Password' Passed")


def test_wrong_password_with_retries(password: str, ssid: str, retries: int, verbose: bool = False):
    """
    Testing 'Wrong Password with Retries'
    """
    print("Testing 'Wrong Password with Retries'")
    interface: Station = Station(password=password, ssid=ssid)
    wlan: WLAN = interface.connect(retries=retries, verbose=verbose)
    assert wlan.status() == STAT_WRONG_PASSWORD, "'Wrong Password' test has failed!"
    print("Test 'Wrong Password' Passed")


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
        verbose=True,
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
        retries=0,
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
    print("Goodbye!")
