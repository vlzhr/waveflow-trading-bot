import pywaves as pw
import waveflow_handler as wf
from time import sleep

account = pw.Address(privateKey="27uhZoT9ASj6XZAn7Fidjws5yijyxWsMRpb3hPMQhNDL")  # address for a public use :)
pw.setMatcher(pw.MATCHER)
WVS = 10**8


def wf_exchange(amount):
    """ changes <amount> WAVES or <all_available> tokenB on WaveFlow.xyz """
    amount = int(amount*WVS)

    tx = account.invokeScript("3PNtfqFrJu6Svp7rKYtb3VmZu8hseiownoo", "exchanger",
                         [{"type": "integer", "value": 0}],
                         [
                                  {"assetId": None, "amount": amount} if amount > 0 else
                                  {"assetId": wf.tokenB, "amount": account.balance(wf.tokenB)}
                          ])

    for x in range(150):
        sleep(0.1)
        if "error" not in pw.tx(tx["id"]):
            print("WaveFlow exchange completed. Payment: {amount} {assetId}. Transaction ID: {txid}"
                  .format(amount=int(tx["payment"][0]["amount"])/10**8,
                          assetId=tx["payment"][0]["assetId"] if tx["payment"][0]["assetId"] else "WAVES",
                          txid=tx["id"]))
            return tx


def get_instant_price(book, amount):
    """ determines price for the instantly filled order on DEX """
    li = book["asks"] if amount > 0 else book["bids"]
    amount = abs(amount)
    while amount > 0:
        amount -= li[0]["amount"]
        price = li[0]["price"]
        li.pop(0)
    return price/WVS


def create_sell_order(amount, pair):
    """ creates order to sell <amount> WAVES on DEX """
    price = get_instant_price(pair.orderbook(), amount)
    tokenA_to_sell = abs(amount)
    order = account.sell(assetPair=pair, amount=int(tokenA_to_sell*WVS), price=price)
    print("Will sell {} WAVES for a price {} BTC".format(tokenA_to_sell / WVS, price / WVS))
    return order


def complete_order(amount=0.001):
    """ completes buy/sell orders for the WAVES/BTC pair """
    asset1 = pw.Asset("WAVES")
    asset2 = pw.Asset("8LQW8f7P5d5PZM7GtZEBgaqRPGSzS3DfPuiXrURJ4AJS")
    pair = pw.AssetPair(asset1, asset2)

    if amount > 0:
        amount = int(amount*WVS)
        price = get_instant_price(pair.orderbook(), amount)
        tokenA_to_buy = int(account.balance(wf.tokenB)/price)
        order = account.buy(assetPair=pair, amount=tokenA_to_buy, price=price)
        print("Will buy {} WAVES for a price {} BTC".format(tokenA_to_buy/WVS, price/WVS))
    else:
        order = create_sell_order(amount, pair)

    print("Order created. Here is the order ID: {}".format(order.orderId))

    for x in range(150):
        sleep(0.1)
        if order.status() == "Filled":
            print("Order is filled!")
            return order
    print("Well, we need wait some more time till order is filled.")


def check_arbitrage():
    """ checks the arbitrage opportunity; just FYI """
    amount = wf.get_optimum_amount()
    if amount < -1:
        return "{token} is overrated on WaveFlow. There is an arbitrage opportunity: " \
               "spend {amount} WAVES for buying {token} on DEX, then resell {token} on WaveFlow".format(amount=-amount, token="BTC")
    elif amount > 1:
        return "{token} is underrated on WaveFlow. There is an arbitrage opportunity: " \
               "buy {token} on WaveFlow by selling {amount} WAVES, then resell {token} on DEX".format(amount=amount, token="BTC")
    else:
        return "There is no arbitrage opportunity"


def trade():
    """ the main function that finds arbitrage opportunity and uses it to "print" money for you!"""
    print("Your account balance is: " + str(account.balance() / WVS))
    print("Looking for a WAVES/BTC arbitrage opportunity")

    amount = wf.get_optimum_amount()
    if abs(amount) <= 1:
        return "There is no arbitrage opportunity"

    amount = min(amount, account.balance()/WVS)
    if abs(amount) <= 0.05:
        return "You don't have enough balance. Please fill it up to 0.05 WAVES"

    if amount > 1:
        trade_underrate(amount)
    else:
        trade_overrate(amount)


def trade_underrate(amount):
    """
    this func is called if tokenB is underrated on waveflow.xyz (i.e. BTC on waveflow is cheaper then on DEX)
    first step: exchange <amount> WAVES to <amount/wf_price> BTC on WaveFlow
    second step: exchange <amount/wf_price> BTC to <amount*dex_price/wf_price> WAVES on DEX
    arbitrage profit: from <amount> WAVES to <amount*dex_price/wf_price> WAVES
    profit = <amount * (amount*dex_price/wf_price - 1)> WAVES
    """

    print("Arbitrage opportunity found! Going to buy Bitcoins by selling {} WAVES on waveflow.xyz".format(amount))

    tx = wf_exchange(amount)

    print("Congratulations! {} WAVES were exchanged to BTC on waveflow.xyz".format(amount))
    print("Now you have {} BTC".format(account.balance(wf.tokenB)/WVS))
    print("It's time to use these BTC for buying WAVES back on DEX. Creating order.")

    order = complete_order(amount)
    print("Finishing the script...")
    print("Final account balance: " + str(account.balance()/WVS))


def trade_overrate(amount):
    """
    this func is called if tokenB is overrated on waveflow.xyz (i.e. BTC on waveflow is more expensive then on DEX)
    first step: exchange <amount> WAVES to <amount/dex_price> BTC on DEX
    second step: exchange <amount/dex_price> BTC to <amount*wf_price/dex_price> WAVES on WaveFlow
    arbitrage profit: from <amount> WAVES to <amount*wf_price/dex_price> WAVES
    profit = <amount * (wf_price/dex_price - 1)> WAVES
    """

    print("Arbitrage opportunity found! Going to buy Bitcoins on DEX")

    order = complete_order(amount)  # buying BTC on DEX

    print("Congratulations! {} WAVES were exchanged to BTC on DEX".format(amount))
    print("Now you have {} BTC".format(account.balance(wf.tokenB)/WVS))
    print("It's time to use these BTC for buying WAVES back on WaveFlow. Invoking script.")

    # TODO: wait till tokenB fall on the balance after order completing
    tx = wf_exchange(amount)

    print("Exchange completed!")


if __name__ == "__main__":
    trade()

