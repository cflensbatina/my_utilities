# -*- coding: utf-8 -*-
"""
Created on Sat Feb 20 14:02:57 2021

@author: cflensbatina
"""
# Import packages
import urllib.request, urllib.parse, urllib.error
from bs4 import BeautifulSoup
import ssl
import pandas as pd

# SSL stuff
ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

# Link Function
def click_link(url) :
    html = urllib.request.urlopen(url, context=ctx).read()
    soup = BeautifulSoup(html, 'html.parser')
    return soup

# Z-score functions
def z_scores(x) :
    if x.isalpha() == True :
        x = str(x).upper()
        url = 'https://www.cefconnect.com/fund/'+ x
        z_scores_html = click_link(url).find("table", {"id": "ContentPlaceHolder1_cph_main_cph_main_ucPricing_ZScoreGridView"})
        return [x] + [float(z_scores_html.find_all("td", {"class": "right-align"})[i].get_text()) for i in range(3)]

def z_score_df(tickers) :
    df = pd.DataFrame([z_scores(i) for i in tickers if i.isalpha() == True],
        columns=['Ticker', '3 Mo Z', '6 Mo Z', '1 Yr Z'])
    return df

# Discount functions
def discounts(x) :
    if x.isalpha() == True :
        x = str(x).upper()
        url = 'https://www.cefconnect.com/fund/'+ x
        discounts_html = click_link(url).find("table", {"id": "ContentPlaceHolder1_cph_main_cph_main_SummaryGrid"})
        more_discounts_html = click_link(url).find("table", {"id": "ContentPlaceHolder1_cph_main_cph_main_ucPricing_DiscountGrid"})
        
        discounts = [float(discounts_html.find_all("td", {"class": "right-align"})[i].get_text().strip("$%")) for i in [2,5]]
        more_discounts = [more_discounts_html.find_all("td", {"class": "right-align"})[i].get_text().strip("$%") for i in [2,3]]
        new_items = [None if x == '\xa0' else float(x) for x in more_discounts]

        return [x] + discounts + new_items

def discount_df(tickers) :
    df = pd.DataFrame([discounts(i) for i in tickers if i.isalpha() == True],
        columns=['Ticker', 'Current D', '1 Yr D', '3 Yr D', '5 Yr D'])
    return df

# Combined functions
def z_scores_discounts(tickers) :
    df1 = z_score_df(tickers)
    df2 = discount_df(tickers)
    return pd.concat([df1,df2[df2.columns[1:]]],axis=1)
