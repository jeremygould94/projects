# -------------------------------- Customer feedback review using sentiment analysis -----------------------------------

# Import stuff
import pandas as pd
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from better_profanity import profanity

# --------------------------------------------- Create Helper Functions ------------------------------------------------

# Define Vader functions to get sentiment
sent_obj = SentimentIntensityAnalyzer()  # initialize


def get_sentiment_dict(sentence):
    sent_dict = sent_obj.polarity_scores(sentence)
    return sent_dict


def get_sentiment(sentence, sentiment):
    sent_dict = sent_obj.polarity_scores(sentence)
    return sent_dict[sentiment]


def comp_word(comp_score):
    if comp_score >= 0.05:
        return "Positive"
    elif comp_score <= -0.05:
        return "Negative"
    else:
        return "Neutral"


# Split sentence into list of sections with potentially different sentiment - e.g. "and" is assumed to be the same
def clause_list(sentence):
    split_sentence = sentence.lower()
    # Replace duplicates of ! and ? and change ?! into ?
    while split_sentence.find("!!") != -1:
        split_sentence = split_sentence.replace("!!", "!")
    while split_sentence.find("??") != -1:
        split_sentence = split_sentence.replace("??", "?")
    while split_sentence.find("!?") != -1:
        split_sentence = split_sentence.replace("!?", "?")
    while split_sentence.find("?!") != -1:
        split_sentence = split_sentence.replace("?!", "?")
    # Initialize clauses list and define possible splits
    clauses = []
    splits = ["however",
              "but",
              "and",
              ".",
              ",",
              ";",
              "?",
              "!",
              "except"]
    # add a space before punctuation, so we can separate easily with split method
    split_sentence = split_sentence.replace(".", " .")
    split_sentence = split_sentence.replace(",", " ,")
    split_sentence = split_sentence.replace(";", " ;")
    split_sentence = split_sentence.replace("?", " ?")
    split_sentence = split_sentence.replace("!", " !")
    # while sentence contains split words, loop until sections are all entered into list separately
    # separate sentence into words and get indexes of anything in the "splits" list
    # we then cut around these indexes, dropping the "split" item, and then reform the sentence into sections
    split_sentence_list = split_sentence.split()
    splits_pos = []
    for idx, word in enumerate(split_sentence_list):
        for split in splits:
            if word.find(split) != -1:
                splits_pos.append(idx)
    if splits_pos:
        list_of_splits = []
        split_start = 0
        while splits_pos:
            split_to_add = split_sentence_list[split_start:splits_pos[0]]
            if split_to_add:
                list_of_splits.append(split_to_add)
            split_start = splits_pos[0] + 1
            splits_pos.pop(0)
        for word_list in list_of_splits:
            section_to_add = " ".join(word_list)
            clauses.append(section_to_add)
    else:
        clauses.append(split_sentence)

    return clauses


# Isolate topics and related sentiment for clauses
def topic_sentiment(sentence, topic):
    # create dictionary to record sentiment for topics
    topic_dict = {"overall_food": 0,
                  "pizza": 0,
                  "sausage": 0,
                  "egg": 0,
                  "environment": 0,
                  "service": 0,
                  "price": 0,
                  "facilities": 0}

    # set list of trigger words for each topic
    topic_triggers = {
        "overall_food": ["food", "grub", "meal"],
        "pizza": ["pizza"],
        "sausage": ["sausage"],
        "egg": ["egg"],
        "environment": ["smell", "building", "dirt", "noise", "noisy", "loud", "filth"],
        "service": ["service", "staff"],
        "price": ["cost", "price", "expensive", "cheap"],
        "facilities": ["toilet", "toilets", "loo ", "loos ", " loo", " loos"]
    }

    # split sentence in clauses and check sentiment of selected topic
    # we must find at least one trigger word for topic to attribute score
    # It is still import to isolate clauses, so that we isolate sentiment.
    fb_clauses = clause_list(sentence.lower())
    topic_list = topic_triggers[topic]
    for clause in fb_clauses:
        if any(word in clause for word in topic_list):
            topic_dict[topic] += get_sentiment(clause, "compound")

    return topic_dict[topic]


# censor plus quotes
def censor_quote(sentence):
    censored_quote = profanity.censor(sentence)
    censored_quote = '"' + censored_quote + '"'
    return censored_quote


# -------------------------------------- Load and Process Feedback as DataFrame ----------------------------------------

# Set df display prefs
pd.set_option('display.max_rows', 500)
pd.set_option('display.max_columns', 500)
pd.set_option('display.width', 1000)

# Import feedback as df
fb_df = pd.read_csv("feedback_in.csv", header=0, encoding='cp1252')

# Get display version of feedback that censors swears etc
fb_df["Display_fb"] = fb_df["Feedback"].apply(lambda x: censor_quote(x))

# Get overall sentiment for df
fb_df["Overall_fb_pos"] = fb_df["Feedback"].apply(lambda x: get_sentiment(x, "pos"))
fb_df["Overall_fb_neu"] = fb_df["Feedback"].apply(lambda x: get_sentiment(x, "neu"))
fb_df["Overall_fb_neg"] = fb_df["Feedback"].apply(lambda x: get_sentiment(x, "neg"))
fb_df["Overall_fb_comp"] = fb_df["Feedback"].apply(lambda x: get_sentiment(x, "compound"))
fb_df["Overall_fb"] = fb_df["Overall_fb_comp"].apply(lambda x: comp_word(x))

# Add sentiment columns for set topics
# Overall food
fb_df["General_food_comp"] = fb_df["Feedback"].apply(lambda x: topic_sentiment(x, "overall_food"))
fb_df["General_food_fb"] = fb_df["General_food_comp"].apply(lambda x: comp_word(x))
# Pizza
fb_df["Pizza_comp"] = fb_df["Feedback"].apply(lambda x: topic_sentiment(x, "pizza"))
fb_df["Pizza_fb"] = fb_df["Pizza_comp"].apply(lambda x: comp_word(x))
# Sausage
fb_df["Sausage_comp"] = fb_df["Feedback"].apply(lambda x: topic_sentiment(x, "sausage"))
fb_df["Sausage_fb"] = fb_df["Sausage_comp"].apply(lambda x: comp_word(x))
# Egg
fb_df["Egg_comp"] = fb_df["Feedback"].apply(lambda x: topic_sentiment(x, "egg"))
fb_df["Egg_fb"] = fb_df["Egg_comp"].apply(lambda x: comp_word(x))
# Environment
fb_df["Environment_comp"] = fb_df["Feedback"].apply(lambda x: topic_sentiment(x, "environment"))
fb_df["Environment_fb"] = fb_df["Environment_comp"].apply(lambda x: comp_word(x))
# Service
fb_df["Service_comp"] = fb_df["Feedback"].apply(lambda x: topic_sentiment(x, "service"))
fb_df["Service_fb"] = fb_df["Service_comp"].apply(lambda x: comp_word(x))
# Price
fb_df["Price_comp"] = fb_df["Feedback"].apply(lambda x: topic_sentiment(x, "price"))
fb_df["Price_fb"] = fb_df["Price_comp"].apply(lambda x: comp_word(x))
# Facilities
fb_df["Facilities_comp"] = fb_df["Feedback"].apply(lambda x: topic_sentiment(x, "facilities"))
fb_df["Facilities_fb"] = fb_df["Facilities_comp"].apply(lambda x: comp_word(x))

# Output df
fb_df.to_csv("feedback_with_sentiment.csv", index=False)
