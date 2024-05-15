import streamlit as st
import pandas as pd
import os 
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
import plotly.express as px
from wordcloud import WordCloud
import numpy as np
from PIL import Image

from visuals.category_colors import color_for_value, categorize_sentiment, sentiment_color

def g2(g2_data, g2_keywords):

    data = pd.read_csv(g2_data)
    keywords = pd.read_csv(g2_keywords)

    data['sentiment_category'] = data['sentiment_score'].apply(categorize_sentiment)
    data['date_published'] = pd.to_datetime(data['date_published'], utc=True)  
    data['date'] = data['date_published'].dt.date

    st.markdown("<br>__Filters__", unsafe_allow_html=True)
    col1, col2, col3 = st.columns(3, gap='large')
    st.markdown("<br>", unsafe_allow_html=True)    
    
    with col1:
        min_score, max_score = st.slider(
                    'Select a range for the sentiment score:',
                    min_value=-1.0, max_value=1.0, value=(-1.0, 1.0),
                    key="sentiment_slider_g2"
               )
    
    with col2:
        industry_choices = ['All'] + data['segment'].unique().tolist()  # Add 'All' to the list of industries
        selected_industries = st.selectbox('Filter by segment:', industry_choices)

    with col3:
        if not data.empty:
            min_date = data['date'].min()
            max_date = data['date'].max()
            default_date_range = (min_date, max_date)
        else:
            min_date, max_date = None, None
            default_date_range = ()

        # Date range
        date_range = st.date_input("Select a date range:",  default_date_range, min_value=min_date, max_value=max_date)
        if date_range:
            try:
                if len(date_range) == 2:
                    start_date, end_date = date_range
                    data = data[(data['date'] >= start_date) & (data['date'] <= end_date)]
            except Exception as e:
                st.info("Please select both start and end dates.")

    # Apply Filters
    if selected_industries == 'All':
        filtered_data = data[(data['sentiment_score'] >= min_score) & (data['sentiment_score'] <= max_score)]
    else:
        filtered_data = data[(data['sentiment_score'] >= min_score) & (data['sentiment_score'] <= max_score) & (data['segment'] == selected_industries)]

    #keywords_filtered = keywords[(keywords['sentiment_score'] >= min_score) & (keywords['sentiment_score'] <= max_score)]
    unique_sentiment_scores = filtered_data['sentiment_score'].unique()
    keywords_filtered = keywords[keywords['sentiment_score'].isin(unique_sentiment_scores)]

    col1, col2, col3 = st.columns([3,2,3], gap='medium')
    with col1:
    #    colors = {
    #    'Negative': '#1C3661',
    #    'Neutral': '#FFCC02',
    #    'Positive': '#3CA0FF'
    #}
    #    filtered_data['Color'] = filtered_data['sentiment_category'].map(colors)
    #    fig = px.pie(filtered_data, names='sentiment_category', color='sentiment_category', color_discrete_map=colors, title='Sentiment Distribution', hole=0.4)
    #    st.plotly_chart(fig, use_container_width=True)

    ###### HIST 

        filtered_data['color'] = filtered_data['sentiment_score'].apply(color_for_value)

        fig = px.histogram(
            filtered_data,
            x='sentiment_score',
            nbins=20,  # Number of bins can be adjusted depending on the distribution
            title='Sentiment Score Distribution',
            color='color',
            color_discrete_map="identity"  # This tells Plotly to use the DataFrame's color column as is
        )

        fig.update_layout(bargap=0.1, xaxis_title='Sentiment Score', yaxis_title='Count') 
        st.plotly_chart(fig, use_container_width=True)

    with col2: 
        #positive_keywords = keywords_filtered[(keywords_filtered['sentiment_score'] > 0) & (keywords_filtered['KEYWORD'] != 'Keboola')]
        keyword_counts = keywords_filtered.groupby('KEYWORD')['KEYWORD_COUNT'].sum().reset_index()
        # Sort by count in descending order and select top 10 keywords
        top_keywords = keyword_counts.sort_values(by='KEYWORD_COUNT', ascending=True).tail(10)

        # Create a horizontal bar chart using Plotly
        fig = px.bar(top_keywords, x='KEYWORD_COUNT', y='KEYWORD', orientation='h', title='Top 10 Keywords by Count', color_discrete_sequence=['#FFCC02'])
        fig.update_layout(xaxis_title='Count', yaxis_title='Keyword')

        st.plotly_chart(fig, use_container_width=True)

    with col3:

        # Count the number of reviews for each industry
        industry_counts = filtered_data['industry'].value_counts().reset_index()
        industry_counts.columns = ['industry', 'count']
        top_10_industries = industry_counts.head(10)
        count = top_10_industries.shape[0]
        colors = ['#071729', '#FDCA00', '#1C3661', '#DDDDDD', '#3CA0FF']
        # Create a pie chart using Plotly
        fig = px.pie(
            top_10_industries, 
            names='industry', 
            values='count', 
            title=f'Distribution of Reviews Across Industries Top {count}',
            color_discrete_sequence=colors
        )
        
        # Display the figure in Streamlit
        st.plotly_chart(fig, use_container_width=True)
        #negative_keywords = keywords_filtered[keywords_filtered['sentiment_score'] < 0]
        #keyword_counts = negative_keywords.groupby('KEYWORD')['KEYWORD_COUNT'].sum().reset_index()
        # Sort by count in descending order and select top 10 keywords
        #top_keywords = keyword_counts.sort_values(by='KEYWORD_COUNT', ascending=True).tail(10)

        # Create a horizontal bar chart using Plotly
        #fig = px.bar(top_keywords, x='KEYWORD_COUNT', y='KEYWORD', orientation='h', title='Top 10 Negative Keywords by Count', color_discrete_sequence=['#1C3661'])
        #fig.update_layout(xaxis_title='Count', yaxis_title='Keyword')

        #st.plotly_chart(fig, use_container_width=True)

    # Histogram
    #fig = px.histogram(filtered_data, x='sentiment_score', nbins=20, title='Distribution of Sentiment Score')

    #fig.update_layout(
    #   xaxis_title='Sentiment Score',
    #  yaxis_title='Count',
    # bargap=0.1)
    #st.plotly_chart(fig, use_container_width=True)
    st.markdown("<br>", unsafe_allow_html=True)
    col1, col2 = st.columns([3,2])
    # Show table

    col1.markdown("__Data__")
    sorted_data = filtered_data.sort_values(by='date', ascending=False)
    col1.dataframe(sorted_data[['sentiment_category',
                                'aggregated_data',                            
                                #'name',
                                #'sentiment_score',
                                'segment',
                                'industry', 
                                'date',
                                'url']].style.applymap(
            sentiment_color, subset=["sentiment_category"]
        ), 
                column_config={#'name': 'Name', 
                                'score': 'Score',
                                #'sentiment_score': 'Sentiment Score',
                                'sentiment_category': 'Sentiment Category',
                                'date': 'Date',
                                'segment': 'Segment',
                                'industry': 'Industry',
                                'aggregated_data': 'Text',
                                'url': st.column_config.LinkColumn('URL')
                                }, height=500,
                use_container_width=True, hide_index=True)

    # Wordcloud
    with col2:
        st.markdown("__Word Cloud__")
        #word_freq = keywords_filtered.set_index('KEYWORD')['KEYWORD_COUNT'].to_dict()
        keywords_filtered = keywords_filtered[keywords_filtered['KEYWORD'] != 'Keboola']
        summary = keywords_filtered.groupby('KEYWORD')['KEYWORD_COUNT'].sum().reset_index()
        word_freq = dict(zip(summary['KEYWORD'], summary['KEYWORD_COUNT']))

        colormap = mcolors.ListedColormap(['#3CA0FF', '#BDBDBD', '#000000', '#FFCC02', '#1C3661', '#071729'])
        #title_text = 'Keyword Frequency'
        #st.markdown(f'**{title_text}**', unsafe_allow_html=True)

        path = os.path.dirname(os.path.abspath(__file__))
        app_path = os.path.dirname(path)
        mask_path = os.path.join(app_path, 'static', 'keboola_wc.png')
        font_path = os.path.join(app_path, 'static', 'Roboto-Bold.ttf')
        
        mask = np.array(Image.open(mask_path))
        font = font_path

        wordcloud = WordCloud(width=500, height=500, background_color=None, font_path=font, mask=mask, mode='RGBA', colormap=colormap).generate_from_frequencies(word_freq)
        wordcloud_array = wordcloud.to_array()

        plt.figure(figsize=(10, 5), frameon=False)
        plt.imshow(wordcloud_array, interpolation='bilinear')
        plt.axis('off')
        st.pyplot(plt, use_container_width=True)