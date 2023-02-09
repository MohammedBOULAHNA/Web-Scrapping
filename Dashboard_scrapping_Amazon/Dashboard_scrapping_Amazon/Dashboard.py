from bs4 import BeautifulSoup
import requests
import pandas as pd
import numpy as np
import re
import time
import pickle
from urllib.parse import unquote
import dash_table

# text preprocessing
from nltk.tokenize import word_tokenize
from nltk.stem import WordNetLemmatizer
from nltk.corpus import stopwords
from sklearn.feature_extraction.text import TfidfVectorizer
import spacy
from textblob import TextBlob

import plotly.express as px

import dash
import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc
# from dash_extensions.enrich import Output, Input, State, DashProxy, MultiplexerTransform
from dash.dependencies import Input, Output, State

categories = [
    {'label': 'Electronics', 'value': 5},
    {'label': 'Computers', 'value': 6},
    {'label': 'Smart Home', 'value': 7},
    {'label': 'Arts & Crafts', 'value': 8},
    {'label': 'Automotive', 'value': 9},
    {'label': 'Baby', 'value': 10},
    {'label': 'Beauty and personal care', 'value': 11},
    {'label': 'Women\'s Fashion', 'value': 12},
    {'label': 'Men\'s Fashion', 'value': 13},
    {'label': 'Girls\' Fashion', 'value': 14},
    {'label': 'Boys\' Fashion', 'value': 15},
    {'label': 'Health and Household', 'value': 16},
    {'label': 'Home and Kitchen', 'value': 17},
    {'label': 'Industrial and Scientific', 'value': 18},
    {'label': 'Luggage', 'value': 19},
    {'label': 'Movies & Television', 'value': 20},
    {'label': 'Pet supplies', 'value': 21},
    {'label': 'Software', 'value': 22},
    {'label': 'Sports and Outdoors', 'value': 23},
    {'label': 'Tools & Home Improvement', 'value': 24},
    {'label': 'Toys and Games', 'value': 25},
    {'label': 'Video Games', 'value': 26},
]

# global variables

# Initializing the app
FA = "https://use.fontawesome.com/releases/v5.12.1/css/all.css"
external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP, FA])
# app = DashProxy(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP, FA], prevent_initial_callbacks=True,transforms=[MultiplexerTransform()])

server = app.server


def get_sub_categories(category):
    headers = {
        'rtt': '100',
        'Accept': 'text/html, */*; q=0.01',
        'Referer': 'https://www.amazon.com/',
        'X-Requested-With': 'XMLHttpRequest',
        'downlink': '2.45',
        'ect': '4g',
        'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.114 Safari/537.36 OPR/75.0.3969.171',
    }

    params = (
        ('ajaxTemplate', 'hamburgerMainContent'),
        ('pageType', 'Gateway'),
        ('hmDataAjaxHint', '1'),
        ('navDeviceType', 'desktop'),
        ('isSmile', '0'),
        ('isPrime', '0'),
        ('isBackup', 'false'),
        ('hashCustomerAndSessionId', 'a4060175b7dbf7316ac5e6ecaa96186226829879'),
        ('isExportMode', 'true'),
        ('languageCode', 'en_US'),
        ('environmentVFI', 'AmazonNavigationCards/development@B6048321973-AL2_x86_64'),
        ('secondLayerTreeName',
         'prm_digital_music_hawkfire+kindle+android_appstore+electronics_exports+computers_exports+sbd_alexa_smart_home+arts_and_crafts_exports+automotive_exports+baby_exports+beauty_and_personal_care_exports+womens_fashion_exports+mens_fashion_exports+girls_fashion_exports+boys_fashion_exports+health_and_household_exports+home_and_kitchen_exports+industrial_and_scientific_exports+luggage_exports+movies_and_television_exports+pet_supplies_exports+software_exports+sports_and_outdoors_exports+tools_home_improvement_exports+toys_games_exports+video_games_exports+giftcards+amazon_live+Amazon_Global'),
    )

    response = requests.get('https://www.amazon.com/gp/navigation/ajax/generic.html', headers=headers, params=params)
    result = BeautifulSoup(response.content, 'lxml')

    sub_category = result.find('ul', attrs={'data-menu-id': category})
    list_cat = sub_category.findAll('a', href=re.compile("bbn"), attrs={'class': 'hmenu-item'})

    list_dict = dict()
    for a in list_cat:
        list_dict[a.text] = a['href']

    return list_dict


def get_url_params(url):
    url = unquote(url)
    url = url.split('?')[1]
    urlparams = url.split('&')
    urlparams = [item for item in urlparams if item.find('=') != -1]
    params_list = []
    for param in urlparams:
        pair = param.split('=')
        key = pair[0]
        value = pair[1]
        params_list.append((key, value))

    return params_list


def get_third_level_categories(sub_category):
    params = tuple(get_url_params(sub_category))

    headers = {
        'authority': 'www.amazon.com',
        'rtt': '50',
        'downlink': '10',
        'ect': '4g',
        'upgrade-insecure-requests': '1',
        'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.114 Safari/537.36 OPR/75.0.3969.171',
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
        'sec-fetch-site': 'same-origin',
        'sec-fetch-mode': 'navigate',
        'sec-fetch-user': '?1',
        'sec-fetch-dest': 'document',
        'referer': 'https://www.amazon.com/s?i=specialty-aps&bbn=16225009011&rh=n%3A%2116225009011%2Cn%3A281407&ref=nav_em__nav_desktop_sa_intl_accessories_and_supplies_0_2_5_2',
        'accept-language': 'en-US,en;q=0.9',
        'cookie': 'session-id=146-3469082-1944640; i18n-prefs=USD; sp-cdn="L5Z9:MA"; ubid-main=134-1917772-8632935; skin=noskin; lc-main=en_US; session-id-time=2082787201l; aws_lang=en; aws-target-data=%7B%22support%22%3A%221%22%7D; s_fid=0B446F6A019CC362-28D3BF6FE12761FF; aws-ubid-main=123-2450080-4748301; remember-account=false; s_sq=awsamazonallprod1%3D%2526pid%253Dhttps%25253A%25252F%25252Fportal.aws.amazon.com%25252Fbilling%25252Fsignup%252523%25252Fstart%2526oid%253Dfunction%252528e%252529%25257Bif%252528s%252526%252526n.__isDisabled%252528%252529%252529returne.preventDefault%252528%252529%25253Bvart%25253De.button%25252Cr%25253De.ctrlKey%25252Ci%25253De.shiftKey%25252Co%2526oidt%253D2%2526ot%253DSUBMIT; session-id-eu=262-2636458-8636513; ubid-acbuk=258-8875985-4065941; session-token=PKEXVDqM+1WyfHR3tfqCkTz+QJC6GN7B1orN8vufgDm8+8rbfqXiTNBRpxfzNW64mL8w7WzzZ+6BY86n3yCz1EYerHA5icES8oVm1+1KavUkD0pxdZaWrV/t9cvTLYXM7OgsnSx003n8WIK6MSAN7Wlp1wBlhxNM+J8CpEpSgHL3sOc9j52BovinqAStCnnX; csm-hit=P5TAKF65AA7N9HSENFWH+s-HEC0R6NEDQ60VV69K81N|1627912056511',
    }

    response = requests.get('https://www.amazon.com/s', headers=headers, params=params)
    result = BeautifulSoup(response.content, 'lxml')

    departments = result.find(id='departments')

    third_cat = departments.findAll('li', attrs={'class': "s-navigation-indent-2"})

    third_cat_dict = dict()
    for cat in third_cat:
        url = cat.find('a', attrs={'class': "a-link-normal s-navigation-item"})['href']
        text = cat.getText()
        third_cat_dict[text] = url

    return third_cat_dict


