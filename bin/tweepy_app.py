import sys
import tweepy
import json
import matplotlib.pyplot as plt; plt.rcdefaults()
import numpy as np
import matplotlib.pyplot as plt
from bin.coin import Coin
import pickle
import requests
from datetime import datetime

MAX_TWEETS = 400
TOP_X = 5

def api_access():
    config = {}
    with open('config.json') as file:
        config.update(json.load(file))
    return config

def create_joint_plots(saved_coins_data):
    # Create joint plot of Tweet Velocity and Price over time
    for coin in saved_coins_data:
        fig = plt.figure()
        ax = fig.add_subplot(111, label="1")
        ax2 = fig.add_subplot(111, label="2", frame_on=False)

        ax.plot(coin.dates, coin.vels, color="C0")
        ax.set_xlabel("Datetime", color="black")
        ax.set_ylabel("Tweet Velocity (twt/min)", color="C0")
        ax.tick_params(axis='x', colors="black")
        ax.tick_params(axis='y', colors="C0")
        ax.grid(True)

        ax2.plot(coin.dates, coin.mkt_caps, color="C1")
        ax2.yaxis.tick_right()
        ax2.set_ylabel('Price (USD)', color="C1")

        ax2.yaxis.set_label_position('right')
        ax2.tick_params(axis='y', colors="C1")
        ax2.xaxis.set_visible(False)
        plt.setp(ax.get_xticklabels(), rotation=30, horizontalalignment='right')
        plt.title('%s Tweet Velocity & Price Over Time' % coin.symbol)
        plt.tight_layout(w_pad=0.5)
        plt.savefig('../outputs/%s_vel_vs_time.png' % coin.symbol)
        plt.close()

def all():

    saved_coins_data = []

    #check command line arguments
    #if argv[1]=='fresh' then we delete past data and start a fresh run
    if (not (len(sys.argv) > 1 and sys.argv[1]=='fresh')):
        #load pat coin data from pickle file
        #this data is stored from previous prgram executions
        with open(r"../bin/save_data.pickle", "rb") as input_file:
            saved_coins_data = pickle.load(input_file)
        #saved_coins_data = pickle.load(bin/save_data.p", "rb" ) )
        #print (len(saved_coins_data))
        #print (len(saved_coins_data[0].dates))
        #print (len(saved_coins_data[0].mktCaps))
        #print (len(saved_coins_data[0].vels))
    else:
        print('Cmd line arg used. Deleted past coin data.')


    #Get top 100 coins data from coinmarketcap.com
    url = "https://api.coinmarketcap.com/v1/ticker/"
    response = requests.get(url)
    coin_mkt_cap_json = json.loads(response.content.decode('utf-8'))

    #Connect to Twitter API
    config = api_access()
    consumer_key = config["consumer_key"]
    consumer_secret = config["consumer_secret"]
    access_token = config["access_token"]
    access_token_secret = config["access_token_secret"]

    auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
    auth.set_access_token(access_token, access_token_secret)

    #Instantiate Tweepy API for searching tweets
    api = tweepy.API(auth, wait_on_rate_limit=True, wait_on_rate_limit_notify=True)

    #Extract top 100 tickers and store relevant data in table
    tickers = []
    mkt_caps = []
    prices = []
    headers = ["Symbol", "Market Cap", "Price", "Percent Change 24h"]
    table = []
    for coins in coin_mkt_cap_json[0:TOP_X]:
        tickers.append('$' + coins['symbol'])
        mkt_caps.append(coins["market_cap_usd"])
        prices.append(coins['price_usd'])
        table.append([coins['symbol'],
                      coins["market_cap_usd"],
                      coins['price_usd'],
                      coins["percent_change_24h"]])

    #Get tweets for each coin ticker in top 100
    coins_tweet_velocity = [None]*TOP_X
    coins_mkt_cap_vel_ratio = [None]*TOP_X
    created_at_format = '%a %b %d %H:%M:%S +0000 %Y'
    for i in range(TOP_X):
        coin_tweets = tweepy.Cursor(api.search, q=tickers[i]).items(MAX_TWEETS)

        youngest_tweet = next(coin_tweets)
        oldest_tweet = None
        for oldest_tweet in coin_tweets:
            pass
        age = (youngest_tweet.created_at - oldest_tweet.created_at).total_seconds()
        print ('age: ', age)
        #age = time.time() - (old_created_at - datetime(1970, 1, 1)).total_seconds()
        tweet_velocity = ((MAX_TWEETS / age) * 60)
        coins_tweet_velocity[i] = tweet_velocity
        coins_mkt_cap_vel_ratio[i] = tweet_velocity/float(table[i][1])
        print('For: ', tickers[i])
        print('Tweeted:', str(oldest_tweet.created_at) + ', age in minutes:', age / 60)
        print('Tweet velocity = %f tweets/min' % ((MAX_TWEETS / age) * 60))
        print('##########')


    # Create barchart from velocities
    bar_chart_objs = tuple(tickers)
    y_pos = np.arange(TOP_X)
    plt.bar( y_pos, coins_tweet_velocity, align='center', alpha=0.5)
    plt.xticks(y_pos, bar_chart_objs)
    plt.ylabel('Tweet Velocity')
    plt.title('Crypto Tweet Velocities')

    plt.savefig('../outputs/coins_tweet_velocity.png')
    plt.close()

    #Create barchart from marketcap/velocity ratios
    plt.bar( y_pos, coins_mkt_cap_vel_ratio, align='center', alpha=0.5)
    plt.xticks(y_pos, bar_chart_objs)
    plt.ylabel('Ratio')
    plt.title('Coin Mkt Cap / Tweet Velocity Ratio')
    #plt.show()

    plt.savefig('../outputs/coins_mkt_cap_vel_ratio.png')
    plt.close()

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




###main program
all()
