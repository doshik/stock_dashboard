import pandas as pd
import plotly.express as px
import ast
from sklearn.preprocessing import StandardScaler

# Read the CSV files
topic_info_large = pd.read_csv('../data/topic_info_large.csv')  # Replace with actual path
topic_assignments_large = pd.read_csv('../data/topic_assignments_per_10k_filing_large.csv')  # Replace with actual path

# Specify the company name (change as needed)
company_name = "CITIZENS, INC."  # Replace with the company name you want to analyze

# Filter the topic_assignments_large dataset for the company
company_data = topic_assignments_large[topic_assignments_large['name'] == company_name]

# Get the top and bottom topics for this company
top_topics = company_data['top5'].values[0]  # Assuming top5 is stored as a list
bottom_topics = company_data['bottom5'].values[0]  # Assuming bottom5 is stored as a list

# Flatten the list of topics
top_topics = [int(topic) for topic in ast.literal_eval(top_topics)]
bottom_topics = [int(topic) for topic in ast.literal_eval(bottom_topics)]

# Merge top and bottom topics
all_topics = top_topics + bottom_topics

# Retrieve stock return scores for the topics from topic_info_large
topic_scores = topic_info_large[topic_info_large['Topic'].isin(all_topics)]

# Prepare data for visualization
visual_data = []

# Add all topics (both top and bottom)
for topic in all_topics:
    topic_data = topic_scores[topic_scores['Topic'] == topic].iloc[0]
    sentiment = 'Positive' if topic_data['Stock_return_score'] > 0 else 'Negative'
    visual_data.append({
        'Topic': topic_data['Name'],
        'Topic_Price_Relevance_score': topic_data['Stock_return_score'],
        'Sentiment': sentiment
    })

# Create a DataFrame for visualization
visual_df = pd.DataFrame(visual_data)

# Apply separate scaling for positive and negative values
visual_df['Adjusted_Topic_Price_Relevance_score'] = visual_df['Topic_Price_Relevance_score'].apply(
    lambda x: x * 10 if x < 0 else x * 0.1  # Scale negatives up, positives down
)

# Add a column for color based on the sentiment
visual_df['Color'] = visual_df['Topic_Price_Relevance_score'].apply(lambda x: 'green' if x > 0 else 'red')

# Create a horizontal bar chart using Plotly
fig = px.bar(visual_df,
             x='Adjusted_Topic_Price_Relevance_score',
             y='Topic',
             color='Color',
             color_discrete_map={'green': 'green', 'red': 'red'},
             title=f"Best and Worst Topics for {company_name} with Topic Price Relevance Scores",
             labels={'Adjusted_Topic_Price_Relevance_score': 'Adjusted Topic Price Relevance Score', 'Topic': 'Topic Name'},
             orientation='h')

# Increase the font size for topic labels (y-axis) and other text elements
fig.update_layout(
    yaxis=dict(
        tickfont=dict(size=14)  # Adjust the font size of the topic names
    ),
    title=dict(
        font=dict(size=20)  # Adjust the font size of the title
    ),
    xaxis=dict(
        title_font=dict(size=14),  # Adjust the font size for x-axis title
        tickfont=dict(size=12)  # Adjust the font size for x-axis ticks
    ),
    coloraxis_colorbar=dict(
        title_font=dict(size=14),  # Adjust the font size for color legend title
        tickfont=dict(size=12)  # Adjust the font size for color legend ticks
    ),
    legend=dict(
        title="Price Influence",
        tracegroupgap=10,  # Adjusts the gap between legend groups
        itemsizing='constant',  # Ensures consistent sizing of legend items
        font=dict(size=14),  # Font size of the legend texts
        itemclick='toggleothers',  # Allows clicking to toggle legend items
        itemdoubleclick='toggle'  # Allows double-clicking to hide/show items
    )
)

# Update the legend text
fig.for_each_trace(lambda t: t.update(name='Positive Influence on Price') if t.name == 'green' else t.update(name='Negative Influence on Price'))

# Show the plot
fig.show()