# get all products for the third category
def get_products(third_category, category):
    params_list = get_url_params(third_category)
    headers = {
        'authority': 'www.amazon.com',
        'x-amazon-s-swrs-version': 'BCB408307E65E0167951EA7B2AA5F482,D41D8CD98F00B204E9800998ECF8427E',
        'x-amazon-s-fallback-url': 'https://www.amazon.com/s?i=electronics-intl-ship&bbn=16225009011&rh=n%3A281407%2Cn%3A172532&dc&page=2&qid=1628286265&rnid=281407&ref=sr_pg_2',
        'rtt': '50',
        'x-amazon-rush-fingerprints': '',
        'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.114 Safari/537.36 OPR/75.0.3969.171',
        'content-type': 'application/json',
        'accept': 'text/html,*/*',
        'x-amazon-s-mismatch-behavior': 'FALLBACK',
        'x-requested-with': 'XMLHttpRequest',
        'downlink': '10',
        'ect': '4g',
        'origin': 'https://www.amazon.com',
        'sec-fetch-site': 'same-origin',
        'sec-fetch-mode': 'cors',
        'sec-fetch-dest': 'empty',
        'referer': 'https://www.amazon.com/s?i=electronics-intl-ship&bbn=16225009011&rh=n%3A281407%2Cn%3A172532&dc&qid=1628286248&rnid=281407&ref=sr_nr_n_1',
        'accept-language': 'en-US,en;q=0.9',
        'cookie': 'session-id=146-3469082-1944640; i18n-prefs=USD; sp-cdn="L5Z9:MA"; ubid-main=134-1917772-8632935; skin=noskin; lc-main=en_US; session-id-time=2082787201l; aws_lang=en; aws-target-data=%7B%22support%22%3A%221%22%7D; s_fid=0B446F6A019CC362-28D3BF6FE12761FF; aws-ubid-main=123-2450080-4748301; remember-account=false; s_sq=awsamazonallprod1%3D%2526pid%253Dhttps%25253A%25252F%25252Fportal.aws.amazon.com%25252Fbilling%25252Fsignup%252523%25252Fstart%2526oid%253Dfunction%252528e%252529%25257Bif%252528s%252526%252526n.__isDisabled%252528%252529%252529returne.preventDefault%252528%252529%25253Bvart%25253De.button%25252Cr%25253De.ctrlKey%25252Ci%25253De.shiftKey%25252Co%2526oidt%253D2%2526ot%253DSUBMIT; session-id-eu=262-2636458-8636513; ubid-acbuk=258-8875985-4065941; session-token=NOLt3ftC1qbkMITuCkkyYtcs683mDNICPmXPglTJkb5RQ3VdDiv+kKw+7JBcS0U7vmkvGtsSMZb3PrhmXgPOIggoA6eWAkkD0cAnd6NUEC3+xcNZH2y+/6LE0cA4ydUO+J8s8J4HLjbNjU5C6fDf2LUcSzAbUBtQdPvbTipn4yc+KdG1uvbETN+pS9I51l6g; csm-hit=V8X61JV10TTXMCSC3YK8+s-DSHRQ5GGNKFDCKK0C2VY|1628332153881',
    }

    title = []
    img = []
    price = []
    url = []
    rating = []
    ids = []
    product_id = 0
    for page in range(1, 2):
        params_list.append(('page', page))
        params = tuple(params_list)

        response = requests.post('https://www.amazon.com/s/query', headers=headers, params=params)

        result = BeautifulSoup(response.text, 'lxml')
        list_product = result.findAll('div', attrs={'data-component-type': re.compile("s-search-result")})

        if len(list_product) == 0:
            break

        for product in list_product:
            product_id = product_id + 1
            product_title = product.find('span', attrs={'class': re.compile("a-size-base-plus")})
            product_img = product.find('img', attrs={'class': re.compile("s-image")})
            product_price = product.find('span', attrs={'class': re.compile("a-offscreen")})
            product_url = product.find('a', attrs={'class': re.compile("a-link-normal")})
            product_rating = product.find('span', attrs={'class': re.compile("a-icon-alt")})

            if product_url is not None:
                if "picassoRedirect" in product_url['href']:
                    continue
                else:
                    y = product_url['href']
                    y = y.replace('\\"', '')
                    url.append(y)
            else:
                continue

            if product_title is not None:
                title.append(product_title.getText())
            else:
                title.append('')

            if product_img is not None:
                y = product_img['src']
                y = y.replace('\\"', '')
                img.append(y)
            else:
                img.append('')

            if product_price is not None:
                product_price = product_price.string.replace("$", "")
                price.append(product_price)
            else:
                price.append('')

            if product_rating is not None:
                product_rating = re.search('^(.+?)out', product_rating.string).group(1)
                rating.append(product_rating)
            else:
                rating.append('')

            ids.append(product_id)

    products = pd.DataFrame(list(zip(ids, title, img, price, rating, url)),
                            columns=['product_id', 'title', 'img', 'price', 'rating', 'url'])

    products[['price', 'rating']] = products[['price', 'rating']].apply(pd.to_numeric, errors='coerce', axis=1)
    product_count = len(products.index)
    mean_price = round(products["price"].mean(), 2)
    mean_rating = round(products["rating"].mean(), 2)
    return products, category, product_count, mean_price, mean_rating


