from bs4 import BeautifulSoup
from stem import Signal
from stem.control import Controller
from tor_handler import TorHandler
import requests
import random
import time

# https://developers.whatismybrowser.com/useragents/explore/software_name/<name_browser>/<page>
BASE_URL_USERAGENT_WEBSITE = (
    "https://developers.whatismybrowser.com/useragents/explore/software_name"
)
LIST_BROWSER_NAMES = ["firefox", "chrome", "edge", "safari"]
USERAGENTS = []
tor = TorHandler()
filename = "useragents.txt"


if __name__ == "__main__":
    for browser in LIST_BROWSER_NAMES:
        for page in range(1, 20):
            try:
                req = f"{BASE_URL_USERAGENT_WEBSITE}/{browser}/{page}"
                sess = tor.get_tor_session()
                content = sess.get(req).text
                soup = BeautifulSoup(content, "html.parser")
                proxies_table = soup.find(
                    "table",
                    {
                        "class": "table table-striped table-hover table-bordered table-useragents"
                    },
                )
                for row in proxies_table.tbody.find_all("tr"):
                    td_list = row.find_all("td")[0]
                    ua = td_list.find("a").text
                    print(ua)
                    USERAGENTS.append(ua)
            except Exception as e:
                print(
                    f"SOMETHING WENT WRONG WITH BROWSER NAME: {browser} AND PAGE {page} \n ERROR: {e}"
                )
                tor.renew_connection()
                print("DELAY 4 SECONDS")
                time.sleep(4)
                break
    # save ua's to file
    print("WRITING UA'S TO FILE ...")
    with open(filename, "w") as fl:
        for ua in USERAGENTS:
            fl.write(f"{ua}\n")
    print(f"UA'S WRITTEN TO {filename} SUCCESSFULLY!")
