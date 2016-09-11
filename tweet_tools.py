#coding:utf-8
import tweepy
import pandas as pd
import time
import datetime
import urllib
from copy import deepcopy
import pdb
import random

import conv_tools as tools

#### fundamental function ####
#NG_word = ['@','#','http','RT','&amp']
NG_word = ['@','#','RT','&amp']
NG_word.append("http")
#image_filter = ['https://t.co/']

encode_table = ['utf_8','utf-8', 'euc_jp','cp932', 'euc_jis_2004', 'euc_jisx0213','shift_jis', 'shift_jis_2004','shift_jisx0213','iso2022jp', 'iso2022_jp_1', 'iso2022_jp_2', 'iso2022_jp_3','iso2022_jp_ext','latin_1', 'ascii']

reply_list = [""]

stack_imagename = ["./default_image%d.jpg"%i for i in range(5)]
stack_videoname = "./default_movie.mp4"

def get_time():
    return datetime.datetime.now().strftime("%Y/%m/%d %H:%M:%S") 

def filter_word(str_array,option='word'):
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

        elif option=="filter_image":
            for word in image_filter:
                if word in tweet:
                    break
            else:
                str_array.remove(tweet)
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

    def delete_reply_tweet(self,N=5000):
        """
        delete reply for anyone, N stands how many tweet to review
        """
        for status in tweepy.Cursor(self.api.user_timeline).items(N):
            if status.text[0]=="@":
                self.api.destroy_status(status.id)
                print "delete: "+str(status.id)
            
    def post_tweet(self,sentence,check_flag=True):
        pdb.set_trace()
        try:
            self.api.update_status(sentence)#.encode('cp932',errors='replace'))
            if check_flag:
                print "posted: \"%s\""%sentence
        except Exception as e:
            if check_flag:
                print "unposted. ERROR as: "+str(e)

    def test_post_DM_myself(self):
        """
        for test use, send DirectMessage to oneself
        """
        now = get_time()
        self.post_tweet("d %s test to send direct message to myself, [%s]"%(self.account_name,now))

    def pakutui(self,num,user):
        str_array = self.read_timeline(num,user)
        filter_word(str_array,option='word')
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
            except Exception as e:
                print "ERROR as: "+str(e)
            

    
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
        sleep_time = 5
	text = status.text #本文
	date = status.created_at #ツイートされた日時（確かdatetime型）
        name = status.author.name #投稿者id名(unicode型、sqlite3で都合が良いので.encode("utf-8")とはしませんでした
	screen_name = status.author.screen_name #投稿者の名前
        img = status.author.profile_image_url #投稿者のプロファイル画像
        lang = status.author.lang
        retweet_count = status._json["retweet_count"]
        #fav_count = status.author.favorities_count
        """
        その他にもauthorはid,location,followers_count,status_count,description,friends_count,
        profile_background_image_url,lang,time_zone,following.favorities_count
        などを持っている
        """
        #pdb.set_trace()
        
        # filter proccessing
        if text=="":
            return False
        if not status._json.has_key("retweeted_status"):
            return True
        retweeted = status._json["retweeted_status"]
        r_count = retweeted["retweet_count"]
        f_count = retweeted["favorite_count"]
        if r_count<100 or f_count<100:
            return True
        if not retweeted["entities"].has_key("media"):
            return True
        media_urls = []
        media_type = None
        index=0
        for item in status.extended_entities["media"]:
            if item["type"]=="photo":
                media_type = "photo"
                urllib.urlretrieve(item["media_url"],stack_imagename[index])
                index += 1
            elif item["type"]=="animated_gif" or item["type"]=="video":
                media_type = "video"
                urllib.urlretrieve(item["video_info"]["variants"][0]["url"],stack_videoname)
            media_urls.append(item["display_url"])
        #if media_urls==[]:
        #    print "has no media_url"
        #    return True
        try:
            [post] = filter_word([text])
            #post = post+" "+media_urls[0]
            #[post] = filter_word(filter_word([text],option="word"),option="filter_image")
        except Exception as e:
            return
        reply_to = reply_list[random.randint(0,len(reply_list)-1)]
        post = reply_to+post
        if not [post]==[]:
            try:
                #print type(post)
                #self.api.update_status(post)
                if media_type=="photo":
                    self.api.update_with_media(filename=stack_imagename[0],status=post)
                elif media_type=="video":
                    self.api.update_with_media(filename=stack_videoname,status=post)
                print "posted[%s]: %s"%(lang,post)
            except Exception as e:
                print str(e)
            """
            except: #Exception as e:
                poscopy = deepcopy(post)
                for char in [poscopy]:
                    for encoding in encode_table:
                        try:
                            char.encode(encoding)
                            break
                        except:
                            pass
                    else:
                        post = post.replace(char,'')
                try:
                    if not post==u'':
                        self.api.update_status(str(post))
                        #print "posted: %s"%post
                except Exception as e:        
                    print '====== ERROR MESSAGE ======'
                    print 'type:' + str(type(e))
                    print 'args:' + str(e.args)
                    print 'message:' + e.message
                    print 'error:' + str(e)
            """
            time.sleep(sleep_time)

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
        
        print text
        return text
	#return True

    
    def on_error(self,status):
	print "can't get"
        
    def on_timeout(self):
	raise myExeption
