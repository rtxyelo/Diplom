
print('Import libraries...')

# Import libraries
import numpy as np
import pandas as pd

import tensorflow as tf
from tensorflow import keras
from tensorflow.keras.preprocessing.sequence import pad_sequences
from tensorflow.keras.preprocessing.text import Tokenizer
import time

import pickle

import socket

import feedparser
import csv

import string
import re
import nltk
nltk.download('stopwords')
nltk.download('punkt')
from nltk.corpus import stopwords
from nltk import word_tokenize
from string import punctuation
from nltk.stem.snowball import SnowballStemmer 

russian_stopwords = stopwords.words("russian")
russian_stopwords.extend(['…', '«', '»', '...', 'т.д.', 'т', 'д'])
stemmer = SnowballStemmer("russian")
print('Libraries are imported...')


# News parser function
def parser():
    newsurls = {'Lenta.ru': 'https://lenta.ru/rss/'}
    f_all_news = 'C:/Users/seryy/Desktop/model_2/lenta_news.csv'

    def parseRSS( rss_url ): #функция получает линк на рсс ленту, возвращает распаршенную ленту с помощью feedpaeser
        return feedparser.parse( rss_url )  

    def getDescriptions( rss_url ): #функция для получения новости
        descriptions = []
        feed = parseRSS( rss_url )
        for newsitem in feed['items']:
            descriptions.append(newsitem['description'])
        return descriptions

    alldescriptions = []

    # Прогоняем нашии URL и добавляем их в наши пустые списки
    for key,url in newsurls.items():
        alldescriptions.extend( getDescriptions( url ) )

    def write_all_news(all_news_filepath): #функция для записи всех новостей в .csv, возвращает нам этот датасет
        header = ['text'] 
        with open(all_news_filepath, 'w', encoding='utf-8-sig') as csvfile:
            writer = csv.writer(csvfile, delimiter=',')
            writer.writerow(i for i in header) 

            for tex  in zip(alldescriptions):
                writer.writerow((tex))

            df = pd.read_csv(all_news_filepath)
                
        return df

    news_dframe = write_all_news(f_all_news) # Распаршенные новости
    return news_dframe
   
f_all_news = 'C:/Users/seryy/Desktop/model_2/lenta_news.csv'   
news_df = pd.read_csv(f_all_news)

# Text clean function
def clean_text(text, remove_sw=True, remove_stem=True):
    # Text to lower index
    text = text.lower()

    # Remove punkruation and numbers from the text
    remove_punkt_digets = ''
    for char in text:
        if char not in string.punctuation and not char.isdigit():
            remove_punkt_digets += char
        else:
            remove_punkt_digets += ' '

    # Remove multiple spaces from the text
    text = re.sub(r'\s+', ' ', remove_punkt_digets, flags=re.I)

    # Remove stopwords from the text (optional)
    if remove_sw:
        clean_text = ''
        tokens = word_tokenize(text)  # tokenize text string
        for token in tokens:
            if token not in russian_stopwords and token != ' ':
                clean_text = clean_text + ' ' + token
        text = clean_text.strip()
    
    if remove_stem:
      stemmed_tokens = []
      tokens = word_tokenize(text) # tokenize text string
      for token in tokens:
        stemmed_tokens.append(stemmer.stem(token)) 
      text = " ".join(stemmed_tokens)
      text = text.strip()
      
    return text
    
    
# Load the pretrained tokenizer
with open('C:/Users/seryy/Desktop/model_2/tokenizer.pickle', 'rb') as handle:
    tokenizer = pickle.load(handle)
    
    
# Dictionary of labels to predict
labels_dict = {0: 'Бывший СССР', 
              1: 'Из жизни', 
              2: 'Интернет и СМИ', 
              3: 'Культура', 
              4: 'Мир', 
              5: 'Наука и техника', 
              6: 'Россия', 
              7: 'Силовые структуры', 
              8: 'Спорт', 
              9: 'Экономика'}
              
              
# Import pretarined CNN model 
file_path2 = "C:/Users/seryy/Desktop/model_2/model_best_val.h5 "    

# It can be used to reconstruct the model identically.
reconstructed_model = keras.models.load_model(file_path2)

# Predict label function
def prediction(news_article):
    # Clean text
    clean_article = clean_text(news_article)

    # Transform text to pad sequence
    seq = tokenizer.texts_to_sequences([clean_article])
    padded = pad_sequences(seq, maxlen=500, padding='post', truncating='post')

    # Eval predict label
    pred = reconstructed_model.predict(padded)

    # Label name
    predicted_label = labels_dict[np.argmax(pred[0])]

    return predicted_label
    

def classificated_news(dataframe):
    class_news = pd.DataFrame(columns=['text', 'topic'])
    predicted_articles = []
    predicted_labels = []
    for article in dataframe['text']:
        article = str(article)     
        article = article.replace('\u200b','')
        article = article.replace('<br />', '')
        article = article.replace('</i>', '')
        article = article.replace('<i>', '')
        article = article.replace('\xe9', '')
        
        predicted_label = prediction(article)
        
        predicted_articles.append(article)
        predicted_labels.append(predicted_label)

    class_news['text'] = predicted_articles
    class_news['topic'] = predicted_labels
    class_news.dropna(subset=['text'], inplace=True)
    class_news.dropna(axis=0,inplace=True)
    return class_news

classified_news = classificated_news(news_df)

print('Readry to predict...')


def start_server():
    global classified_news
    try:
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)   # socket.AF_INET, socket.SOCK_STREAM
        server.bind(('192.168.0.115', 3930))
        server.listen(3)
        print('Server is working...')
        client_socket, address = server.accept()
        print('Client is connected...')
        watched_news = []
        
        while True:
            client_label = client_socket.recv(2048).decode('cp1251')
            print(client_label)
            
            if client_label == 'update':
                news_df = parser() #все новости
                classified_news = classificated_news(news_df)
                print('News are updated!!!')
            
            if client_label == 'clean':
                watched_news = []

            flag = False
            for art in range(len(classified_news)):
                if (classified_news['topic'][art] == client_label) and (classified_news['text'][art] not in watched_news):
                    #print(classified_news['text'][art])
                    content = classified_news['text'][art].encode('cp1251')
                    client_socket.send(content)
                    flag = True
                    watched_news.append(classified_news['text'][art])
                
                if flag:
                    break
            
            if flag == False and client_label != 'clean' and client_label != 'update':
                content = 'Больше нет новостей из этой темы.'.encode('cp1251')
                client_socket.send(content)
            
            
            #predicted_label = prediction(data)
            #content = predicted_label.encode('cp1251')
            #client_socket.send(content)
            #client_socket.close()
            #client_socket.shutdown(socket.SHUT_RDWR)
            #print('Client is disconnected...')
    
    except KeyboardInterrupt:
        server.close()
        print('Server is shutdown.')
        
if __name__ == '__main__':
    start_server()