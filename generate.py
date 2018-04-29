# -*- coding: utf-8 -*-
import os
import time
import unicodedata
import re
import codecs
import importlib
import sys
from heureka import main_crawl

importlib.reload(sys)


def make_price(price):
    new_price = ''
    if len(price) == 4:
        new_price = price[0]+' '+price[1]+price[2]+price[3]
    if len(price) == 5:
        new_price = price[0]+price[1]+' '+price[2]+price[3]+price[4]
    if len(price) == 6:
        new_price = price[0]+price[1]+price[2]+' '+price[3]+price[4]+price[5]
    new_price = new_price+' Kc'
    return str(new_price)


def make_table():
    categories, names, prices_lowest, prices_second, links, shoppers, images, params = main_crawl()
    tabulka = ''
    template = codecs.open(os.path.join(os.path.dirname(__file__), 'index.html'), 'r', encoding='utf-8', errors='ignore')
    
    for i in range(len(names)):
        diff = int(prices_second[i])-int(prices_lowest[i])
        price_lowest = make_price(prices_lowest[i])
        diff = make_price(str(diff))
        tabulka = tabulka+'<tr><td><img src="'+str(images[i])+'"/></td><td><strong>'+names[i]+':</strong>'+str(params[i])+\
                '</td><td>'+price_lowest+'</td><td>'+diff+'</td><td>'+shoppers[i]+'</td><td>'+categories[i]+'</td><td>'+\
                '<a href="'+links[i]+'">Odkaz</a></td></tr>'

    tabulka = tabulka+'</tbody></table></body>'
    page = template.read()+tabulka
    output = codecs.open(os.path.join(os.path.dirname(__file__), 'rendered.html'), 'w', encoding='utf-8', errors='ignore')
    output.write(page)
    output.close()


make_table()
