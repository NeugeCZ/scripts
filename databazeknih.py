# -*- coding: utf-8 -*-
import re
import codecs
import urllib.request
from bs4 import BeautifulSoup


user = "katka134-165818"


def main_crawl(user):
    items = []
    dates = []
    ratings = []
    years = []
    authors = []
    publishers = []
    ratings_b = []
    lenghts = []
    genres = []
    names = []
    votes = []
    
    adress_main = "http://www.databazeknih.cz/hodnocene-knihy/"+str(user)
    page_crawled = urllib.request.urlopen(adress_main)
    page_main = BeautifulSoup(page_crawled, 'html.parser')

# Vypocet mnozstvi stran - 40 zaznamu na stranu

    ratings_raw = page_main.find_all(class_='voixes now')
    ratings_count = ratings_raw[0].get_text()
    ratings_count = ratings_count.split()
    ratings_count = int(ratings_count[1])
    page_count = ratings_count/40
    page_count = page_count+1
    
    for i in range(1, int(page_count)+1):
        adress_page = adress_main+"/strana-"+str(i)
        items, dates, ratings = items_crawl(adress_page, items, dates, ratings)
   
    for item in items:
        authors, ratings_b, years, publishers, lenghts, genres, names, votes = stats_crawl(item, authors, ratings_b,
                                                                                           years, publishers, lenghts,
                                                                                           genres, names, votes)
           
      
def items_crawl(adress_page, items, dates, ratings):
    page_raw = urllib.request.urlopen(adress_page)
    page_items = BeautifulSoup(page_raw, 'html.parser')
    items_raw = page_items.find_all(class_='new strong')
    ratings_raw = page_items.find_all(class_='odtop')
    dates_raw = page_items.find_all(class_='fright pozn_lightest timer')
    
    for i in range(len(dates_raw)):
        items.append(items_raw[i].get('href'))
        dates.append(dates_raw[i].get_text())

        try:
            ratings.append(ratings_raw[i].get('src')[-5])

        except TypeError:
            ratings.append('0')
        
    return items, dates, ratings

    
def stats_crawl(item, authors, ratings_b, years, publishers, lenghts, genres, names, votes):
    item_crawled = urllib.request.urlopen(item+'?show=binfo')  # +full info atribut
    page_item = BeautifulSoup(item_crawled, 'html.parser')
    author_raw = page_item.find_all(class_='jmenaautoru')
    votes_raw = page_item.find_all(class_='bpointsm')
    year_alt_raw = page_item.find_all(class_='binfo_hard')
    name_raw = page_item.find_all(itemprop='name')
    rating_raw = page_item.find_all(class_='bpoints')
    year_raw = page_item.find_all(itemprop='datePublished')
    publisher_raw = page_item.find_all(itemprop='publisher')
    pages_raw = page_item.find_all(itemprop='numberOfPages')
    genre_raw = page_item.find_all(itemprop='category')
    
    if len(author_raw) == 0:
        author = '-'
        page_author = '-'

    else: 
        author_text = author_raw[0].get_text()
        author = author_text[4:]
        page_author = author_raw[0].a.get('href')
        
    if len(rating_raw) == 0:
        rating = '-'

    else:
        rating_text = rating_raw[0].get_text()
        rating = rating_text[:-1]
        
    if len(publisher_raw) == 0:
        publisher = '-'
    else:
        publisher = publisher_raw[0].get_text()
        
    if len(pages_raw) == 0:
        pages = '-'

    else:
        pages = pages_raw[0].get_text()
        
    if len(genre_raw) == 0:
        genre = '-'

    else:
        genre = genre_raw[0].get_text()
    
    if len(year_raw) == 0:
        year = '-'

    else:
        year = year_raw[0].get_text()
    
    if len(name_raw) == 0:
        name = '-'

    else:
        name = name_raw[0].get_text()
    
    if len(votes_raw) == 0:
        vote = '-'

    else:
        vote_a = votes_raw[0].get_text()
        vote_b = vote_a.split()
        vote = vote_b[0]
        
    author_more = author.split(',')
        
    for autor in author_more:
        if '(p)' in autor:
            authors.append(pseudonym_crawl(page_author))
        else:
            authors.append(autor)
            
    for rec in year_alt_raw:
        if '1. vyd' in rec.get_text():
            rr = rec.next_sibling
            year = rr.get_text()
    
    for rec in year_alt_raw: 
        if 'zev:' in rec.get_text():
            rr = rec.next_sibling.next_sibling
            a = rr.get_text()
            a = a.split()
            year = a[len(a)-1].strip('()')
                         
    ratings_b.append(rating)
    years.append(year)
    publishers.append(publisher)
    lenghts.append(pages)
    genres.append(genre)
    names.append(name)
    votes.append(vote)
         
    return authors, ratings_b, years, publishers, lenghts, genres, names, votes
    

def pseudonym_crawl(page_author):
    item_crawled = urllib.request.urlopen('http://www.databazeknih.cz/'+page_author)
    page_item = BeautifulSoup(item_crawled, 'html.parser')
    author_raw = page_item.find_all(itemprop='name')
    
    author = author_raw[0].get_text()
    return author

    
main_crawl(user)
