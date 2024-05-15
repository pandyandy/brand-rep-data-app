#colors.py 

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