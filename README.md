# Crypto trading bot: WaveFlow + DEX

Smart trading using crypto price difference on two markets: [DEX](https://dex.wavesplatform.com/) and [WaveFlow.xyz](https://waveflow.xyz/).

### WaveFlow provides arbitrage

Oct, 24 a new application was launched on Waves: https://www.dappocean.io/dapps/waveflow. This project allows crypto holders to create and use exsiting crypto pairs for trading. The price is determined in an algorithmic way: the more popular the token is, the higher its price is set. 

<img src="https://server.vlzhr.top/hosted/662900714-29-13.png" width="250px">

So, WaveFlow pricing model has no relations to DEX which is the main Waves based exchange client. This means there could be an **arbitrage opportunity**: traders can buy crypto asset on WaveFlow for a price `P1` and sell it on DEX for a price `P2` making `P2 - P1` profit in a few seconds. Learn more about arbitrage at [Investopedia]( https://www.investopedia.com/ask/answers/what-is-arbitrage/) for a better understanding if needed.

This bot is made to find the arbitrage opportunities and immediately use them doing the exchange operations on [DEX](https://dex.wavesplatform.com/) and [WaveFlow](https://waveflow.xyz/). Right now bot does trading operations for a pair WAVES/BTC only. Welcome any contributions =)

### Arbitrage step-by-step

Bot algorithm for WAVES/BTC pair arbitrage trading is the following:

_waveflow_handler.get_optimum_amount_

1. Getting `current_dex_price` for a pair
2. Determining if BTC is under- or overrated on WaveFlow and storing this value to `dest`
3. Finding the most profitable `amount` of WAVES to trade using reversed WaveFlow algorithm

_bot.trade_

4. If BTC underrated: buy BTC on WaveFlow -> sell BTC on DEX
5. If BTC overrated: buy BTC on DEX -> sell BTC on WaveFlow

#### Arbitrage profit counting

Assume, BTC price on WaveFlow is cheaper than the price on DEX. It will stay cheaper if we spend less than `amount` WAVES for buying BTC on WaveFlow. `amount` is determined following the WaveFlow algorithm.

We decide to sell `amount` WAVES on WaveFlow and get `amount*wf_price` BTC

Now we can exchange these `amount*wf_price` BTC back to WAVES on DEX. The price for this will be `dex_price`. We will get `amount*wf_price/dex_price` WAVES from selling our BTC

The final profit will be `amount*wf_price/dex_price - amount` = `amount*(wf_price/dex_price - 1)`

### Usage

You will need Python to run the bot. 

Please install `requests` and `pywaves` libraries and run `trade()` function in `bot.py`.

### Conclusion

The WAVES/BTC pair is ready for the arbitrage trading. Please feel free to use this bot for "printing" money and contribute for adding new pairs like WAVES/ETH. 
