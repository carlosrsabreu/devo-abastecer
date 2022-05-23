import tweepy
import json
import os

from keys import *
 
def main():
    client = tweepy.Client(
            consumer_key = os.environ['CONSUMER_KEY'],
            consumer_secret = os.environ['CONSUMER_SECRET'],
            access_token = os.environ['ACCESS_TOKEN'],
            access_token_secret = os.environ['ACCESS_TOKEN_SECRET']
            )
 
    f = open('gas_info.json')
    data_gas_info = json.load(f)

    gasoline_98 = {GAS_NAME_KEY: "Gasolina 98", GAS_PRICE_KEY: []}
    gasoline_95 = {GAS_NAME_KEY: "Gasolina 95", GAS_PRICE_KEY: []}
    diesel = {GAS_NAME_KEY: "Gasóleo       ", GAS_PRICE_KEY: []}

    for i in data_gas_info[THIS_WEEK][GAS_KEY]:
      if (i[GAS_NAME_KEY] == 'Gasolina IO95'):
        gasoline_95[GAS_PRICE_KEY].append(i[GAS_PRICE_KEY])
      if (i[GAS_NAME_KEY] == 'Gasóleo Rodoviário'):
        diesel[GAS_PRICE_KEY].append(i[GAS_PRICE_KEY])

    for i in data_gas_info[NEXT_WEEK][GAS_KEY]:
      if (i[GAS_NAME_KEY] == 'Gasolina IO95'):
        gasoline_95[GAS_PRICE_KEY].append(round(i[GAS_PRICE_KEY], 3))
      if (i[GAS_NAME_KEY] == 'Gasóleo Rodoviário'):
        diesel[GAS_PRICE_KEY].append(round(i[GAS_PRICE_KEY], 3))

    for i in gasoline_95[GAS_PRICE_KEY]:
      gasoline_98[GAS_PRICE_KEY].append(round(i + DIFFERENCE_95_98_PRICE, 3))

    def gas_prices_message(price_this_week, price_next_week):
      if (price_this_week < price_next_week):
        return f'{price_this_week}€   ⬆️     {price_next_week}€'
      if (price_this_week > price_next_week):
        return f'{price_this_week}€   ⬇️     {price_next_week}€'
      if (price_this_week == price_next_week):
        return f'{price_this_week}€   =     {price_next_week}€'

    tweet_gas_prices = ''

    for i in [diesel, gasoline_95, gasoline_98]:
      tweet_gas_prices += f"{i[GAS_NAME_KEY]}   {gas_prices_message(i[GAS_PRICE_KEY][0], i[GAS_PRICE_KEY][1])}\n"

    tweet_message = '— Devo abastecer? ⛽️ \n\n'
    tweet_start_dates = f"         {data_gas_info[THIS_WEEK][START_DATE_KEY]}  |  {data_gas_info[NEXT_WEEK][START_DATE_KEY]}\n"
    tweet_interval_dates = f"                      a         |            a\n"
    tweet_end_dates = f"         {data_gas_info[THIS_WEEK][END_DATE_KEY]}  |  {data_gas_info[NEXT_WEEK][END_DATE_KEY]}\n\n"

    tweet = f"{tweet_message}{tweet_start_dates}{tweet_interval_dates}{tweet_end_dates}{tweet_gas_prices}"
    client.create_tweet(text=tweet)
 
if __name__ == "__main__":
    main()
