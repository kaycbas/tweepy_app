import sys
import tweepy
import json
import matplotlib.pyplot as plt;
import numpy as np
from bin.coin import Coin
import pickle
import requests
from datetime import datetime

MAX_TWEETS = 200
TOP_X = 5


def api_access():
    config = {}
    with open('config.json') as file:
        config.update(json.load(file))
    return config


def create_bar_chart(x_axis_vals, y_axis_vals, x_label, y_label, title, file):
    x_tuple_vals = tuple(x_axis_vals)
    y_pos = np.arange(TOP_X)
    plt.bar(y_pos, y_axis_vals, align='center', alpha=0.5)
    plt.xticks(y_pos, x_tuple_vals)
    plt.ylabel(y_label)
    plt.title(title)
    plt.savefig('../outputs/' + file)
    plt.close()


def create_joint_plots(saved_coins_data):
    # plots tweet velocity and price over time
    for coin in saved_coins_data:
        fig = plt.figure()
        ax = fig.add_subplot(111, label="1")
        ax2 = fig.add_subplot(111, label="2", frame_on=False)

        ax.plot(coin.get_dates(), coin.get_vels(), color="C0")
        ax.set_xlabel("Datetime", color="black")
        ax.set_ylabel("Tweet Velocity (twt/min)", color="C0")
        ax.tick_params(axis='y', colors="C0")
        ax.grid(True)

        ax2.plot(coin.get_dates(), coin.get_mkt_caps(), color="C1")
        ax2.set_ylabel('Price (USD)', color="C1")
        ax2.yaxis.tick_right()
        ax2.yaxis.set_label_position('right')
        ax2.tick_params(axis='y', colors="C1")
        ax2.xaxis.set_visible(False)
        #set num ticks
        y_loc = plt.MaxNLocator(10)
        ax2.yaxis.set_major_locator(y_loc)

        plt.setp(ax.get_xticklabels(), rotation=30, horizontalalignment='right')
        plt.title('%s Tweet Velocity & Price Over Time' % coin.symbol)
        plt.tight_layout(w_pad=0.5)
        plt.savefig('../outputs/%s_vel_vs_time.png' % coin.symbol)
        plt.close()


saved_coins_data = []

#load saved data inless cmd line arg 'fresh' for fresh run
if (not (len(sys.argv) > 1 and sys.argv[1]=='fresh')):
    with open(r"../bin/save_data.pickle", "rb") as input_file:
        saved_coins_data = pickle.load(input_file)
else:
    print('Cmd line arg used. Deleted past coin data.')


#Get top 100 coins data from coinmarketcap.com
print ("Getting CoinMarketCap data...")
url = "https://api.coinmarketcap.com/v1/ticker/"
response = requests.get(url)
coin_mkt_cap_json = json.loads(response.content.decode('utf-8'))

#Connect to Twitter API
config = api_access()
consumer_key = config["consumer_key"]
consumer_secret = config["consumer_secret"]
access_token = config["access_token"]
access_token_secret = config["access_token_secret"]

print ("Connecting to Twitter API...")
auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_token, access_token_secret)

#Instantiate Tweepy API for searching tweets
api = tweepy.API(auth, wait_on_rate_limit=True, wait_on_rate_limit_notify=True)

#Extract and store info on top 100 coins
tickers = []
mkt_caps = []
prices = []
for coins in coin_mkt_cap_json[0:TOP_X]:
    tickers.append('$' + coins['symbol'])
    mkt_caps.append(coins["market_cap_usd"])
    prices.append(coins['price_usd'])


coins_tweet_velocity = [None]*TOP_X
coins_mkt_cap_vel_ratio = [None]*TOP_X

#Get tweets for each coin ticker in top 100 and caluclate vel & ratio
for i in range(TOP_X):
    print("For: $"+ coin_mkt_cap_json[i]['symbol'])
    coin_tweets = tweepy.Cursor(api.search, q=coin_mkt_cap_json[i]['symbol']).items(MAX_TWEETS)

    youngest_tweet = next(coin_tweets)
    oldest_tweet = None
    for oldest_tweet in coin_tweets:
        pass
    age = (youngest_tweet.created_at - oldest_tweet.created_at).total_seconds()
    tweet_velocity = ((MAX_TWEETS / age) * 60)
    coins_tweet_velocity[i] = tweet_velocity
    coins_mkt_cap_vel_ratio[i] = (tweet_velocity/float(coin_mkt_cap_json[i]['market_cap_usd']))
    print('Tweet velocity = %f tweets/min' % ((MAX_TWEETS / age) * 60))
    print('##########')


#create bar chart
create_bar_chart(tickers, coins_tweet_velocity, 'Coins', 'Tweet Velocity (twts/min)',
                    'Crypto Tweet Velocities', 'coins_tweet_velocities.png')
create_bar_chart(tickers, coins_mkt_cap_vel_ratio, 'Coins', 'Tweet Velocity (twts/min)',
                    'Crypto Tweet Velocities', 'coins_tweet_vel_ratio.png')

#updates the saved_coins_data with new coin data
for i in range(TOP_X):
    already_exists = False
    for c in saved_coins_data:
        if c.symbol == tickers[i]:
            c.add_data(datetime.now(), prices[i], coins_tweet_velocity[i])
            already_exists = True
            break
    if (not already_exists):
        c = Coin(tickers[i])
        c.add_data(datetime.now(), prices[i], coins_tweet_velocity[i])
        saved_coins_data.append(c)


create_joint_plots(saved_coins_data)

#pickles saved_coins_data for access on next execution
with open(r"../bin/save_data.pickle", "wb") as output_file:
    pickle.dump(saved_coins_data, output_file)