# scrap reviews for a product
def scrap_reviews(reviews_url):
    # scrap all reviews for product
    headers = {
        'authority': 'www.amazon.com',
        'rtt': '200',
        'accept': 'text/html,*/*',
        'x-requested-with': 'XMLHttpRequest',
        'downlink': '3.3',
        'ect': '4g',
        'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.114 Safari/537.36 OPR/75.0.3969.171',
        'content-type': 'application/x-www-form-urlencoded;charset=UTF-8',
        'origin': 'https://www.amazon.com',
        'sec-fetch-site': 'same-origin',
        'sec-fetch-mode': 'cors',
        'sec-fetch-dest': 'empty',
        'referer': 'https://www.amazon.com/Roku-Streaming-Stick-HDR-Streaming-Long-range/product-reviews/B075XLWML4/ref=cm_cr_dp_d_show_all_btm?ie=UTF8&reviewerType=all_reviews',
        'accept-language': 'en-US,en;q=0.9',
        'cookie': 'session-id=146-3469082-1944640; i18n-prefs=USD; sp-cdn="L5Z9:MA"; ubid-main=134-1917772-8632935; skin=noskin; lc-main=en_US; session-id-time=2082787201l; aws_lang=en; aws-target-data=%7B%22support%22%3A%221%22%7D; s_fid=0B446F6A019CC362-28D3BF6FE12761FF; aws-ubid-main=123-2450080-4748301; remember-account=false; s_sq=awsamazonallprod1%3D%2526pid%253Dhttps%25253A%25252F%25252Fportal.aws.amazon.com%25252Fbilling%25252Fsignup%252523%25252Fstart%2526oid%253Dfunction%252528e%252529%25257Bif%252528s%252526%252526n.__isDisabled%252528%252529%252529returne.preventDefault%252528%252529%25253Bvart%25253De.button%25252Cr%25253De.ctrlKey%25252Ci%25253De.shiftKey%25252Co%2526oidt%253D2%2526ot%253DSUBMIT; session-id-eu=262-2636458-8636513; ubid-acbuk=258-8875985-4065941; session-token=bwSTe9tnKxPVQf8sSS1EW09sq+f4hEGLmOWbEbgMz6LlkAu1eK8U2NyFJ4Wtnx7gu+C8FlFL7ATb/DO1azkUKdvIxTNXr+TIOPFiuuJxwHH59Q8wV81zx4PlMtow2iu5GmbbXU008+doh+JrfeqBH/IohrR8PMRK1HX+VPtePJxVy9L5eLeftPQttaOaKlI3gZrXk1TJyKLPQw8yTLDokp4VD/B5rFM0ZGTbgCRnkZPXXS/oTdkmGDTzPESpveO3; csm-hit=D1XQB0S3KJXBCNR015K6+b-D1XQB0S3KJXBCNR015K6|1625776829385',
    }
    page = 1
    reviews_date = []
    reviews_text = []
    reviews_owner = []
    while True:
        time.sleep(1)
        data = {
            'ie': 'UTF8',
            'reviewerType': 'all_reviews',
            'pageNumber': page,
        }
        page += 1
        response = requests.post('https://www.amazon.com' + reviews_url, headers=headers, data=data)
        result = BeautifulSoup(response.text, 'lxml')
        list_reviews = result.findAll('div', attrs={'data-hook': "review"})

        if list_reviews and page < 3:
            for a in list_reviews:

                title = a.find('a', attrs={'class': 'review-title'})
                if title is None:
                    continue
                else:
                    title = title.span.string

                review = a.find('div', attrs={'class': 'a-row a-spacing-small review-data'})
                if review is None:
                    continue
                else:
                    review = review.get_text()

                dateloc = a.find('span', attrs={'data-hook': 'review-date'})
                if dateloc is None:
                    continue
                else:
                    dateloc = dateloc.string
                    date = re.search('on(.+?)$', dateloc).group(1)

                owner = a.find('span', attrs={'class': 'a-profile-name'})
                if owner is None:
                    continue
                else:
                    owner = owner.string
                # append data to lists
                reviews_text.append(title + ' ' + review)
                reviews_date.append(date)
                reviews_owner.append(owner)
        else:
            break

    return reviews_text, reviews_date, reviews_owner


# get reviews for all product
def get_review(products):
    products_urls = products['url'].to_list()
    all_reviews_id = []
    all_reviews_text = []
    all_reviews_date = []
    all_reviews_owner = []
    for url in products_urls:

        time.sleep(1)
        url_tmp = unquote(url)
        url_base = url_tmp.split('?')[0]
        params = tuple(get_url_params(url))
        headers = {
            'authority': 'www.amazon.com',
            'cache-control': 'max-age=0',
            'rtt': '50',
            'downlink': '5.8',
            'ect': '4g',
            'upgrade-insecure-requests': '1',
            'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.114 Safari/537.36 OPR/75.0.3969.171',
            'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
            'sec-fetch-site': 'none',
            'sec-fetch-mode': 'navigate',
            'sec-fetch-user': '?1',
            'sec-fetch-dest': 'document',
            'accept-language': 'en-US,en;q=0.9',
            'cookie': 'session-id=146-3469082-1944640; i18n-prefs=USD; sp-cdn="L5Z9:MA"; ubid-main=134-1917772-8632935; skin=noskin; lc-main=en_US; session-id-time=2082787201l; aws_lang=en; aws-target-data=%7B%22support%22%3A%221%22%7D; s_fid=0B446F6A019CC362-28D3BF6FE12761FF; aws-ubid-main=123-2450080-4748301; remember-account=false; s_sq=awsamazonallprod1%3D%2526pid%253Dhttps%25253A%25252F%25252Fportal.aws.amazon.com%25252Fbilling%25252Fsignup%252523%25252Fstart%2526oid%253Dfunction%252528e%252529%25257Bif%252528s%252526%252526n.__isDisabled%252528%252529%252529returne.preventDefault%252528%252529%25253Bvart%25253De.button%25252Cr%25253De.ctrlKey%25252Ci%25253De.shiftKey%25252Co%2526oidt%253D2%2526ot%253DSUBMIT; session-id-eu=262-2636458-8636513; ubid-acbuk=258-8875985-4065941; session-token=F24vKlcvOyJor3Juk+KFJSLeE1Chf5UnP/kjeDwTzdX+uPfNifgfVixUxOKxBGhjHt9bbTcql+K9VDTTdk6ljbKF/8XBaVNEP1B+piqrd6NbFdn36awOO6tzP32EITTuT8RaQVSUVK7yBtnRzU6SLfiueNmawekOgLPp+B19I27DbBLS7hu2XufF6Mb6JTrd; csm-hit=s-S73BZF2VFF7ZN5SDSSQD|1628520358688',
        }
        response = requests.get('https://www.amazon.com' + url_base, headers=headers, params=params)
        result = BeautifulSoup(response.text, 'lxml')

        reviews_url = result.find('div', attrs={'id': 'reviews-medley-footer'})

        if reviews_url is None:
            continue
        else:
            reviews_url = reviews_url.find('a')['href'].split('?')[0]

        reviews_text, reviews_date, reviews_owner = scrap_reviews(reviews_url)
        all_reviews_text += reviews_text
        all_reviews_date += reviews_date
        all_reviews_owner += reviews_owner

        product_id = products[products['url'] == url]['product_id'].values[0]
        all_reviews_id += [product_id] * len(reviews_text)

    reviews = pd.DataFrame(list(zip(all_reviews_id, all_reviews_text, all_reviews_date, all_reviews_owner)),
                           columns=['product_id', 'text', 'date_rev', 'owner'])

    return reviews


def plot_products_rating(products):
    bins = [0, 1, 2, 3, 4, 5]
    grouped = products['rating'].value_counts(bins=bins, sort=False).to_frame()
    fig = px.bar(x=['[0,1[', '[1,2[', '[2,3[', '[3,4[', '[4,5['],
                 y=grouped['rating'].to_list(),
                 labels={
                     "x": "Rating ranges",
                     "y": "Number of products",
                 }
                 )
    fig.update_layout(
        paper_bgcolor=colors['background'],
        plot_bgcolor=colors['background'],
        font=dict(color=colors['text'])
    )

    return fig


