from bs4 import BeautifulSoup
from decimal import *

import csv

"""
<tr id="id-bitcoin" class="">
<td class="text-center">
1
</td>
<td class="no-wrap currency-name" data-sort="Bitcoin">
<div class="s-s-1 logo-sprite"></div>
<span class="currency-symbol"><a href="/currencies/bitcoin/">BTC</a></span>
<a class="currency-name-container" href="/currencies/bitcoin/">Bitcoin</a>
</td>
<td class="text-left col-symbol">BTC</td>
<td class="no-wrap market-cap text-right" data-usd="1.56447534337e+11" data-btc="17006812.0" data-sort="1.56447534337e+11">
$156,447,534,337
</td>
<td class="no-wrap text-right" data-sort="9199.11">
<a href="/currencies/bitcoin/#markets" class="price" data-usd="9199.11" data-btc="1.0">$9199.11</a>
</td>
<td class="no-wrap text-right circulating-supply" data-sort="17006812.0">
<a href="https://blockchain.info/" target="_blank" rel="nofollow noopener" data-supply="17006812.0" data-supply-container>
17,006,812</a>
</td>
<td class="no-wrap text-right " data-sort="8312710000.0">
<a href="/currencies/bitcoin/#markets" class="volume" data-usd="8312710000.0" data-btc="905106.0">$8,312,710,000</a>
</td>
<td class="no-wrap percent-change  negative_change text-right" data-timespan="1h" data-percentusd="-0.53" data-symbol="BTC" data-sort="-0.525669">-0.53%</td>
<td class="no-wrap percent-change  negative_change text-right" data-timespan="24h" data-percentusd="-1.64" data-symbol="BTC" data-sort="-1.63797">-1.64%</td>
<td class="no-wrap percent-change  positive_change  text-right" data-timespan="7d" data-percentusd="3.38" data-symbol="BTC" data-sort="3.38138">3.38%</td>
</tr>
<tr id="id-ethereum" class="">
<td class="text-center">
2
</td>
<td class="no-wrap currency-name" data-sort="Ethereum">
<div class="s-s-1027 logo-sprite"></div>
<span class="currency-symbol"><a href="/currencies/ethereum/">ETH</a></span>
<a class="currency-name-container" href="/currencies/ethereum/">Ethereum</a>
</td>
<td class="text-left col-symbol">ETH</td>
<td class="no-wrap market-cap text-right" data-usd="67875428311.8" data-btc="7390421.73318" data-sort="67875428311.8">
$67,875,428,312
</td>
<td class="no-wrap text-right" data-sort="684.655">
<a href="/currencies/ethereum/#markets" class="price" data-usd="684.655" data-btc="0.0745467">$684.65</a>
</td>
<td class="no-wrap text-right circulating-supply" data-sort="99138147.4053">
<a href="https://etherscan.io/" target="_blank" rel="nofollow noopener" data-supply="99138147.4053" data-supply-container>
99,138,147</a>
</td>
<td class="no-wrap text-right " data-sort="2724970000.0">
<a href="/currencies/ethereum/#markets" class="volume" data-usd="2724970000.0" data-btc="296700.0">$2,724,970,000</a>
</td>
<td class="no-wrap percent-change  positive_change  text-right" data-timespan="1h" data-percentusd="0.57" data-symbol="ETH" data-sort="0.569181">0.57%</td>
<td class="no-wrap percent-change  positive_change  text-right" data-timespan="24h" data-percentusd="0.16" data-symbol="ETH" data-sort="0.162584">0.16%</td>
<td class="no-wrap percent-change  positive_change  text-right" data-timespan="7d" data-percentusd="7.40" data-symbol="ETH" data-sort="7.40099">7.40%</td>
</tr>
"""

getcontext().prec = 16

page_file = open('all.html')
page_text = page_file.read()
page_file.close()

# Prepare CSV writer
all_coins_file = open('all_coins.csv', 'w')
fieldnames = ['symbol', 'price_btc', 'circulating_supply']
writer = csv.DictWriter(all_coins_file, fieldnames=fieldnames)
writer.writeheader()

# Extract data
page_dom = BeautifulSoup(page_text, "html.parser")
coins_rows = page_dom.select("table#currencies-all tr")

for coin_row in coins_rows:
    coin_name_tag = coin_row.select_one("td.currency-name")
    if coin_name_tag is None:
        continue

    name = coin_name_tag.attrs['data-sort']

    coin_link_tag = coin_name_tag.select_one("span > a")
    symbol = coin_link_tag.text
    link = coin_link_tag.attrs['href']

    coin_price_tag = coin_row.select_one("a.price")

    try:
        price_usd = Decimal(coin_price_tag.attrs['data-usd'])
    except InvalidOperation:
        price_usd = None

    try:
        price_btc = Decimal(coin_price_tag.attrs['data-btc'])
    except InvalidOperation:
        price_btc = None

    circulating_supply = Decimal(coin_row.select_one("td.circulating-supply").attrs['data-sort'])

    print(name, symbol, "{0:.16}".format(price_usd), "{0:.16}".format(price_btc), "{0:.16}".format(circulating_supply))
    writer.writerow({'symbol': symbol, 'price_btc': price_btc, 'circulating_supply': circulating_supply})

all_coins_file.close()