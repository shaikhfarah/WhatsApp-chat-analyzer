import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import io
import emoji
from collections import Counter
from chatline import Chatline
from font_color import Color
from textblob import TextBlob
import os

st.set_page_config(page_title="📱 WhatsApp Chat Analyzer", layout="wide")
st.title("📊 WhatsApp Chat Analyzer")

uploaded_file = st.file_uploader("Upload your WhatsApp chat .txt file", type=["txt"])

stop_words_options = [
    "arabic", "bulgarian", "catalan", "czech", "danish", "dutch", "english", "finnish",
    "french", "german", "hebrew", "hindi", "hinglish","hungarian", "indonesian", "italian", "malaysian",
    "norwegian", "polish", "portuguese", "romanian", "russian", "slovak", "spanish", "swedish",
    "turkish", "ukrainian", "vietnamese"
]

stopword_lang = st.selectbox("Select stopword language", stop_words_options, index=6)

if uploaded_file is not None:
    data = uploaded_file.read().decode("utf-8")
    lines = data.splitlines()

    # Load stop words from stop-words folder
    stop_words = []
    stop_words_file = f"stop-words/{stopword_lang}.txt"
    if os.path.exists(stop_words_file):
        with open(stop_words_file, "r", encoding="utf-8") as f:
            stop_words = [line.strip() for line in f if line.strip()]
    else:
        st.warning(f"⚠️ Stopword file '{stopword_lang}.txt' not found in 'stop-words/' folder. Proceeding without stopwords.")

    # Initialize chat counter
    chat_counter = {
        'chat_count': 0,
        'deleted_chat_count': 0,
        'event_count': 0,
        'senders': [],
        'timestamps': [],
        'words': [],
        'domains': [],
        'emojis': [],
        'fav_emoji': [],
        'fav_word': [],
        'sentiments': [],
        'message_lengths': [],
        'timestamp_deltas': []
    }

    previous_line = None
    previous_timestamp = None
    for line in lines:
        chatline = Chatline(line=line, previous_line=previous_line)
        previous_line = chatline

        if chatline.line_type == 'Chat':
            chat_counter['chat_count'] += 1
            chat_counter['message_lengths'].append(len(" ".join(chatline.words)))
            chat_counter['sentiments'].append(TextBlob(" ".join(chatline.words)).sentiment.polarity)

        if chatline.line_type == 'Event':
            chat_counter['event_count'] += 1

        if chatline.is_deleted_chat:
            chat_counter['deleted_chat_count'] += 1

        if chatline.sender is not None:
            chat_counter['senders'].append(chatline.sender)
            for i in chatline.emojis:
                chat_counter['fav_emoji'].append((chatline.sender, i))
            for i in chatline.words:
                chat_counter['fav_word'].append((chatline.sender, i))

        if chatline.timestamp:
            chat_counter['timestamps'].append(chatline.timestamp)
            if previous_timestamp:
                chat_counter['timestamp_deltas'].append((chatline.timestamp - previous_timestamp).total_seconds())
            previous_timestamp = chatline.timestamp

        chat_counter['words'].extend(chatline.words)
        chat_counter['emojis'].extend(chatline.emojis)
        chat_counter['domains'].extend(chatline.domains)

    # Reduction functions
    def reduce_and_sort(data):
        return sorted(dict(Counter(data)).items(), key=lambda x: x[1], reverse=True)

    def reduce_and_filter_words(words):
        return [w.lower() for w in words if len(w) > 1 and w.isalnum() and not w.isnumeric() and w.lower() not in stop_words]

    def reduce_fav_item(data):
        exist = []
        arr = []
        for i in data:
            if i[1] > 0 and not i[0][0] in exist:
                exist.append(i[0][0])
                arr.append(i)
        return arr

    filtered_words = reduce_and_filter_words(chat_counter['words'])

    chat_counter['senders'] = reduce_and_sort(chat_counter['senders'])
    chat_counter['words'] = reduce_and_sort(filtered_words)
    chat_counter['domains'] = reduce_and_sort(chat_counter['domains'])
    chat_counter['emojis'] = reduce_and_sort(chat_counter['emojis'])
    chat_counter['timestamps'] = reduce_and_sort([(x.strftime('%A'), x.strftime('%H')) for x in chat_counter['timestamps']])
    chat_counter['fav_emoji'] = reduce_fav_item(reduce_and_sort(chat_counter['fav_emoji']))
    chat_counter['fav_word'] = reduce_fav_item(reduce_and_sort([x for x in chat_counter['fav_word'] if len(x[1]) > 1 and x[1].isalnum() and x[1].lower() not in stop_words]))

    # Display results
    st.header("📈 Basic Statistics")
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total Messages", chat_counter['chat_count'])
    col2.metric("Deleted Messages", chat_counter['deleted_chat_count'])
    col3.metric("Events", chat_counter['event_count'])
    col4.metric("Unique Senders", len(chat_counter['senders']))

    st.header("🗣️ Top Senders")
    sender_df = pd.DataFrame(chat_counter['senders'], columns=["Sender", "Message Count"])
    st.dataframe(sender_df.head(10))

    st.header("🌐 Shared Domains")
    domain_df = pd.DataFrame(chat_counter['domains'], columns=["Domain", "Count"])
    st.dataframe(domain_df.head(10))

    st.header("😂 Most Used Emojis")
    emoji_df = pd.DataFrame(chat_counter['emojis'], columns=["Emoji", "Count"])
    st.dataframe(emoji_df.head(10))

    st.header("📖 Most Used Words")
    word_df = pd.DataFrame(chat_counter['words'], columns=["Word", "Count"])
    st.dataframe(word_df.head(10))

    st.header("🔥 Favorite Emojis by Sender")
    fav_emoji_df = pd.DataFrame(chat_counter['fav_emoji'], columns=["(Sender, Emoji)", "Count"])
    st.dataframe(fav_emoji_df.head(10))

    st.header("📝 Favorite Words by Sender")
    fav_word_df = pd.DataFrame(chat_counter['fav_word'], columns=["(Sender, Word)", "Count"])
    st.dataframe(fav_word_df.head(10))

    st.header("📅 Chat Activity Heatmap (Weekday x Hour)")
    heat_df = pd.DataFrame(chat_counter['timestamps'], columns=["Weekday-Hour", "Count"])
    heat_df[['Weekday', 'Hour']] = pd.DataFrame(heat_df['Weekday-Hour'].tolist(), index=heat_df.index)
    pivot_table = heat_df.pivot_table(index='Hour', columns='Weekday', values='Count', aggfunc='sum', fill_value=0)
    fig, ax = plt.subplots(figsize=(10, 5))
    sns.heatmap(pivot_table, cmap="YlGnBu", ax=ax)
    st.pyplot(fig)

    st.header("⏳ Sentiment Analysis Distribution")
    sentiment_df = pd.DataFrame(chat_counter['sentiments'], columns=['Sentiment'])
    fig, ax = plt.subplots()
    sns.histplot(sentiment_df, x='Sentiment', bins=20, kde=True, ax=ax)
    st.pyplot(fig)

    st.header("📆 Most Active Days")
    day_counts = heat_df['Weekday'].value_counts().reindex(['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'])
    st.bar_chart(day_counts)

    st.header("⏰ Most Active Hours")
    hour_counts = heat_df['Hour'].value_counts().sort_index()
    st.line_chart(hour_counts)

    st.header("📉 Chat Gaps and Message Streaks")
    if chat_counter['timestamp_deltas']:
        gap_df = pd.Series(chat_counter['timestamp_deltas']) / 3600  # convert to hours
        st.subheader("⏲️ Time Gaps Between Messages (Hours)")
        fig, ax = plt.subplots()
        sns.histplot(gap_df, bins=50, kde=True, ax=ax)
        st.pyplot(fig)
        st.metric("Longest Gap (hrs)", round(gap_df.max(), 2))
        st.metric("Shortest Gap (secs)", round(gap_df.min() * 3600, 2))
        st.metric("Average Gap (mins)", round(gap_df.mean() * 60, 2))
else:
    st.info("📄 Please upload a WhatsApp chat text file to start analysis.")
