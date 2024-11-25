# Description
The Stock Dashboard is an analytical tool designed to explore relationships between corporate financial reports (10K filings) and stock price movements. The project focuses on two key analytical objectives:

1. Analyzing correlations between company 10K filings and subsequent stock price changes across multiple timeframes (1 day, 5 days, and 30 days post-release)
2. Categorizing 10K filings based on textual content to identify which categories correlate with stock price fluctuations

The project is available as an interactive web application that allows users to explore these insights across different companies.

Hosted Version: https://stock-dashboard-f4sijbkfv-doshiks-projects.vercel.app/

# Installation
There are two ways to access the dashboard:

1. Web Access
   - Visit the hosted version directly through the URL above

2. Local Development Setup
   ```bash
   npm install
   npm run dev
After installation, access the dashboard at http://localhost:3000
# Execution
The project's analytical components can be run through several steps:

* Install dependencies
```pip install -r requirements.txt```

* Data Processing Pipeline :
   * Run the script `/scripts/pull_data_and_extract_sentiments.py`
   * Execute the notebook experiments/notebooks/dva_sentiment_extraction.ipynb.
   * These steps generate the necessary preprocessed CSV files

* Correlation Analysis: Run experiments/notebooks/dva_sentiment_extraction_and_correlation.ipynb
* Topic Modeling: Execute experiments/scripts/topic_modelling.py (GPU recommended)
   * Extract topics from the filings
   * Compute TPR (Topic-Price Relationship) scores for each topic
