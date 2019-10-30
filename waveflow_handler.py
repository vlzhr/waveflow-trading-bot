import pywaves as pw
import requests
from json import loads, dumps

base_url = "https://nodes.wavesnodes.com"
address = "3PNtfqFrJu6Svp7rKYtb3VmZu8hseiownoo"  # WAVES/BTC exchange account
# address = "3P6G2qeAsgcxFgSe4qUwN8zLhMCpxS5BUCR"  # WAVES/ETH exchange account
tokenA = "WAVES"
tokenB = "8LQW8f7P5d5PZM7GtZEBgaqRPGSzS3DfPuiXrURJ4AJS"  # wBTC ID
# tokenB = "474jTeYx2r2Va35794tCScAXWJG9hU2HcgxzMowaZUnu"  # wETH ID


def parse_value(text):
    return loads(text)["value"]

def get_amounts():
    amountA = parse_value(requests.get(base_url+"/addresses/data/"+address+"/amountTokenA").text)
    amountB = parse_value(requests.get(base_url + "/addresses/data/" + address + "/amountTokenB").text)
    return amountA/10**8, amountB/10**8


def get_current_wf_price():
    a,b = get_amounts()
    return round(b*10**8/a) / 10**8


def get_current_dex_price():
    asset1 = pw.Asset(tokenA)
    asset2 = pw.Asset(tokenB)
    return float(pw.AssetPair(asset1, asset2).last())


def get_optimum_amount():
    def get_delta(a):
        A, B = current_amounts
        b = A * B / -(A + a) + B
        return b / current_dex_price - a

    current_amounts = get_amounts()  # amounts of tokens locked in WaveFlow
    current_dex_price = get_current_dex_price()  # last match price on DEX

    dest = 1 if get_current_wf_price()/get_current_dex_price() > 1 else -1

    a = dest
    max_value = False
    while True:
        step = (1 if dest > 0 else -1) * 10**-4
        value = get_delta(a)
        a += step
        if not max_value or value*10**8 > max_value*10**8:
            max_value = value
        else:
            return round((a-step)*10**8)/10**8


if __name__ == "__main__":
    get_optimum_amount()

