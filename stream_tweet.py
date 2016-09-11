#encoding:utf-8

from tweet_tools import *
import random

FILE = "./accounts.csv"
NAME = "subswd2"

twistream = TweetStreaming(FILE,NAME)
twistream.run()

#twitools = TweetTools(FILE,NAME)
#twitools.post_tweet("%f"%random.random())
#twitools.delete_reply_tweet(100)
