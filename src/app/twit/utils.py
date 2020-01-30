import tweepy
from .models import Tweetv2, TwitUserv2
from django.conf import settings
from pymongo import MongoClient
import json


def GetMongo_client(collection_name='django'):
	a = 'mongodb://root:pleaseUseAStr0ngPassword@mongod:27017/admin'
	client = MongoClient(a)
	db = client['%s' % collection_name]


	# >> > db.twit_tweet
	# Collection(
	# 	Database(MongoClient(host=['mongod:27017'], document_class=dict, tz_aware=False, connect=True), 'django'),
	# 	'twit_tweet')
	# >> > db.list_collection_names()
	# ['__schema__', 'twit_tweet', 'django_migrations']

	return db


class TwitStreamListener(tweepy.StreamListener):

	def __init__(self, tweetCount):
		self.tweetCount = 0
		self.tweetLimit = tweetCount

	def on_connect(self):
		print("Connection established!!")

	def on_disconnect(self,notice):
		print("Connection lost!! : ", notice)

	def on_data(self, data):
		if self.tweetCount < self.tweetLimit:
			# process data here
			all_data = json.loads(data)
			#if all_data['coordinates'] is not None:
			user = dict((k, all_data['user'][k]) for k in ('name', 'screen_name', 'location', 'description'))

			hashtags = list(k['text'] for k in all_data['entities']['hashtags'])
			entry = {
				#'created_at': all_data['created_at'].split()[:4],
				'text': all_data['text'],
				'coordinates': all_data.get('coordinates', list()),
				'hashtags': hashtags,
				'user': TwitUserv2(**user)
			}
			Tweetv2(**entry).save()
			print(data)
			self.tweetCount += 1
		else:
			# this stop the streamer
			return False

	def on_error(self, status_code):
		if status_code in [420, 429]:
			# returning False in on_error disconnects the stream
			return False


class TwitStreamer(object):

	# use geopy to get coardinates location and index it

	def __init__(self,total_tweets):
		isinstance(total_tweets, int)

		auth = tweepy.OAuthHandler(settings.CONSUMER_KEY, settings.CONSUMER_SECRET)
		auth.set_access_token(settings.ACCESS_TOKEN, settings.ACCESS_SECRET)
		self.Stream = tweepy.Stream(auth, listener=TwitStreamListener(total_tweets))

	def start(self, keywords):
		isinstance(keywords, list)
		assert len(keywords) > 0, 'keywords list is empty'
		# streamer docs
		# https://developer.twitter.com/en/docs/tweets/filter-realtime/guides/basic-stream-parameters
		# self.Stream.filter(track=["car"])
		self.Stream.filter(languages=['en'],track=keywords)



# class TwitSearch(object):
#
# 	def __init__(self,keywords):
# 		# init tweepy auth
# 		auth = tweepy.AppAuthHandler(settings.CONSUMER_KEY, settings.CONSUMER_SECRET)
# 		self.api = tweepy.API(auth)
# 		self.keywords = keyswords
#
# 	def start(self):
# 		pass
