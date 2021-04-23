from bs4 import BeautifulSoup
import requests
from stem import Signal
from stem.control import Controller
import random
import time

#https://developers.whatismybrowser.com/useragents/explore/software_name/<name_browser>/<page>
BASE_URL_USERAGENT_WEBSITE='https://developers.whatismybrowser.com/useragents/explore/software_name'
LIST_BROWSER_NAMES=[
    'firefox',
    'chrome',
    'edge',
    'safari'
]
USERAGENTS=[]

# TOR
def get_tor_session():
    # initialize a requests Session
    session = requests.Session()
    # setting the proxy of both http & https to the localhost:9050 
    # this requires a running Tor service in your machine and listening on port 9050 (by default)
    session.proxies = {"http": "socks5://localhost:9050", "https": "socks5://localhost:9050"}
    return session

def renew_connection():
    print('CHANGING IP ...')
    with Controller.from_port(port=9051) as c:
        c.authenticate()
        # send NEWNYM signal to establish a new clean connection through the Tor network
        c.signal(Signal.NEWNYM)
    print('IP CHANGED!')

if __name__ == '__main__':
    for browser in LIST_BROWSER_NAMES:
        for page in range(1,20):
            try:
                req = f'{BASE_URL_USERAGENT_WEBSITE}/{browser}/{page}'
                sess = get_tor_session()
                content = sess.get(req).text
                soup = BeautifulSoup(content, 'html.parser')
                proxies_table = soup.find('table', { 'class' : 'table table-striped table-hover table-bordered table-useragents' })
                for row in proxies_table.tbody.find_all('tr'):
                    td_list = row.find_all('td')[0]
                    ua = td_list.find('a').text
                    print(ua)
                    USERAGENTS.append(ua)
            except Exception as e:
                print(f'SOMETHING WENT WRONG WITH BROWSER NAME: {browser} AND PAGE {page} \n ERROR: {e}')
                renew_connection()
                print('DELAY 4 SECONDS')
                time.sleep(4)
                break
    # save ua's to file
    print('WRITING UA\'S TO FILE ...')
    with open('useragents.txt', 'w') as fl:
        for ua in USERAGENTS:
            fl.write(f'{ua}\n')
    print(f'UA\'S WRITTEN TO FILE useragents.txt SUCCESSFULLY!')