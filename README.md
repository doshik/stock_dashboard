## Getting Started

You can run this locally or go to the hosted site. 

Hostedt site: https://stock-dashboard-f4sijbkfv-doshiks-projects.vercel.app/

OR run the development server:

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