# plot products prices
def plot_products_price(products):
    bins = [[0, 10], [10, 20], [20, 30], [30, 40], [40, 50], [50, 60], [60, 70], [70, 80], [80, 90], [90, 100],
            [100, np.Inf]]
    count = []
    for x in bins:
        count.append(products[(products["price"] >= x[0]) & (products["price"] < x[1])]['price'].count())
    bins = ['[0, 10[', '[10, 20[', '[20, 30[', '[30, 40[', '[40, 50[', '[50, 60[', '[60, 70[', '[70, 80[', '[80, 90[',
            '[90, 100[', '[100, more than 100[']
    fig = px.bar(x=bins,
                 y=count,
                 labels={
                     "x": "Price ranges",
                     "y": "Number of products",
                 }
                 )
    fig.update_layout(
        paper_bgcolor=colors['background'],
        plot_bgcolor=colors['background'],
        font=dict(color=colors['text'])
    )
    return fig


# preprocessing corpus
def preproc_text(corpus):
    lemmmatizer = WordNetLemmatizer()

    preporc_corpus = []

    for review in corpus:
        # tokenize each review
        review_tokens = word_tokenize(review)
        review_tokens = [word.lower() for word in review_tokens]
        # limmatized and clean review
        review_lemmatized = [
            lemmmatizer.lemmatize(word)
            for word in review_tokens
            if (not word in stopwords.words('english')
                and word.isalpha())
        ]
        preporc_corpus.append(review_lemmatized)

    return preporc_corpus


# joined corpus function
def join_corpus(corpus):
    joined_corupus = []

    for review in corpus:
        delim = ' '
        joined_review = delim.join(review)
        joined_corupus.append(joined_review)

    return joined_corupus


# TFIDF function
def tfidf(corpus):
    # join token in one doc for tfidf
    joined_corupus = join_corpus(corpus)

    with open('tfidfvectorizer.pkl', 'rb') as f:
        tfidfvectorizer = pickle.load(f)

    X = tfidfvectorizer.transform(joined_corupus)
    return X


# predict sentiments
def predict_sentiments(reviews):
    preproc_reviews = preproc_text(reviews['text'])
    X = tfidf(preproc_reviews)

    with open('LogisticRegression.pkl', 'rb') as f:
        clf = pickle.load(f)

    polarity = clf.predict(X)

    sentiments = pd.DataFrame(
        list(zip(reviews['product_id'], polarity, reviews['text'], reviews['date_rev'], reviews['owner'])),
        columns=['product_id', 'polarity', 'text', 'date_rev', 'owner'])

    return sentiments


# plot pie graph
def plot_pie_graph(sentiments):
    polarity = sentiments['polarity']

    positive = (polarity == 2).sum()
    negative = (polarity == 1).sum()

    labels = ['positive', 'negative']
    values = [positive, negative]

    df = pd.DataFrame(zip(labels, values), columns=['Polarity', 'values'])
    fig = px.pie(df, values='values', names='Polarity', color='Polarity',
                 color_discrete_map={
                     "negative": "#CA2020",
                     "positive": "#137E12"}
                 )
    fig.update_layout(
        paper_bgcolor=colors['background'],
        plot_bgcolor=colors['background'],
        font=dict(color=colors['text'])
    )

    return fig


# get years
def get_years(sentiments):
    df = sentiments.copy()
    df['date_rev'] = df['date_rev'].apply(lambda x: x[-4:])
    years = np.flip(np.sort(df['date_rev'].unique()))
    return [{'label': year, 'value': year} for year in years]


# plot sentiment by year
def plot_sentiment_year(sentiments, year):
    df = sentiments.copy()
    df['month'] = df['date_rev'].apply(lambda x: x.split()[0])
    df['date_rev'] = df['date_rev'].apply(lambda x: x[-4:])
    df = df[df.date_rev == year]

    # compute polarity by month
    df_fig = pd.DataFrame(columns=['polarity', 'month', 'count'])
    months = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October',
              'November', 'December']
    for month in months:
        # compute negative
        count = df[(df['polarity'] == 1) & (df['month'] == month)].count()[0]
        new_row = {'polarity': 'negative', 'month': month, 'count': count}
        df_fig = df_fig.append(new_row, ignore_index=True)
        # compute positive
        count = df[(df['polarity'] == 2) & (df['month'] == month)].count()[0]
        new_row = {'polarity': 'positive', 'month': month, 'count': count}
        df_fig = df_fig.append(new_row, ignore_index=True)

    fig = px.line(df_fig, x="month", y="count", color='polarity', markers=True,
                  color_discrete_map={
                      "negative": "#CA2020",
                      "positive": "#137E12"})
    fig.update_traces(mode="markers+lines", hovertemplate=None)
    fig.update_layout(
        hovermode="x unified",
        paper_bgcolor=colors['background'],
        plot_bgcolor=colors['background'],
        font=dict(color=colors['text'])
    )
    return fig


# aspect-based Sentiment Analysis
def aspect_based(reviews):
    nlp = spacy.load("en_core_web_sm")
    # split reviews into sentences
    review_sentences = []
    for review in reviews:
        sentences = review.split('.')
        review_sentences += sentences

    # get aspect and description
    aspects = []
    for sentence in review_sentences:
        doc = nlp(sentence)
        descriptive_term = ''
        target = ''
        for token in doc:
            if token.dep_ == 'nsubj' and token.pos_ == 'NOUN':
                target = token.lemma_
            if token.pos_ == 'ADJ':
                prepend = ''
                for child in token.children:
                    if child.pos_ != 'ADV':
                        continue
                    prepend += child.text + ' '
                descriptive_term = prepend + token.text

        aspects.append({'aspect': target, 'description': descriptive_term})

    # get polarity
    aspects_df = pd.DataFrame(columns=['aspect', 'description', 'polarity', 'subjectivity', 'sentiment'])
    for aspect in aspects:
        if aspect['aspect'] == '' or aspect['description'] == '':
            continue
        subjectivity = TextBlob(aspect['description']).sentiment.subjectivity
        polarity = TextBlob(aspect['description']).sentiment.polarity

        if subjectivity < 0.5:
            continue
        if polarity < 0:
            sentiment = "negative"
        else:
            sentiment = "positive"
        new_row = {
            'aspect': aspect['aspect'],
            'description': aspect['description'],
            'polarity': polarity,
            'subjectivity': subjectivity,
            'sentiment': sentiment,
        }
        aspects_df = aspects_df.append(new_row, ignore_index=True)

    df = aspects_df.value_counts(subset=['aspect', 'sentiment'], sort=False).reset_index().rename(columns={0: 'count'})
    df = df.groupby(['aspect', 'sentiment'])['count'].aggregate('mean').unstack()
    df = df.sort_values(by=['positive', 'negative'], ascending=False, na_position='last')
    df = df.fillna(0)
    df.reset_index(level=0, inplace=True)

    return df


