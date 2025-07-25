import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import plotly.express as px
from wordcloud import WordCloud

from visuals.category_colors import color_for_value, categorize_sentiment, sentiment_color, generate_wordcloud, ai_content
    
def capterra(capterra_data, capterra_keywords):

    data = capterra_data
    keywords = capterra_keywords

    data['sentiment_category'] = data['sentiment_score'].apply(categorize_sentiment)
    data['writtenOn'] = pd.to_datetime(data['writtenOn'], utc=True)  
    data['date'] = data['writtenOn'].dt.date

    col1, col2, col3 = st.columns(3, gap='large')
    col1.markdown("<br>__Filters__", unsafe_allow_html=True)
    placeholder = col3.empty()

    col1, col2, col3 = st.columns(3, gap='large')
    st.markdown("<br>", unsafe_allow_html=True)    
    
    with col1:
        min_score, max_score = st.slider(
                    'Select a range for the sentiment score:',
                    min_value=-1.0, max_value=1.0, value=(-1.0, 1.0),
                    key="sentiment_slider_capterra"
               )
    
    with col2:
        industry_choices = ['All'] + data['reviewer_industry'].unique().tolist() 
        industry_filter = st.selectbox('Filter by industry:', industry_choices)

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
    if industry_filter == 'All':
        filtered_data = data[(data['sentiment_score'] >= min_score) & (data['sentiment_score'] <= max_score)]
    else:
        filtered_data = data[(data['sentiment_score'] >= min_score) & (data['sentiment_score'] <= max_score) & (data['reviewer_industry'] == industry_filter)]

    unique_sentiment_scores = filtered_data['sentiment_score'].unique()
    keywords_filtered = keywords[keywords['sentiment_score'].isin(unique_sentiment_scores)]
    
    values_to_exclude = ['Keboola', 'keboola']
    keywords_filtered = keywords_filtered[~keywords_filtered['KEYWORD'].isin(values_to_exclude)]

    col1, col2, col3 = st.columns([3,2,3], gap='medium')
    with col1:
        filtered_data['color'] = filtered_data['sentiment_score'].apply(color_for_value)

        fig = px.histogram(
            filtered_data,
            x='sentiment_score',
            nbins=21,
            title='Sentiment Score Distribution',
            color='color',
            color_discrete_map="identity"
        )

        fig.update_layout(bargap=0.1, xaxis_title='Sentiment Score', yaxis_title='Count') 
        st.plotly_chart(fig, use_container_width=True)

    with col2: 
        keyword_counts = keywords_filtered.groupby('KEYWORD')['KEYWORD_COUNT'].sum().reset_index()
        top_keywords = keyword_counts.sort_values(by='KEYWORD_COUNT', ascending=True).tail(10)
    
        # Create a horizontal bar chart using Plotly
        fig = px.bar(top_keywords, x='KEYWORD_COUNT', y='KEYWORD', orientation='h', title='Top 10 Keywords by Count', color_discrete_sequence=['#FFCC02'])
        fig.update_layout(xaxis_title='Count', yaxis_title='Keyword')

        st.plotly_chart(fig, use_container_width=True)

    with col3:
        # Count the number of reviews for each industry
        industry_counts = filtered_data['reviewer_industry'].value_counts().reset_index()
        industry_counts.columns = ['reviewer_industry', 'count']
        top_10_industries = industry_counts.head(10)
        colors = ['#3CA0FF', '#071729', '#1C3661', '#FDCA00', '#DDDDDD']
        fig = px.pie(
            top_10_industries, 
            names='reviewer_industry', 
            values='count', 
            title=f'Distribution of Reviews Across Industries',
            color_discrete_sequence=colors
    )   
        st.plotly_chart(fig, use_container_width=True)
    st.markdown("<br>", unsafe_allow_html=True)
    
    
    
    col1, col2 = st.columns([3,2])
    # Show table
    col1.markdown("__Data__")
    sorted_data = filtered_data.sort_values(by='date', ascending=False)
    col1.dataframe(sorted_data[['sentiment_category',
                                'prosText',
                                'consText',
                                'generalComments',
                                'reviewer_industry',
                                'date'
                                ]].style.applymap(
            sentiment_color, subset=["sentiment_category"]
        ), 
                column_config={'reviewer_industry': 'Industry',
                                'sentiment_category': 'Sentiment Category',
                                'date': 'Date',
                                'prosText': 'Pros',
                                'consText': 'Cons',
                                'body': 'Text'
                                }, height=500,
                use_container_width=True, hide_index=True)

    summary = keywords_filtered.groupby('KEYWORD')['KEYWORD_COUNT'].sum().reset_index()
    word_freq = dict(zip(summary['KEYWORD'], summary['KEYWORD_COUNT']))
    
    # Wordcloud
    with col2:
        st.markdown("__Word Cloud__")
    
        wordcloud = generate_wordcloud(word_freq)
        plt.figure(figsize=(10, 5), frameon=False)
        plt.imshow(wordcloud, interpolation='bilinear')
        plt.axis('off')
        st.pyplot(plt, use_container_width=True)
    
    content = filtered_data['aggregatedText']

    if placeholder.button("AI Content Strategy Ideas 🧠", use_container_width=True, key='capterra'):
        ai_content(content)
