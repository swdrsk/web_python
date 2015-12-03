#coding:utf-8
import tweepy
import pandas as pd
import time
import datetime
from copy import deepcopy
import pdb

import conv_tools as tools

#### fundamental function ####
#NG_word = ['@','#','http','RT','&amp']
NG_word = ['@','#','RT','&amp']


def get_time():
    return datetime.datetime.now().strftime("%Y/%m/%d %H:%M:%S") 

def remove_NGword(str_array,option='word'):
    '''
    remove NG word from string array of tweet
    option
    word: remove one word
    sentence: remove whole sentense
    '''
    for tweet in str_array:
        if option=='sentence':
            for ngword in NG_word:
                if ngword in tweet:
                    str_array.remove(tweet)
                    break
                
        elif option=='word':
            wordlist = tweet.split(' ')
            wordlist_copy = deepcopy(wordlist)
            for word in wordlist_copy:
                for ngword in NG_word:
                    if ngword in word:
                        wordlist.remove(word)
                        break
            if wordlist == []:
                str_array.remove(tweet)
            else:
                rst_tweet = ' '.join(wordlist)
                str_array[str_array.index(tweet)] = rst_tweet    
    return str_array

class TweetTools:
    def __init__(self,mapfile,account_name):
        self.account_name = account_name
        self.account_datas = pd.read_csv(mapfile,index_col='account')
        self.api = self.authorizing(account_name)
        
    def authorizing(self,account_name):
        key_datas = self.account_datas
        consumer_key = key_datas['consumer_key'][account_name]
        consumer_secret = key_datas['consumer_secret'][account_name]
        access_token = key_datas['access_token'][account_name]
        access_token_secret = key_datas['access_token_secret'][account_name] 
        auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
        auth.set_access_token(access_token, access_token_secret)
        api = tweepy.API(auth)
        return api
        
    def run(self):
        self.streaming()
        #self.print_timeline(6,"ssssss0325")
        #self.pakutui(6,"ssssss0325")

    def read_timeline(self,num,user=''):
        if user=='':
            api = self.api
        else:
            api = self.authorizing(user)

        rst_str = ['' for i in range(num)]
        public_tweets = api.home_timeline()
        for i in range(num):
            tweet = public_tweets[i]
            rst_str[i] =  tweet.text
        return rst_str

    def print_timeline(self,num,user=''):
        if user=='':
            user = self.account_name
        str_array = self.read_timeline(num,user)
        for tweet in str_array:
            print tweet.encode('cp932',errors='replace')#for windows console
            print "---------------------"
            
    def post_tweet(self,sentence,check_flag=True):
        try:
            self.api.update_status(sentence)#.encode('cp932',errors='replace'))
            if check_flag:
                print "posted: \"%s\""%sentence
        except:
            if check_flag:
                print "unposted..."

    def test_post_DM_myself(self):
        """
        for test use, send DirectMessage to oneself
        """
        now = get_time()
        self.post_tweet("d %s test to send direct message to myself, [%s]"%(self.account_name,now))

    def pakutui(self,num,user):
        str_array = self.read_timeline(num,user)
        remove_NGword(str_array,option='word')
        for tweet in str_array:
            self.post_tweet(tweet)
            #s,coding = tools.conv_encoding(tweet)
            #print tweet+"/"+str(coding)
                
        
        
class TweetStreaming:
    def __init__(self,mapfile,account_name):
        self.api = TweetTools(mapfile,account_name).api
    def run(self):
        stream = tweepy.Stream(self.api.auth,myStreamListener(self.api))
        while True:
            try:
                stream.sample()
            except:
                print 'unprintable'
            

    
class myExeption(Exception): pass

class myStreamListener(tweepy.streaming.StreamListener):
    '''
    http://monowasure78.hatenablog.com/entry/2013/11/26/tweepy%E3%81%A7streaming%E3%82%92%E4%BD%BF%E3%81%86    
    '''
    
    def __init__(self,api):
	#データベースに接続するときなどに使えます
        #↓これを忘れると動きません
	super(myStreamListener,self).__init__()
        self.api = tweepy.API(api.auth)
        
    def __del__(self):
	#データベースを閉じることなどに使えます
        return -1
            
    def on_status(self,status):            
	text = status.text #本文
	date = status.created_at #ツイートされた日時（確かdatetime型）
        name = status.author.name #投稿者id名(unicode型、sqlite3で都合が良いので.encode("utf-8")とはしませんでした
	screen_name = status.author.screen_name #投稿者の名前
        img = status.author.profile_image_url #投稿者のプロファイル画像
        lang = status.author.lang
        #fav_count = status.author.favorities_count
        """
        その他にもauthorはid,location,followers_count,status_count,description,friends_count,
        profile_background_image_url,lang,time_zone,following.favorities_count
        などを持っている
        """
        rst = text
        [post] = remove_NGword([text])
        if not rst=='':
            try:
                self.api.update_status(post)
                print "posted: %s"%post
            except: #Exception as e:
                poscopy = deepcoppy(post)
                for char in [poscopy]:
                    try:
                        char.encode('cp932')
                    except:
                        post = post.replace(char,'')
                try:
                    if post=='':
                        self.api.update_status(post)
                        print "posted: %s"%post
                except Exception as e:        
                    print '====== ERROR MESSAGE ======'
                    print 'type:' + str(type(e))
                    print 'args:' + str(e.args)
                    print 'message:' + e.message
                    print 'error:' + str(e)
            time.sleep(5)

        """
        try:
            rst = text.encode('cp932')
            [post] = remove_NGword([rst])
            if not rst=='':
                try:
                    self.api.update_status(post.encode('utf-8'))
                    print "posted: %s"%post
                except tweepy.error.TweetError:
                    self.api.update_status(post.encode('ascii'))
                    print "posted: %s"%post
                except Exception as e:
                    print '=== エラー内容 ==='
                    print 'type:' + str(type(e))
                    print 'args:' + str(e.args)
                    print 'message:' + e.message
                    print 'e自身:' + str(e)
                time.sleep(5)
        except:
            rst = '-'
        """
        
        print rst
        return rst
	#return True

    
    def on_error(self,status):
	print "can't get"
        
    def on_timeout(self):
	raise myExeption