# Building the app layout
colors = {
    'background': '#1F2940',
    'text': '#ffffff'
}

figure_layout = {
    'plot_bgcolor': colors['background'],
    'paper_bgcolor': colors['background'],
    'font': {
        'color': colors['text']
    }
}

app.layout = html.Div(
    [
        # global storage
        dcc.Store(id='sentiments_store'),
        dcc.Store(id='products_store'),

        # header
        dbc.Row(
            [
                # amazon logo
                dbc.Col(
                    html.Img(src="/static/images/amazon_white_logo.png", width="150px",
                             className="img-fluid d-block mx-auto mb-md-0 mb-4"),
                    width=12,
                    md="auto"
                ),
                # dashboard title
                dbc.Col(
                    html.H4("Amazon products reputation monitoring"),
                    className="text-center text-white d-flex justify-content-center align-items-center",
                    width=12,
                    md=""
                )
            ],
            className="mb-5"
        ),
        # choose category header
        dbc.Row(
            dbc.Col(
                html.H4("Choose category", className="text-white")
            )
        ),
        dbc.Row(
            dbc.Col(
                dcc.Loading(id="loading_category", type="default", children=html.Div(id="loading_category_output"))
            )
        ),
        # choose category
        dbc.Card(
            dbc.Row(
                [
                    dbc.Col(
                        dbc.FormGroup(
                            [
                                dbc.Label("Main categories :", html_for="dropdown",
                                          className="font-weight-bold"),
                                dcc.Dropdown(
                                    id="main_categories",
                                    options=categories,
                                ),
                            ],
                            className="mb-2"
                        ),
                        md=4,
                        width=12
                    ),
                    dbc.Col(
                        dbc.FormGroup(
                            [
                                dbc.Label("Sub categories :", html_for="dropdown",
                                          className="font-weight-bold"),
                                dcc.Dropdown(
                                    id="sub_categories",
                                    options=[],
                                ),
                            ],
                            className="mb-2"
                        ),
                        md=4,
                        width=12
                    ),
                    dbc.Col(
                        dbc.FormGroup(
                            [
                                dbc.Label("Third level categories :", html_for="dropdown",
                                          className="font-weight-bold"),
                                dcc.Dropdown(
                                    id="third_categories",
                                    options=[],
                                ),
                            ],
                            className="mb-2"
                        ),
                        md=4,
                        width=12
                    )
                ]
            ),
            className="mb-5"
        ),
        # category stats header
        dbc.Row(
            dbc.Col(
                html.H4("Category's statistics", className="text-white")
            )
        ),
        # category stats
        dbc.Row(
            [
                dbc.Col(
                    dbc.Card(
                        dbc.CardBody(
                            [
                                html.Div(
                                    [
                                        html.Div(
                                            [
                                                html.H5("Category",
                                                        className="card-stats-title text-white"),
                                                html.Span("----", id="category", className="text-white")

                                            ],
                                            className="media-body text-left"
                                        ),
                                        html.Div(
                                            html.I(className="fas fa-bookmark h4"),
                                            className="align-self-center"
                                        )
                                    ],
                                    className="media d-flex"
                                ),

                            ],
                            className="p-2"
                        ),
                        className="border-0 rounded-0 shadow-sm bg-gradient-info"
                    ),
                    className="card-stats  mb-lg-0 mb-4",
                    lg=3,
                    md=6,
                    width=12

                ),
                dbc.Col(
                    dbc.Card(
                        dbc.CardBody(
                            [
                                html.Div(
                                    [
                                        html.Div(
                                            [
                                                html.H5("Products",
                                                        className="card-stats-title text-white"),
                                                html.Span("----", id="product_count",
                                                          className="text-white")

                                            ],
                                            className="media-body text-left"
                                        ),
                                        html.Div(
                                            html.I(className="fas fa-shopping-basket h4"),
                                            className="align-self-center"
                                        )
                                    ],
                                    className="media d-flex"
                                ),

                            ],
                            className="p-2"
                        ),
                        className="border-0 rounded-0 shadow-sm bg-gradient-danger"
                    ),
                    className="card-stats  mb-lg-0 mb-4",
                    lg=3,
                    md=6,
                    width=12

                ),
                dbc.Col(
                    dbc.Card(
                        dbc.CardBody(
                            [
                                html.Div(
                                    [
                                        html.Div(
                                            [
                                                html.H5("Mean Price",
                                                        className="card-stats-title text-white"),
                                                html.Span("----", id="mean_price",
                                                          className="text-white")

                                            ],
                                            className="media-body text-left"
                                        ),
                                        html.Div(
                                            html.I(className="fas fa-dollar-sign h4"),
                                            className="align-self-center"
                                        )
                                    ],
                                    className="media d-flex"
                                ),

                            ],
                            className="p-2"
                        ),
                        className="border-0 rounded-0 shadow-sm bg-gradient-warning"
                    ),
                    className="card-stats  mb-md-0 mb-4",
                    lg=3,
                    md=6,
                    width=12
                ),
                dbc.Col(
                    dbc.Card(
                        dbc.CardBody(
                            [
                                html.Div(
                                    [
                                        html.Div(
                                            [
                                                html.H5("Mean Rating",
                                                        className="card-stats-title text-white"),
                                                html.Span("----", id="mean_rating",
                                                          className="text-white")

                                            ],
                                            className="media-body text-left"
                                        ),
                                        html.Div(
                                            html.I(className="fas fa-star h4"),
                                            className="align-self-center"
                                        )
                                    ],
                                    className="media d-flex"
                                ),

                            ],
                            className="p-2"
                        ),
                        className="border-0 rounded-0 shadow-sm bg-gradient-primary"
                    ),
                    className="card-stats",
                    lg=3,
                    md=6,
                    width=12
                ),
            ],
            className="mb-4"
        ),
        # price and rating mean
        dbc.Row(
            [
                dbc.Col(
                    dbc.Card(
                        [
                            dbc.CardHeader(html.H5("Number of products by ratings"),
                                           className="border-0 bg-transparent text-center"),
                            dbc.CardBody(
                                dcc.Graph(
                                    id="products_rating",
                                    figure={
                                        'data': [],
                                        'layout': figure_layout
                                    }),
                                className="p-0"
                            )
                        ],
                        className="border-0 rounded-0 shadow-sm mb-4"
                    ),
                    lg=6,
                    width=12
                ),
                dbc.Col(
                    dbc.Card(
                        [
                            dbc.CardHeader(html.H5("Number of products by prices"),
                                           className="border-0 bg-transparent text-center"),
                            dbc.CardBody(dcc.Graph(
                                id="products_price",
                                figure={
                                    'data': [],
                                    'layout': figure_layout
                                }

                            ),
                                className="p-0")
                        ],
                        className="border-0 rounded-0 shadow-sm mb-4"
                    ),
                    lg=6,
                    width=12
                )
            ],
            className="mb-5"
        ),
        # choose product header
        dbc.Row(
            dbc.Col(
                html.H4("Choose product", className="text-white")
            )
        ),
        # product list
        dbc.Row(
            [
                dbc.Col(
                    dbc.Card(
                        [
                            dbc.CardBody(
                                [
                                    dbc.FormGroup(
                                        [
                                            dcc.Dropdown(
                                                id="products_list",
                                                options=[],
                                            ),
                                        ],
                                        className="mb-0"
                                    ),

                                ],
                                className="p-0"
                            )
                        ],
                        className="border-0 rounded-0 shadow-sm"
                    ),
                )
            ],
            className="mb-4"
        ),
        # product container
        dbc.Row(
            [
                dbc.Col(id="product_container")
            ],
            className="mb-5"
        ),
        # sentiment analysis Header
        dbc.Row(
            dbc.Col(
                html.H4("Sentiment analysis", className="text-white"),
            )
        ),
        # sentiment analysis
        dbc.Row(
            [
                dbc.Col(
                    # sentiment by year
                    dbc.Card(
                        [
                            dbc.CardHeader(
                                dbc.Row(
                                    [
                                        dbc.Col(html.H5("Sentiments polarity by year", className="text-center"),
                                                sm="auto", width=12),
                                        dbc.Col(dcc.Dropdown(options=[], id="sentiments_years_option", clearable=False),
                                                md=3, sm=4, width=6)

                                    ],
                                    justify="center"
                                ),
                                className="border-0 bg-transparent text-center"),
                            dbc.CardBody(
                                [
                                    dbc.Row(
                                        [
                                            dbc.Col(
                                                dcc.Graph(
                                                    id="sentiment_year_figure",
                                                    figure={
                                                        'data': [],
                                                        'layout': figure_layout
                                                    }
                                                ),
                                                width=12
                                            )
                                        ]
                                    )
                                ],
                                className="p-0"
                            )
                        ],
                        className="border-0 rounded-0 shadow-sm"
                    ),
                    className="mb-lg-0 mb-4",
                    lg=7,
                    width=12
                ),
                dbc.Col(
                    # pie graph
                    dbc.Card(
                        [
                            dbc.CardHeader(html.H5("Percentage of sentiments polarity"),
                                           className="border-0 bg-transparent text-center"),
                            dbc.CardBody(
                                dcc.Graph
                                    (
                                    id="sentiment_pie_figure",
                                    figure={
                                        'data': [],
                                        'layout': figure_layout
                                    }
                                ),
                                className="p-0")
                        ],
                        className="border-0 rounded-0 shadow-sm"
                    ),
                    lg=5,
                    width=12
                )
            ],
            className="mb-4"
        ),
        # negative and positive review examples
        dbc.Row(
            [
                dbc.Col(
                    dbc.Card(
                        [
                            dbc.CardHeader(html.H5("Example of negative review"),
                                           className="border-0 bg-transparent text-center"),
                            dbc.CardBody(
                                html.Blockquote([], id="negative_review")
                            )
                        ],
                        className="border-0 rounded-0 shadow-sm bg-gradient-negative"
                    ),
                    className="mb-lg-0 mb-4",
                    lg=6,
                    width=12
                ),
                dbc.Col(
                    dbc.Card(
                        [
                            dbc.CardHeader(html.H5("Example of positive review"),
                                           className="border-0 bg-transparent text-center"),
                            dbc.CardBody(
                                html.Blockquote([], id="positive_review")
                            )
                        ],
                        className="border-0 rounded-0 shadow-sm bg-gradient-positive"
                    ),
                    lg=6,
                    width=12
                )
            ],
            className="mb-5"
        ),
        # aspect-based sentiments analysis Header
        dbc.Row(
            dbc.Col(
                html.H4("Aspect-based sentiments analysis", className="text-white"),
            )
        ),
        # aspect-based sentiments analysis
        dbc.Row(
            [
                dbc.Col(dbc.Card(dbc.CardBody(id='table')))
            ]
        )
    ]
)


