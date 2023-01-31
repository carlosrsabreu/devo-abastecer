# ⛽️ Devo Abastecer (_beta_)

[![⛽️ Update Gas Prices from DRETT](https://github.com/carlosrsabreu/devo-abastecer/actions/workflows/update_gas_prices.yml/badge.svg?branch=main)](https://github.com/carlosrsabreu/devo-abastecer/actions/workflows/update_gas_prices.yml)
[![📈 Publish History Plot](https://github.com/carlosrsabreu/devo-abastecer/actions/workflows/post_plot_history.yml/badge.svg?branch=main)](https://github.com/carlosrsabreu/devo-abastecer/actions/workflows/post_plot_history.yml)
[![💅 Format Codebase](https://github.com/carlosrsabreu/devo-abastecer/actions/workflows/format_codebase.yml/badge.svg?branch=main)](https://github.com/carlosrsabreu/devo-abastecer/actions/workflows/format_codebase.yml)

🇵🇹 Informação acessível com os preços dos combustíveis na Madeira, publicada semanalmente no Twitter recorrendo a um bot.<br> 🇬🇧 Up-to-date fuel prices in Madeira, conveniently updated weekly on Twitter via our automated bot.

## Functionality overview

### Sequence summary

```mermaid
sequenceDiagram
    participant 🐍 update_gas_prices
    participant 🐍 post_tweet
    participant 🐍 add_history
    participant 🌐 drett

    🐍 update_gas_prices ->> 🌐 drett:GET (HTML content)
    🌐 drett -->> 🐍 update_gas_prices: beautifulSoup object
    🐍 update_gas_prices -->> 🐍 update_gas_prices: extract 📄 from beautifulSoup object
    🐍 update_gas_prices ->> 🐍 update_gas_prices: 💾 gas_info.json
    🐍 update_gas_prices -->> 🐍 update_gas_prices: compare (current date : previous date)
    🐍 update_gas_prices -->> 🐍 update_gas_prices: post a tweet
    🐍 update_gas_prices ->> 🐍 post_tweet: 📄 make_tweet
    🐍 post_tweet -->> 🐍 post_tweet: compare(current price : previous price)
    🐍 update_gas_prices ->> 🐍 add_history: 📄 add_history
    🐍 add_history ->> 🐍 add_history: 💾 gas_info_history.json
    🐍 add_history ->> 🐍 add_history: 💾 gas_info_history.csv

```

### Summary

The `update_gas_prices.py` parses content of DRETT website, and extracts the gas price data it needs using `beautifulSoup` object. Then it opens the `gas_info.json` containing previous data and compares the dates of new and previous data. If the new date is different it then, updates the `gas_info.json` and post a tweet using `post_tweet.py` which also compares the previous price and represents it within the tweet. Finally it uses `add_history.py` to add the new data to `gas_info_history.{csv,json}`.
