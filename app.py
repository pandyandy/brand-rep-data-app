import streamlit as st
import base64
import os 

from visuals.g2 import g2
from visuals.reddit import  reddit
from visuals.capterra import capterra

st.set_page_config(layout='wide')

with open('static/style.css') as f:
    st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

# Logo and Title
path = os.path.dirname(os.path.abspath(__file__))
keboola_logo = path + '/static/logo.png'
logo_html = f'''
<div style="display: flex; align-items: center; justify-content: left; font-size: 45px; font-weight: 600;">
    <img src="data:image/png;base64,{base64.b64encode(open(keboola_logo, "rb").read()).decode()}" style="height: 55px;">
    <span style="margin: 0 20px;">Brand Reputation Management</span>
</div>
'''
st.markdown(f"{logo_html}", unsafe_allow_html=True)

# Caption
st.caption("<br>See how users rate Keboola on various platforms & social media.<br>", unsafe_allow_html=True)

# Data
g2_data = '/data/in/tables/g2_sentiment_final.csv'
g2_keywords = '/data/in/tables/g2_keywords_final.csv'

reddit_data = '/data/in/tables/reddit_sentiment_final.csv'
reddit_keywords = '/data/in/tables/reddit_keywords_final.csv'

capterra_data = '/data/in/tables/capterra_sentiment_final.csv'
capterra_keywords = '/data/in/tables/capterra_keywords_final.csv'


tab1, tab2, tab3 = st.tabs(["G2", "Capterra", "Reddit"])
with tab1:
    g2(g2_data, g2_keywords)

with tab2: 
    capterra(capterra_data, capterra_keywords)

with tab3:
    reddit(reddit_data, reddit_keywords)