# app.layout = dbc.Container(
#     [
#         # global storage
#         dcc.Store(id='sentiments_store'),
#         dcc.Store(id='products_store'),
#
#         # navbar
#         dbc.Row(
#             [
#                 # amazon logo
#                 dbc.Col(
#                     html.Img(src="/static/images/amazon_white_logo.png", width="150px"),
#                     width="auto",
#                     className="img-fluid"
#                 ),
#                 # dashboard title
#                 dbc.Col(
#                     html.H4("Web scraping and sentiment analysis for product reputation monitoring"),
#                     className="text-center text-white d-flex justify-content-center align-items-center"
#                 )
#             ],
#             className="bg-blue-dark shadow-sm py-1 px-2"
#         ),
#         # main-content
#         html.Div(
#             [
#                 dbc.Card(
#                     [
#                         dbc.CardHeader(
#                             [
#                                 html.H4("Choose a category", className="mb-0"),
#                                 dcc.Loading(id="loading_category", type="default",
#                                             children=html.Div(id="loading_category_output"))
#                             ],
#                             className="bg-white"
#                         ),
#                         dbc.CardBody(
#                             dbc.Row(
#                                 [
#                                     dbc.Col(
#                                         dbc.FormGroup(
#                                             [
#                                                 dbc.Label("Main categories", html_for="dropdown"),
#                                                 dcc.Dropdown(
#                                                     id="main_categories",
#                                                     options=categories,
#                                                 ),
#                                             ]
#                                         ),
#                                         width=4,
#                                     ),
#                                     dbc.Col(
#                                         dbc.FormGroup(
#                                             [
#                                                 dbc.Label("Sub categories", html_for="dropdown"),
#                                                 dcc.Dropdown(
#                                                     id="sub_categories",
#                                                     options=[],
#                                                 ),
#                                             ]
#                                         ),
#                                         width=4,
#                                     ),
#                                     dbc.Col(
#                                         dbc.FormGroup(
#                                             [
#                                                 dbc.Label("Third level categories", html_for="dropdown"),
#                                                 dcc.Dropdown(
#                                                     id="third_categories",
#                                                     options=[],
#                                                 ),
#                                             ]
#                                         ),
#                                         width=4,
#                                     ),
#
#                                 ],
#                                 form=True,
#                                 className="justify-content-center"
#                             )
#                         )
#                     ],
#                     className="border-0 rounded-0 shadow-sm mb-4"
#                 ),
#                 # stats cards
#                 dbc.Row(
#                     [
#                         # card col
#                         dbc.Col(
#
#                             dbc.Card(
#                                 dbc.CardBody(
#                                     [
#                                         html.Div(
#                                             [
#                                                 html.Div(
#                                                     [
#                                                         html.H3("Category", className="card-stats-title text-white"),
#                                                         html.Span("----", id="category", className="text-white")
#
#                                                     ],
#                                                     className="media-body text-left"
#                                                 ),
#                                                 html.Div(
#                                                     html.I(className="fas fa-bookmark h2"),
#                                                     className="align-self-center"
#                                                 )
#                                             ],
#                                             className="media d-flex"
#                                         ),
#
#                                     ]
#                                 ),
#                                 className="border-0 rounded-0 shadow-sm bg-blue-dark danger"
#                             ),
#                             className="card-stats",
#                             width=3
#
#                         ),
#                         # card col
#                         dbc.Col(
#
#                             dbc.Card(
#                                 dbc.CardBody(
#                                     html.Div(
#                                         [
#                                             html.Div(
#                                                 [
#                                                     html.H3("Product Count", className="card-stats-title  text-white"),
#                                                     html.Span("----", id="product_count", className="text-white")
#
#                                                 ],
#                                                 className="media-body text-left"
#                                             ),
#                                             html.Div(
#                                                 html.I(className="fas fa-shopping-basket h2"),
#                                                 className="align-self-center"
#                                             )
#                                         ],
#                                         className="media d-flex"
#                                     )
#                                 ),
#                                 className="border-0 rounded-0 shadow-sm  bg-blue-dark success"
#                             ),
#                             className="card-stats",
#                             width=3
#
#                         ),
#                         # card col
#                         dbc.Col(
#
#                             dbc.Card(
#                                 dbc.CardBody(
#                                     html.Div(
#                                         [
#                                             html.Div(
#                                                 [
#                                                     html.H3("Mean Price", className="card-stats-title  text-white"),
#                                                     html.Span("----", id="mean_price", className="text-white")
#
#                                                 ],
#                                                 className="media-body text-left"
#                                             ),
#                                             html.Div(
#                                                 html.I(className="fas fa-dollar-sign h2"),
#                                                 className="align-self-center"
#                                             )
#                                         ],
#                                         className="media d-flex"
#                                     )
#                                 ),
#                                 className="border-0 rounded-0 shadow-sm bg-blue-dark warning"
#                             ),
#                             className="card-stats",
#                             width=3
#
#                         ),
#                         # card col
#                         dbc.Col(
#
#                             dbc.Card(
#                                 dbc.CardBody(
#                                     html.Div(
#                                         [
#                                             html.Div(
#                                                 [
#                                                     html.H3("Mean Rating", className="card-stats-title  text-white"),
#                                                     html.Span("----", id="mean_rating", className="text-white")
#
#                                                 ],
#                                                 className="media-body text-left"
#                                             ),
#                                             html.Div(
#                                                 html.I(className="fas fa-star h2"),
#                                                 className="align-self-center"
#                                             )
#                                         ],
#                                         className="media d-flex"
#                                     )
#                                 ),
#                                 className="border-0 rounded-0 shadow-sm bg-blue-dark info"
#                             ),
#                             className="card-stats",
#                             width=3
#
#                         ),
#                     ],
#                     className="mb-4"
#                 ),
#                 # products
#                 dbc.Card(
#                     [
#                         dbc.CardHeader(html.H4("Choose a product", className="mb-0"), className="bg-white"),
#                         dbc.CardBody(
#                             [
#                                 dbc.FormGroup(
#                                     [
#                                         dcc.Dropdown(
#                                             id="products_list",
#                                             options=[],
#                                         ),
#                                     ],
#                                     className="mb-0"
#                                 ),
#
#                             ],
#                             id="product_container"
#                         )
#                     ],
#                     className="border-0 rounded-0 shadow-sm mb-4"
#                 ),
#                 # plot products rating and price
#                 dbc.Row(
#                     [
#                         dbc.Col(
#                             dbc.Card(
#                                 [
#                                     dbc.CardHeader(html.H4("Products rating", className="mb-0"), className="bg-white"),
#                                     dbc.CardBody(dcc.Graph(id="products_rating"))
#                                 ],
#                                 className="border-0 rounded-0 shadow-sm mb-4"
#                             ),
#                             width=6
#                         ),
#                         dbc.Col(
#                             dbc.Card(
#                                 [
#                                     dbc.CardHeader(html.H4("Products price", className="mb-0"), className="bg-white"),
#                                     dbc.CardBody(dcc.Graph(id="products_price"))
#                                 ],
#                                 className="border-0 rounded-0 shadow-sm mb-4"
#                             ),
#                             width=6
#                         )
#                     ]
#                 ),
#                 dbc.Row(
#                     dbc.Col(
#                         dbc.Card(
#                             [
#                                 dbc.CardHeader(html.H4("Negative review example", className="mb-0"),
#                                                className="bg-white"),
#                                 dbc.CardBody(
#                                     html.Blockquote([], id="negative_review")
#                                 )
#                             ],
#                             className="border-0 rounded-0 shadow-sm mb-4"
#                         )
#                     )
#                 ),
#                 dbc.Row(
#                     dbc.Col(
#                         dbc.Card(
#                             [
#                                 dbc.CardHeader(html.H4("Positive review example", className="mb-0"),
#                                                className="bg-white"),
#                                 dbc.CardBody(
#                                     html.Blockquote([], id="positive_review")
#                                 )
#                             ],
#                             className="border-0 rounded-0 shadow-sm mb-4"
#                         )
#                     )
#                 ),
#                 dbc.Row(
#                     [
#                         dbc.Col(
#                             # sentiment by year
#                             dbc.Card(
#                                 [
#                                     dbc.CardHeader(
#                                         [
#                                             dbc.Row(
#                                                 [
#                                                     dbc.Col(html.H4("Products sentiment by year", className="mb-0")),
#                                                     dbc.Col(
#                                                         dcc.Dropdown(options=[], id="sentiments_years_option",
#                                                                      clearable=False),
#                                                     )
#                                                 ],
#                                                 justify="start"
#
#                                             )
#                                         ],
#                                         className="bg-white"
#                                     ),
#                                     dbc.CardBody(dcc.Graph(id="sentiment_year_figure"))
#                                 ],
#                                 className="border-0 rounded-0 shadow-sm mb-4"
#                             ),
#                             width=8
#                         ),
#                         dbc.Col(
#                             # pie graph
#                             dbc.Card(
#                                 [
#                                     dbc.CardHeader(html.H4("Sentiments percentage ", className="mb-0"),
#                                                    className="bg-white"),
#                                     dbc.CardBody(dcc.Graph(id="sentiment_pie_figure"))
#                                 ],
#                                 className="border-0 rounded-0 shadow-sm mb-4"
#                             ),
#                             width=4
#                         )
#                     ]
#                 )
#
#             ]
#             ,
#             className="p-3 main-content"
#         ),
#         dcc.Loading(
#             id="loading-1",
#             type="default",
#             children=html.Div(id="loading-output-1")
#         ),
#     ],
#     fluid=True,
#     className="bg-light"
# )


