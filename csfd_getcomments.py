# -*- coding: utf-8 -*-
import re
import codecs
import sys
from random import choice
import urllib.request
from bs4 import BeautifulSoup


def get_pagecount(source_souped):
    pages = source_souped.find_all(class_="paginator text")
    pagination = pages[0].get_text().split()
    page_count = int(pagination[-3])
    return page_count

       
def get_comments(source_souped, source, user):
    comments_raw = []
    page_count = get_pagecount(source_souped)
    
    for i in range(1, page_count+1):
        page_url = source+user+'strana-'+str(i)+'/'
        page_crawled = urllib.request.urlopen(page_url)
        page_souped = BeautifulSoup(page_crawled, "html.parser")
        comments_raw_paged = page_souped.find_all(class_='post')
        comments_raw = comments_raw+comments_raw_paged
    return comments_raw


def convert_comments(comments_raw):
    titles = []
    texts = []
    src = None
    stars = '-'

    for comment in comments_raw:
        title_raw = comment.find_all(class_='title')

        try:
            src = title_raw[0].find_all(class_='rating')[0].get('src')

            if src is not None:
                stars = src[-5]+'*'

        except IndexError:
            stars = 'Nehodnoceno'

        if src is None:
            texts.append(comment.get_text())

        else:
            text = comment.get_text()
            texty = text.split('\n')
            titulek = texty[0]+texty[1]+stars+'\n'+texty[2]+texty[3]+'\n'
            texts.append(titulek)

    return titles, texts


def archive_comments(titles, texts):
    file = open('archiv.txt', 'w', encoding='utf-8')
    for i in range(len(texts)):
        file.write(texts[i])
        file.write('*********************************************\n\n')
    file.close()


def main():
    source = 'https://www.csfd.cz'
    user = '/uzivatel/195357-verbal/komentare/'
    source_crawled = urllib.request.urlopen(source+user)
    source_souped = BeautifulSoup(source_crawled, "html.parser")
    comments_raw = get_comments(source_souped, source, user)
    titles, texts = convert_comments(comments_raw)
    archive_comments(titles, texts)
    text_merged = merge_texts(texts)
    style = analyze_text(text_merged)

    for i in range(20):
        print(generate_sent(style))


def merge_texts(texts):
    text_merged = ''
    for text in texts:
        text_merged = text_merged+text.split('\n')[1]

    return text_merged


def analyze_text(text_merged):
    words = text_merged.split()
    key = {}
    for i, word in enumerate(words):
        try:
            word1, word2, word3 = words[i], words[i+1], words[i+2]

        except IndexError:
            break

        colocation = (word1, word2)

        if colocation not in key:
            key[colocation] = []
        key[colocation].append(word3)
    return key

    
def generate_sent(style):
    sent = []
    endings = ['!', '?', '.']
    starts = [key for key in style.keys() if key[0][0].isupper()]
    start = choice(starts)
    first, second = start
    sent.append(first)
    sent.append(second)

    while True:
        try:
            third = choice(style[start])
        except KeyError:
            break
        sent.append(third)
        if third[-1] in endings:
            break
        else:
            start = (second, third)
            first, second = start
    return ' '.join(sent)


main()      
