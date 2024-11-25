import pandas as pd
import numpy as np
import nltk
from nltk.corpus import stopwords
import ast
import os

from sentence_transformers import SentenceTransformer
from bertopic import BERTopic
from cuml.cluster import HDBSCAN
from cuml.manifold import UMAP

# prep the embeddings
sentence_model = SentenceTransformer("all-MiniLM-L6-v2")




#Remove stop words
from nltk.tokenize import word_tokenize
from nltk.tokenize import RegexpTokenizer

# Only need to run once

nltk.download('stopwords')
nltk.download('punkt_tab')

# DATA_PATH = "../data/10k_sections_small.csv"
DATA_PATH = "../data/10k_sentences_large100_sentiments.csv"

print(f"Loading dataset")

# Load the dataset. This is where you modify to large dataset

df = pd.read_csv(DATA_PATH).drop("Unnamed: 0", axis=1)  #TODO
embedding_file = 'sentence_embeddings.npy'
print(f"Embedding generation")

docs = df['sentence']
if os.path.exists(embedding_file):
    print(f"Embeddings file '{embedding_file}' already exists. Loading embeddings...")
    # Load the existing embeddings
    embeddings = np.load(embedding_file)
else:
    print(f"Embeddings file '{embedding_file}' not found. Calculating embeddings...")
    # Initialize the SBERT model
    model = SentenceTransformer('all-MiniLM-L6-v2')  # Replace with your desired SBERT model

    # Generate embeddings
    embeddings = model.encode(df['sentence'], show_progress=True, batch_size=1024)

    # Save embeddings as a NumPy array
    np.save(embedding_file, embeddings)
    print(f"Embeddings saved as '{embedding_file}'.")



print(f"Starting topic modelling")
# Run the topic modelling
from bertopic import BERTopic

umap_model = UMAP(n_components=5, n_neighbors=15, min_dist=0.0)
hdbscan_model = HDBSCAN(min_samples=10, gen_min_span_tree=True, prediction_data=True)

topic_model = BERTopic(umap_model=umap_model, hdbscan_model=hdbscan_model, verbose=True )

topics, probs = topic_model.fit_transform(docs, embeddings)

df['topics'] = topics

print("Done with topic modelling....")




# Pre-processing
tokenizer = RegexpTokenizer(r'\w+')

stop_words = set(stopwords.words('english'))

def remove_stopwords(sentence):
    tokens = tokenizer.tokenize(sentence)
    filtered = [w.lower() for w in tokens if w.lower() not in stop_words and not w.isnumeric()]
    return ' '.join(filtered)


df['sentence'] = df['sentence'].map(remove_stopwords)

print("Done preprocessing...")

# Get tfidf values for each word
from sklearn.feature_extraction.text import TfidfVectorizer
docs = df['sentence'].to_list()
tfidf = TfidfVectorizer()
 
# get tf-df values
result = tfidf.fit_transform(docs)

print("Done tfidf.....")

# Get total sum of score and average of score
# Also, multiply by tf-idf score to weigh them correctly
score_sum = {}
score_count = {}
for i, row in df.iterrows():
    words = row['sentence'].split(' ')
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
df = pd.read_csv(DATA_PATH).drop("Unnamed: 0", axis=1) #TODO
tokenizer = RegexpTokenizer(r'\w+')

stop_words = set(stopwords.words('english'))

def remove_stopwords(sentence):
    tokens = tokenizer.tokenize(sentence)
    filtered = [w.lower() for w in tokens if w.lower() not in stop_words and not w.isnumeric()]
    return ' '.join(filtered)


df['sentence'] = df['sentence'].map(remove_stopwords)



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
final_df = df[["docID", "sentence", "topics", "name"]]
final_df = final_df[final_df.topics != -1]
final_df = final_df.drop('sentence', axis=1).groupby(['docID', 'name']).aggregate(set)

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
final_df.to_csv('topic_assignments_per_10k_filing_large.csv')
topic_info.to_csv("topic_info_large.csv", index=False)

print("Saved files.")
print("Done!")
