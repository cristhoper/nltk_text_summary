#!/usr/bin/python3

import bs4 as bs  
import re
import nltk
import csv
from unicodedata import normalize
import os

def make_summary(filepath):
    with open(filepath) as f:
        text = f.read()
        filename = f.name
    filename = os.path.basename(filename)    

    article_text = text
    article_text = article_text.replace("[ edit ]", "")

    article_text = re.sub(r'\[[0-9]*\]', ' ', article_text)  
    article_text = re.sub(r'\s+', ' ', article_text)  

    #full = ['0000000', '0000002', '0000003', '0000008', '0000010', '0000011', '0000012', '0000014', '0000016', 'AAAAAFD', 'AAAAAFE', 'AAAAAFS', 'AAAAAFD', 'AAAAAFD' ]

    article_text = re.sub(
        r"([^n\u0300-\u036f]|n(?!\u0303(?![\u0300-\u036f])))[\u0300-\u036f]+",
        r"\1",
        normalize( "NFD", article_text), 0, re.I)
    
    article_text = normalize( 'NFC', article_text)

    formatted_article_text = re.sub('[^a-zA-Z]', ' ', article_text )  
    formatted_article_text = re.sub(r'\s+', ' ', formatted_article_text)  

    #nltk.download()

    sentence_list = nltk.sent_tokenize(article_text)  
    
    #EN ESTA PARTE ENCUENTRA LA FRECUENCIA DE CADA PALABRA
    stopwords = nltk.corpus.stopwords.words('spanish')
    
    word_frequencies = {}  
    for word in nltk.word_tokenize(formatted_article_text):  
        if word not in stopwords:
            if word not in word_frequencies.keys():
                word_frequencies[word] = 1
            else:
                word_frequencies[word] += 1
    
    word_frequencies_sorted = dict(sorted(word_frequencies.items(), key=lambda item: item[1]))
    with open('../word_frequencies.'+filename+'.csv', 'w') as f:
        writer = csv.writer(f)
        for row in word_frequencies_sorted.items():
            writer.writerow(row)

    maximum_frequncy = max(word_frequencies.values())
    
    for word in word_frequencies.keys():  
        word_frequencies[word] = (word_frequencies[word]/maximum_frequncy)
    
    #CALCULA LAS FRASES QUE MÁS SE REPITEN
    sentence_scores = {}  
    for sent in sentence_list:  
        for word in nltk.word_tokenize(sent.lower()):
            if word in word_frequencies.keys():
                if len(sent.split(' ')) < 30:
                    if sent not in sentence_scores.keys():
                        sentence_scores[sent] = word_frequencies[word]
                    else:
                        sentence_scores[sent] += word_frequencies[word]
    
    #REALIZA EL RESUMEN CON LAS MEJORES FRASES
    import heapq  
    summary_sentences = heapq.nlargest(12, sentence_scores, key=sentence_scores.get)
    
    summary = ' '.join(summary_sentences)  
    return summary  

import sys
if __name__ == '__main__':
    
    if(len(sys.argv)==2):
        filepath = sys.argv[1]
        summary = make_summary(filepath)
        print(summary)