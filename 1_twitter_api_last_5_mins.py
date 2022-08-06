# ----- Twitter API Test - Search Tweets by Keyword -----

# Import stuff
import tweepy
import configparser
import pandas as pd
from dateutil import parser
import win32com.client as win32

# Attempt to load current tweets as df and get max tweeted at time
# If the dataframe can't be found, or is empty, we will load all tweets up to limit at the end
# If we can get a max time, we'll just load the tweets from after that time
og_df = pd.DataFrame
og_max_found = False
og_tweeted_at_max = "1900/01/01"

try:
    og_df = pd.read_csv("C:\\Users\\Jeremy\\PycharmProjects\\pythonProject1\\twitter_feedback_test\\last_5min_tweets.csv", header=0)
    og_file_exists = True
except FileNotFoundError:
    og_file_exists = False

if og_file_exists and not og_df.empty:
    og_tweeted_at = og_df["Tweeted_at"]
    og_tweeted_at_max = og_tweeted_at.max()
    og_max_found = True
    print("Existing file and max tweet time found.")
    print(og_tweeted_at_max)
elif og_file_exists and og_df.empty:
    print("Existing file found but is empty.")
else:
    print("No existing file found.")

# Convert og max tweet time to datetime object
og_tweeted_at_max_dt = parser.parse(og_tweeted_at_max)

# Read credentials from config
config = configparser.ConfigParser()
config.read("C:\\Users\\Jeremy\\PycharmProjects\\pythonProject1\\twitter_feedback_test\\config.ini")

api_key = config["twitter"]["api_key"]
api_key_secret = config["twitter"]["api_key_secret"]

access_token = config["twitter"]["access_token"]
access_token_secret = config["twitter"]["access_token_secret"]

# Authentication
auth = tweepy.OAuthHandler(api_key, api_key_secret)
auth.set_access_token(access_token, access_token_secret)

api = tweepy.API(auth)

# Search tweets - cursor is used to increase available tweets from 100 limit - limit is the most recent tweets
# keywords = "@gcntweet"
keywords = "@jeremygould_"
limit = 300
tweets = tweepy.Cursor(api.search_tweets, q=keywords, count=100, tweet_mode="extended").items(limit)

# Create dataframe to store tweet data
columns = ["Tweet_ID", "Tweeted_at", "User", "Tweet"]
data = []
alert_data = []
potential_alerts = 0
for tweet in tweets:
    if og_max_found:
        if tweet.created_at > og_tweeted_at_max_dt:
            data.append([tweet.id_str, tweet.created_at, tweet.user.screen_name, tweet.full_text])
            # check if tweet is potential alert - but only want emails for new cases
            alert_tweet = False
            if tweet.full_text.find("stream") != -1 and tweet.full_text.find("down") != -1:
                alert_tweet = True
            if tweet.full_text.find("broken") != -1:
                alert_tweet = True
            if tweet.full_text.find("problem") != -1:
                alert_tweet = True
            if tweet.full_text.find("issue") != -1:
                alert_tweet = True
            # if any alert criteria met, append to alert tweets and increment counter
            if alert_tweet:
                alert_data.append([tweet.id_str, tweet.created_at, tweet.user.screen_name, tweet.full_text])
                potential_alerts += 1
    else:
        data.append([tweet.id_str, tweet.created_at, tweet.user.screen_name, tweet.full_text])

newdata_df = pd.DataFrame(data, columns=columns)
alert_df = pd.DataFrame(alert_data, columns=columns)

# If newdata_df not empty, i.e. we have new tweets, insert above existing tweets and output as csv
# If we don't have any new tweets, don't output anything
if not newdata_df.empty and not og_df.empty:
    output_df = pd.concat([newdata_df,og_df])
    output_df.to_csv("C:\\Users\\Jeremy\\PycharmProjects\\pythonProject1\\twitter_feedback_test\\last_5min_tweets.csv", index=False)
    print("New tweets added to file.")
elif not newdata_df.empty and og_df.empty:
    newdata_df.to_csv("C:\\Users\\Jeremy\\PycharmProjects\\pythonProject1\\twitter_feedback_test\\last_5min_tweets.csv", index=False)
    print("New tweets added to file.")
else:
    print("No new tweets. No output generated.")

# If alert data not empty, then send email with alert counter and tweets attached
if not alert_df.empty:
    alert_df.to_csv("C:\\Users\\Jeremy\\PycharmProjects\\pythonProject1\\twitter_feedback_test\\potential_alert_tweets.csv", index=False)

    # construct Outlook application instance
    olApp = win32.Dispatch("Outlook.Application")
    olNS = olApp.GetNameSpace("MAPI")

    # construct email item object
    mailItem = olApp.CreateItem(0)  # 0 relates to olMailItem - see outlook.olitem type microsoft docs for more info
    mailItem.Subject = str(potential_alerts) + " tweet(s) received indicating a potential issue"
    mailItem.BodyFormat = 1
    mailItem.Body = "Please see attached. \n\nWe have received "\
                    + str(potential_alerts)\
                    + " tweet(s) that may indicate a potential issue and require review."
    mailItem.To = "jeremygould94@gmail.com"
    mailItem.Attachments.Add("C:\\Users\\Jeremy\\PycharmProjects\\pythonProject1\\twitter_feedback_test\\potential_alert_tweets.csv")
    # mailItem.Attachments.Add(os.path.join(os.getcwd(), "potential_alert_tweets.csv"))
    mailItem.Send()
