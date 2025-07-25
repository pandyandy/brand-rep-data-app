import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import plotly.express as px

from visuals.category_colors import color_for_value, categorize_sentiment, sentiment_color, generate_wordcloud, ai_content

def g2(g2_data, g2_keywords):

    data = g2_data
    keywords = g2_keywords

    data['sentiment_category'] = data['sentiment_score'].apply(categorize_sentiment)
    data['date_published'] = pd.to_datetime(data['date_published'], utc=True)  
    data['date'] = data['date_published'].dt.date
    _, _, _, _, col5 = st.columns(5)
    #placeholder = col5.empty()
    
    col1, col2, col3 = st.columns(3, gap='large')
    col1.markdown("<br>__Filters__", unsafe_allow_html=True)
    placeholder = col3.empty()
    
    col1, col2, col3 = st.columns(3, gap='large')
    st.markdown("<br>", unsafe_allow_html=True)    
    
    with col1:
        min_score, max_score = st.slider(
                    'Select a range for the sentiment score:',
                    min_value=-1.0, max_value=1.0, value=(-1.0, 1.0),
                    key="sentiment_slider_g2"
               )
    
    with col2:
        industry_choices = ['All'] + data['segment'].unique().tolist() 
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

    unique_sentiment_scores = filtered_data['sentiment_score'].unique()
    keywords_filtered = keywords[keywords['sentiment_score'].isin(unique_sentiment_scores)]

    values_to_exclude = ['keboola', 'Keboola']
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
        
        st.plotly_chart(fig, use_container_width=True)
         
    st.markdown("<br>", unsafe_allow_html=True)
    col1, col2 = st.columns([3,2])
    
    # Show table
    col1.markdown("__Data__")
    sorted_data = filtered_data.sort_values(by='date', ascending=False)
    col1.dataframe(sorted_data[['sentiment_category',
                                'aggregated_data',                            
                                'segment',
                                'industry', 
                                'date',
                                'url']].style.map(
            sentiment_color, subset=["sentiment_category"]
        ), 
                column_config={'score': 'Score',
                                'sentiment_category': 'Sentiment Category',
                                'date': 'Date',
                                'segment': 'Segment',
                                'industry': 'Industry',
                                'aggregated_data': 'Text',
                                'url': st.column_config.LinkColumn('URL')
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

    content = filtered_data['aggregated_data']

    if placeholder.button("AI Content Strategy Ideas 🧠", use_container_width=True, key='g2'):
        ai_content(content)
