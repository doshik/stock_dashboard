# Stock Dashboard
A dashboard for insights into the relationship between the sentiment and topics from 10K filings with the price movements of a selected stock. 
Hostedt site: https://stock-dashboard-f4sijbkfv-doshiks-projects.vercel.app/

Our goal for this project is to accomplish two main analytical tasks. First, analyze the relationship between company financial reports (10K filings) and the change in stock price 1 day, 5 days and 30 days after their release. Second, we want to categorize the 10-K filings based on their text content and look at what categories correlate to increase/decrease in stock price. Our interactive web app would illustrate our analysis and allow users to explore insights across companies. 


## Installation

You can run this locally or go to the hosted [site](https://stock-dashboard-f4sijbkfv-doshiks-projects.vercel.app/). 


To run locally in a development server:

```bash
npm install
npm run dev
```

Open [http://localhost:3000](http://localhost:3000) with your browser to see the result.


## Running the Python Experiments. 

#### Installation
Install the required packages from the `requirements.txt`
```
pip install -r requirements.txt
```

#### Data preprocessing and Sentiment Extraction
Run the script `experiments/scripts/pull_data_and_extract_sentiments.py` and notebook `dva_sentiment_extraction.ipynb` to generate the preprocessed csv files. 

#### Correlation Analysis
Run the notebook `dva_sentiment_extraction_and_correlation.ipynb` for correlation analysis. 

#### Topic Modelling and TPR Score computation. 
Run the script `experiments/scripts/topic_modelling.py` (preferably on a GPU machine ) to extract the topics and compute TPR scores for each topics. 




