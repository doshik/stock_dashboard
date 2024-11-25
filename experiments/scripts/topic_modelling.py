import pandas as pd
import numpy as np
import nltk
from nltk.corpus import stopwords
import ast

#Remove stop words
from nltk.tokenize import word_tokenize
from nltk.tokenize import RegexpTokenizer

# Only need to run once

# nltk.download('stopwords')
# nltk.download('punkt_tab')

# Load the dataset. This is where you modify to large dataset
df = pd.read_csv("../data/10k_sections_small.csv").drop("Unnamed: 0", axis=1)  #TODO

# Pre-processing
tokenizer = RegexpTokenizer(r'\w+')

stop_words = set(stopwords.words('english'))

def remove_stopwords(sentence):
    tokens = tokenizer.tokenize(sentence)
    filtered = [w.lower() for w in tokens if w.lower() not in stop_words and not w.isnumeric()]
    return ' '.join(filtered)


df['text'] = df['text'].map(remove_stopwords)

print("Done preprocessing...")

# Get tfidf values for each word
from sklearn.feature_extraction.text import TfidfVectorizer
docs = df['text'].to_list()
tfidf = TfidfVectorizer()
 
# get tf-df values
result = tfidf.fit_transform(docs)

print("Done tfidf.....")

# Get total sum of score and average of score
# Also, multiply by tf-idf score to weigh them correctly
score_sum = {}
score_count = {}
for i, row in df.iterrows():
    words = row['text'].split(' ')
    returns = ast.literal_eval(row['returns'])
    for w in words:
        if w not in tfidf.vocabulary_:
            continue
        
        if w in score_sum:
            score_sum[w] += (returns['30d']['ret']/returns['30d']['closePriceStartDate']) * result[i, tfidf.vocabulary_[w]]
            score_count[w] += 1
        else:
            score_sum[w] = (returns['30d']['ret']/returns['30d']['closePriceStartDate']) * result[i, tfidf.vocabulary_[w]]
            score_count[w] = 1

# Divide all scores by their count to get final score
final_score = {}
for w in score_sum.keys():
    final_score[w] = score_sum[w]/score_count[w]

print("Got scores for each word....")

## Topic modelling
# Load the original dataset again
df = pd.read_csv("../data/10k_sections_small.csv").drop("Unnamed: 0", axis=1) #TODO
tokenizer = RegexpTokenizer(r'\w+')

stop_words = set(stopwords.words('english'))

def remove_stopwords(sentence):
    tokens = tokenizer.tokenize(sentence)
    filtered = [w.lower() for w in tokens if w.lower() not in stop_words and not w.isnumeric()]
    return ' '.join(filtered)


df['text'] = df['text'].map(remove_stopwords)

# Run the topic modelling
from bertopic import BERTopic

topic_model = BERTopic()
docs = df['text']
topics, probs = topic_model.fit_transform(docs)

df['topics'] = topics

print("Done with topic modelling....")

# Assign score to each topic
topic_info = topic_model.get_topic_info()
topic_info = topic_info.drop(["Representation", "Representative_Docs"], axis=1)
topic_info["Stock_return_score"] = 0.0


for i, row in topic_info.iterrows():
    topic_words = topic_model.get_topic(row['Topic'])
    topic_score = 0.0
    for w, p in topic_model.get_topic(row['Topic']):
        if w not in final_score:
            continue
        topic_score += p * final_score[w]
    topic_info.loc[i, "Stock_return_score"] = topic_score

print("Assigned score for each topic...")

## Getting top 5 and bottom 5 topics for each 10k filing
final_df = df[["docID", "text", "topics"]]
final_df = final_df[final_df.topics != -1]
final_df = final_df.drop('text', axis=1).groupby('docID').aggregate(set)

def get_extreme_topics(row):
    topic_df = topic_info.loc[topic_info.Topic.isin(row['topics']), ["Topic", "Stock_return_score"]]
    topic_df = topic_df.sort_values('Stock_return_score')
    row['top5'] = topic_df['Topic'][-5:].to_list()
    row['bottom5'] = topic_df['Topic'][:5].to_list()
    return row

final_df = final_df.apply(get_extreme_topics, axis=1).drop('topics', axis=1)

print("Filtered top 5 and bottom 5 topics...")

print("Saving files....")

## Writing results
final_df.to_csv('topic_assignments_per_10k_filing.csv', index=False)
topic_info.to_csv("topic_info.csv", index=False)

print("Saved files.")
print("Done!")