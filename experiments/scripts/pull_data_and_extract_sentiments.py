
from transformers import pipeline
from datasets import load_dataset
import pandas as pd
import ast
from tqdm import tqdm

tqdm.pandas()



ds = load_dataset("JanosAudran/financial-reports-sec", "large_full", trust_remote_code=True, num_proc=35)

ds = ds["train"]


unique_companies = ds.unique("name")[:50]
print(f"Filtering to companies : {unique_companies}")

ds = ds.filter(lambda example: example["name"] in unique_companies)


batch_size = 64

print(f"Loading sentiment model")
sentiment_pipeline = pipeline("text-classification", model="ProsusAI/finbert", device=0, truncation=True, batch_size=batch_size)


def extract_sentiment_batch(batch):
    results = sentiment_pipeline(batch["sentence"])
    batch["sentiment"] = [res["label"] for res in results]
    return batch

ds = ds.map(extract_sentiment_batch, batched=True, batch_size=batch_size)




df = ds.to_pandas()
COLS = ["sentenceID", "sentence", "docID", "filingDate", "section", "name", "labels", "tickers", "reportDate", "returns", "sentiment"]
df = df[COLS]
print(f"Size of df : {len(df)}")

# convert the dict val inside the labels col to 3 separate cols for 1d, 5d and 30d window. 
def parse_labels(label):
    if isinstance(label, str):  # Check if the entry is a string
        try:
            return json.loads(label.replace("'", '"'))  # Convert single quotes to double quotes for JSON
        except json.JSONDecodeError as e:
            print(f"Error parsing label: {label} -> {e}")
            return {}  # Return an empty dict if parsing fails
    return label 


labels_df = df['labels'].progress_apply(parse_labels).progress_apply(pd.Series)
labels_df.columns = [f"label_{col}" for col in labels_df.columns]
df = pd.concat([df, labels_df], axis=1).drop(columns=['labels'])



df.to_csv("10k_sentences_large100_sentiments.csv")