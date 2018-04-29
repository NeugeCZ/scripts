# -*- coding: utf-8 -*-
import urllib.request
import re
import codecs
from bs4 import BeautifulSoup


def main_crawl():
    adress_buffer = []
    adress_buffer.append('http://notebooky.heureka.cz')
    
    images = []
    params = []
    prices_lowest = []
    prices_second = []
    names = []
    links = []
    shoppers = []
    categories = []
       
    for adress_root in adress_buffer:
        adress_root2 = adress_root.split('.')
        category = adress_root2[0].split('/')
        categories.append(category[2])
        page = urllib.request.urlopen(adress_root)
        page_soup = BeautifulSoup(page, "html.parser")
        items = page_soup.find_all(title='Poslední stránka')
        page_count = int(items[0].string)
            
        for i in range(page_count):
            print('Page:', i)
            adress = adress_root+'/?f='+str(i)
            names, prices_lowest, prices_second, links, shoppers, categories, images, params = category_crawl(adress,
                            names, prices_lowest, prices_second, links, shoppers, categories, category, images, params)
    
    return categories, names, prices_lowest, prices_second, links, shoppers, images, params


def category_crawl(adress, names, prices_lowest, prices_second, links, shoppers, categories, category, images, params):
    page = urllib.request.urlopen(adress)
    soup = BeautifulSoup(page, "html.parser")
    items = soup.find_all(class_='p')
    
    for item in items:
        image = item.find_all(class_='foto')
        parameter = item.find_all(class_='params')

        price = item.find_all(class_='pricen')
        price_disp = price[0].string[:-3].replace(' ', '')

        if '-' in price_disp:
            price_disp = price_disp.split('-')
            diff_prev = int(price_disp[1])-int(price_disp[0])
            if diff_prev > 2499:
                item_detail = price[0].get('href')
                price_lowest, price_second, first_shopper, second_shopper, more_var = detail_crawl(item_detail)
                diff = int(price_second)-int(price_lowest)
                               
                if diff > 2499 and item.img.get('alt') not in names and first_shopper != second_shopper and \
                        len(more_var) == 0:
                              
                    names.append(item.img.get('alt'))
                    links.append(item.a.get('href'))
                    prices_lowest.append(price_lowest)
                    prices_second.append(price_second)
                    shoppers.append(first_shopper)
                    categories.append(category[2])
                    images.append(image[0].img.get('src'))

                    if len(parameter) != 0:
                        params.append(parameter[0])

                    else:
                        params.append('-')
            
    return names, prices_lowest, prices_second, links, shoppers, categories, images, params     


def detail_crawl(adress):
    page = urllib.request.urlopen(adress)
    soup = BeautifulSoup(page, "html.parser")
    
    try:
        bot = soup.find_all(class_='shopspr bottom')
        items = bot[0].find_all(class_='shoppr')
        first_price = items[0].find_all(class_='pricen')
        second_price = items[1].find_all(class_='pricen')
        more_var = items[0].find_all(class_='morevar')
        first_shopper = items[0].img.get('alt')
        second_shopper = items[1].img.get('alt')
        return first_price[0].string[:-3].replace(' ', ''), second_price[0].string[:-3].replace(' ', ''), first_shopper,\
               second_shopper, more_var
        
    except IndexError:
        return 0, 0, 0, 0, 0
    except AttributeError:
        return 0, 0, 0, 0, 0

    
def discount_crawl(adress, names, prices_lowest, prices_second, links):
    page = urllib.request.urlopen(adress)
    soup = BeautifulSoup(page, "html.parser")
    
    items = soup.find_all(class_='item')
    for item in items:
        price_old = item.p.contents[0].string[:-3].replace(' ', '')
        price_new = item.p.contents[1].string[:-3].replace(' ', '')
        diff_prev = int(price_old)-int(price_new)
        if diff_prev > 2499:
            item_detail = item.a.get('href')
            price_lowest, price_second = detail_crawl(item_detail)
            diff = int(price_second)-int(price_lowest)
            
            if diff > 2499 and item.img.get('alt') not in names:
                names.append(item.img.get('alt'))
                links.append(item.a.get('href'))
                prices_lowest.append(price_lowest)
                prices_second.append(price_second)

    return names, prices_lowest, prices_second, links   
