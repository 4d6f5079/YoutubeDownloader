import requests
from stem import Signal
from stem.control import Controller


class TorHandler(object):
    def __init__(self, tor_host="localhost", authentication_password=None):
        self.authentication_password = authentication_password
        self.tor_host = tor_host
        self.controller_port = 9051
        self.tor_port = 9050
        self.socks5_url = f"socks5://{self.tor_host}:{self.tor_port}"
        self.session = self.get_tor_session()

    def get_tor_session(self):
        # initialize a requests Session
        session = requests.Session()
        # setting the proxy of both http & https to the localhost:9050
        # this requires a running Tor service in your machine and listening on port 9050 (by default)
        session.proxies = {"http": self.socks5_url, "https": self.socks5_url}
        return session

    def renew_tor_connection(self):
        # logging.debug('CHANGING IP ...')
        # print('CHANGING IP ...')
        with Controller.from_port(port=self.controller_port) as c:
            if self.authentication_password:
                c.authenticate(password=self.authentication_password)
            else:
                c.authenticate()
            # send NEWNYM signal to establish a new clean connection through the Tor network
            c.signal(Signal.NEWNYM)
        # logging.debug('IP CHANGED!')
        # print('IP CHANGED!')

    def test_tor_proxy_connection(self):
        ip_test = requests.get("http://httpbin.org/ip").json()
        self.renew_tor_connection()
        tor_ip_test = self.session.get("http://httpbin.org/ip").json()
        if ip_test != tor_ip_test:
            return True, ip_test, tor_ip_test
        else:
            return False, ip_test, tor_ip_test
