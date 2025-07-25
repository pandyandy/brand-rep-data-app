import streamlit as st
import pandas as pd
import base64
import os 
import openai

from visuals.g2 import g2
from visuals.reddit import  reddit
from visuals.capterra import capterra
from visuals.category_colors import categorize_sentiment
from keboola_streamlit import KeboolaStreamlit

st.set_page_config(layout='wide')

path = os.path.dirname(os.path.abspath(__file__))
with open(path + '/static/style.css') as f:
    st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

# Logo and Title
keboola_logo = path + '/static/logo.png'
logo_html = f'''
<div style="display: flex; align-items: center; justify-content: left; font-size: 45px; font-weight: 600;">
    <img src="data:image/png;base64,{base64.b64encode(open(keboola_logo, "rb").read()).decode()}" style="height: 50px;">
    <span style="margin: 0 20px;">Brand Reputation Management</span>
</div>
'''
st.markdown(f"{logo_html}", unsafe_allow_html=True)

# Caption
st.caption("<br>See how users rate Keboola on various platforms & social media.<br>", unsafe_allow_html=True)


@st.cache_data
def load_data():
    keboola = KeboolaStreamlit(
        st.secrets["kbc_url"],
        st.secrets["kbc_token"],

        
    )
    g2_data = keboola.read_table("out.c-sentiment-cleaning.g2_sentiment_final")
    g2_keywords = keboola.read_table("out.c-keywords-cleaning.g2_keywords_final")
    reddit_data = keboola.read_table("out.c-sentiment-cleaning.reddit_sentiment_final")
    reddit_keywords = keboola.read_table("out.c-keywords-cleaning.reddit_keywords_final")
    capterra_data = keboola.read_table("out.c-sentiment-cleaning.capterra_sentiment_final")
    capterra_keywords = keboola.read_table("out.c-keywords-cleaning.capterra_keywords_final")
    return g2_data, g2_keywords, reddit_data, reddit_keywords, capterra_data, capterra_keywords

g2_data, g2_keywords, reddit_data, reddit_keywords, capterra_data, capterra_keywords = load_data()

tab1, tab2, tab3 = st.tabs(["G2", "Capterra", "Reddit"])
with tab1:
    g2(g2_data, g2_keywords)

with tab2: 
    capterra(capterra_data, capterra_keywords)

with tab3:
    reddit(reddit_data, reddit_keywords)
