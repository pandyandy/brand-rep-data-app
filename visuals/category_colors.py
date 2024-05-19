#colors.py 

import streamlit as st
import matplotlib.colors as mcolors
from wordcloud import WordCloud
import numpy as np
from PIL import Image
import os 
import openai
from openai import OpenAI

def color_for_value(value):
    if value < -0.1:
        return '#1C3661'
    elif -0.1 <= value < 0.2:
        return '#9A9FA5' 
    else:
        return '#3CA0FF' 
    
def categorize_sentiment(score):
    if score < 0:
        return 'Negative'
    elif 0 <= score <= 0.2:
        return 'Neutral'
    else:
        return 'Positive'
    
def sentiment_color(sentiment):
    if sentiment == "Positive":
        return "color: #3CA0FF"
    if sentiment == "Neutral":
        return "color: #9A9FA5"
    else:
        return "color: #1C3661"
    
@st.cache_data
def generate_wordcloud(word_freq):
    colormap = mcolors.ListedColormap(['#3CA0FF', '#BDBDBD', '#000000', '#FFCC02', '#1C3661', '#071729'])    
    
    path = os.path.dirname(os.path.abspath(__file__))
    app_path = os.path.dirname(path)
    mask_path = os.path.join(app_path, 'static', 'keboola_wc.png')
    font_path = os.path.join(app_path, 'static', 'Roboto-Bold.ttf')
    
    font = font_path
    mask_image = np.array(Image.open(mask_path))

    wordcloud = WordCloud(width=500, height=500, background_color=None, 
                          font_path=font, mask=mask_image, mode='RGBA', 
                          colormap=colormap).generate_from_frequencies(word_freq)
    #wordcloud_array = wordcloud.to_array()
    return wordcloud

openai.api_key = st.secrets["OPENAI_API_KEY"]

@st.experimental_dialog("Proposed content strategy", width="large")
def ai_content(content):

    result_string = '\n\n'.join(content.astype(str))
    prompt = f"""
    Come up with some relevant 3-5 content strategy ideas for given reviews:
    {result_string}
    """
    with st.spinner('🤖 Analyzing reviews, please wait...'):
        st.session_state['response'] = generate(prompt)
    if 'response' in st.session_state:
        st.write(st.session_state['response'])

def generate(prompt):
    client = OpenAI()
    completion = client.chat.completions.create(
    model="gpt-4o",
    messages=[
        {"role": "system", "content": 
        """
        You are a social media manager at Keboola. Generate insightful and strategic content ideas. Your task is to come up with a content strategy to help Keboola respond effectively to customer reviews and enhance its reputation.
        """
        },
        {"role": "user", "content": prompt}])
    return completion.choices[0].message.content