# get sub categories callbacks

@app.callback(
    Output("sub_categories", "options"),
    Input("main_categories", "value"),
)
def update_sub_categories(category):
    sub_categories = get_sub_categories(category)
    return [{'label': i, 'value': sub_categories[i]} for i in sub_categories.keys()]


# get third level categories callbacks
@app.callback(
    Output("third_categories", "options"),
    Input("sub_categories", "value")
)
def update_third_level_categories(sub_category):
    third_level_categories = get_third_level_categories(sub_category)
    return [{'label': i, 'value': third_level_categories[i]} for i in third_level_categories.keys()]


# get stats for third category
@app.callback(
    Output("loading_category_output", "children"),
    Output("category", "children"),
    Output("product_count", "children"),
    Output("mean_price", "children"),
    Output("mean_rating", "children"),
    Output("products_list", "options"),
    Output("products_rating", "figure"),
    Output("products_price", "figure"),
    Output("negative_review", "children"),
    Output("positive_review", "children"),
    Output("sentiment_pie_figure", "figure"),
    Output("sentiments_years_option", "options"),
    Output("sentiments_store", "data"),
    Output("products_store", "data"),
    Output("product_container", "children"),
    Output("table", "children"),
    # inputs for choosing category
    Input("loading_category", "value"),
    Input("third_categories", "value"),
    Input("third_categories", "options"),
    # inputs for choosing product
    Input("products_list", "value"),
    # load data
    State("sentiments_store", "data"),
    State("products_store", "data")

)
def update_stats(value, third_category, options, product_id, sentiments_data, products_data):
    ctx = dash.callback_context
    input_id = ctx.triggered[0]['prop_id'].split('.')[0]

    # input from category
    if input_id == 'third_categories':
        category = [x['label'] for x in options if x['value'] == third_category]
        products, category, product_count, mean_price, mean_rating = get_products(third_category, category)

        # show products
        products_list = [{'label': product['title'], 'value': product['product_id']} for product in
                         products.to_dict('records')]

        # plot products rating
        products_rating_figure = plot_products_rating(products)

        # plot products prices
        products_price_figure = plot_products_price(products)

        # get all reviews
        reviews = get_review(products)

        # predict sentiment
        sentiments = predict_sentiments(reviews)

        # negative review example
        negative_review = sentiments[sentiments.polarity == 1].iloc[0]
        negative_review_layout = [
            html.P(negative_review['text'], className="mb-0"),
            html.Footer(negative_review['owner'] + ' - ' + negative_review['date_rev'],
                        className="blockquote-footer blockquote-footer-color")
        ]

        # positive review example
        positive_review = sentiments[sentiments.polarity == 2].iloc[0]
        positive_review_layout = [
            html.P(positive_review['text'], className="mb-0"),
            html.Footer(positive_review['owner'] + ' - ' + positive_review['date_rev'],
                        className="blockquote-footer blockquote-footer-color")
        ]

        # sentiments percentage
        sentiment_pie_figure = plot_pie_graph(sentiments)

        # get years
        years = get_years(sentiments)

        return value, \
               category, \
               product_count, \
               mean_price, \
               mean_rating, \
               products_list, \
               products_rating_figure, \
               products_price_figure, \
               negative_review_layout, \
               positive_review_layout, \
               sentiment_pie_figure, \
               years, \
               sentiments.to_json(orient='split'), \
               products.to_json(orient='split'), \
               dash.no_update, \
               dash.no_update

    # input from products
    if input_id == 'products_list':

        products = pd.read_json(products_data, orient='split')
        product = products[products['product_id'] == product_id]

        # get product review
        product_review = get_review(product)

        # get product sentiment
        product_sentiments = predict_sentiments(product_review)

        # product  negative review example
        product_negative_review = product_sentiments[product_sentiments.polarity == 1].iloc[0]
        product_negative_review_layout = [
            html.P(product_negative_review['text'], className="mb-0"),
            html.Footer(product_negative_review['owner'] + ' - ' + product_negative_review['date_rev'],
                        className="blockquote-footer")
        ]

        # product positive review example
        product_positive_review = product_sentiments[product_sentiments.polarity == 2].iloc[0]
        product_positive_review_layout = [
            html.P(product_positive_review['text'], className="mb-0"),
            html.Footer(product_positive_review['owner'] + ' - ' + product_positive_review['date_rev'],
                        className="blockquote-footer")
        ]

        # sentiments percentage
        product_sentiment_pie_figure = plot_pie_graph(product_sentiments)

        # get years
        product_years = get_years(product_sentiments)

        # create product info container
        product = product.values.tolist()[0]

        img = product[2]
        title = product[1]
        price = product[3]
        rating = []
        for i in range(int(product[4])):
            rating.append(html.I(className="fas fa-star"))
        for j in range(5 - int(product[4])):
            rating.append(html.I(className="far fa-star"))
        product_container = dbc.Card(
            dbc.Row(
                [
                    dbc.Col(
                        [
                            html.Img(src=img, className="product-img")
                        ],
                        sm=4,
                        width=12
                    ),
                    dbc.Col(
                        [
                            html.H6(title),
                            html.H3('$' + str(price)),
                            html.Div(rating, className="text-warning")
                        ],
                        className="text-white",
                        sm=8,
                        width=12
                    )
                ]
            ),
            className="product-item"
        )

        # aspect-based
        aspect_df = aspect_based(product_review['text'].to_list())
        table = dash_table.DataTable(
                columns=[{"name": i, "id": i} for i in aspect_df.columns],
                data=aspect_df.to_dict('records'),
                style_header={'backgroundColor': 'rgb(30, 30, 30)'},
                style_cell={
                    'backgroundColor': 'rgb(50, 50, 50)',
                    'color': 'white'
                },
            )

        return value, \
               dash.no_update, \
               dash.no_update, \
               dash.no_update, \
               dash.no_update, \
               dash.no_update, \
               dash.no_update, \
               dash.no_update, \
               product_negative_review_layout, \
               product_positive_review_layout, \
               product_sentiment_pie_figure, \
               product_years, \
               product_sentiments.to_json(orient='split'), \
               dash.no_update, \
               product_container, \
               table


