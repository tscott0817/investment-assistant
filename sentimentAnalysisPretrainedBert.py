# Import required libraries
import re
import praw
import matplotlib.pyplot as plt
from transformers import DistilBertTokenizer, TFDistilBertForSequenceClassification
import tensorflow as tf

# Reddit API keys and access tokens
client_id = 'YVirXu_Irg88reCzbFUubQ'
client_secret = 'a5yIOot8qGHtZQAYhbCIVYrrJJPuyA'
user_agent = 'ml3'
username = 'Dazzling-Resident988'
password = 'Nikhil009'


# Function to set up Reddit API
def create_api():
    reddit = praw.Reddit(
        client_id=client_id,
        client_secret=client_secret,
        user_agent=user_agent,
        username=username,
        password=password
    )
    return reddit


# Function to clean post titles
def clean_title(title):
    # Remove mentions, URLs, and non-alphanumeric characters
    return ' '.join(re.sub("(@[A-Za-z0-9]+)|([^0-9A-Za-z \t])|(\w+:\/\/\S+)", " ", title).split())


# Function to fetch post titles using Reddit API
def get_titles(api, query, count=10000):
    subreddit = api.subreddit(query)
    titles = []

    for post in subreddit.new(limit=count):
        parsed_title = {'title': clean_title(post.title)}
        titles.append(parsed_title)

    return titles


# Function to load the pre-trained DistilBert model and tokenizer
def load_model():
    model = TFDistilBertForSequenceClassification.from_pretrained('distilbert-base-uncased-finetuned-sst-2-english')
    tokenizer = DistilBertTokenizer.from_pretrained('distilbert-base-uncased-finetuned-sst-2-english')
    return model, tokenizer


# Function to perform sentiment analysis
def sentiment_analysis(query):
    api = create_api()
    titles = get_titles(api, query)
    model, tokenizer = load_model()

    # Check if titles list is empty
    if not titles:
        print(f"No titles found for subreddit: {query}")
        return

    title_sentiments = {'positive': 0, 'negative': 0, 'neutral': 0}
    neutral_threshold = 0.05

    # Classify title sentiment using the model
    for title in titles:
        inputs = tokenizer.encode_plus(title['title'], return_tensors='tf', padding=True, truncation=True)
        outputs = model(inputs)
        logits = outputs.logits.numpy()
        probs = tf.nn.softmax(logits, axis=1).numpy()[0]

        if probs[1] - probs[0] > neutral_threshold:
            title_sentiments['positive'] += 1
        elif probs[0] - probs[1] > neutral_threshold:
            title_sentiments['negative'] += 1
        else:
            title_sentiments['neutral'] += 1

    # Calculate sentiment percentages
    title_sentiments_percentages = {k: v / len(titles) * 100 for k, v in title_sentiments.items()}

    # Print sentiment percentages
    print("Reddit Sentiment Analysis of pre-trained DistilBERT Model for", query)
    for sentiment, percentage in title_sentiments_percentages.items():
        print(f"{sentiment.capitalize()}: {percentage:.2f}%")

    # Create a pie chart to visualize sentiment percentages
    plt.pie(title_sentiments_percentages.values(), labels=title_sentiments_percentages.keys(), autopct='%1.1f%%',
            startangle=90)
    plt.axis('equal')
    plt.title(f"Reddit Sentiment Analysis of pre-trained DistilBERT Model for {query}")
    plt.show()

    print('\nNote: This sentiment analysis might not accurately capture sarcasm or nuanced expressions of sentiment.')

    if title_sentiments['positive'] > title_sentiments['negative'] * 0.5:
        print(f"Based on sentiment analysis, ({query}) is performing well.")
        return 1
    else:
        print(f"Based on sentiment analysis, ({query}) is performing poorly.")
        return 0




