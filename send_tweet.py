#encoding:utf-8

from tweet_tools import *

FILE = "accounts.csv"
NAME = "subswd2"

twitools = TweetTools(FILE,NAME)
twitools.run()