# update the default value of years DropDown
@app.callback(
    Output("sentiments_years_option", "value"),
    Input("sentiments_years_option", "options")
)
def update_default_year(years):
    return [year['value'] for year in years][0]


# update sentiments by year figure
@app.callback(
    Output("sentiment_year_figure", "figure"),
    Input("sentiments_years_option", "value"),
    State("sentiments_store", "data")
)
def update_sentiments_year(year, data):
    sentiments = pd.read_json(data, orient='split')
    sentiment_year_figure = plot_sentiment_year(sentiments, year)

    return sentiment_year_figure


# choose a product
# @app.callback(
#     Output("sentiments_store", "data"),
#     Output("sentiments_years_option", "options"),
#     # Output("negative_review", "children"),
#     # Output("positive_review", "children"),
#     Input("products_list", "value"),
#     State("products_store", "data"),
#     State("sentiments_store", "data")
# )
# def update_product(product_id, products_data, sentiments_data):
#     products = pd.read_json(products_data, orient='split')
#     sentiments = pd.read_json(sentiments_data, orient='split')
#     product = products[products['id'] == product_id]
#     product_sentiments = sentiments[sentiments['id'] == product_id]
#     years = get_years(product_sentiments)
#
#     return product_sentiments, years


if __name__ == "__main__":
    app.run_server(debug=True, dev_tools_hot_reload=True)
