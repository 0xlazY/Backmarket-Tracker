#!/usr/bin/python3

'''
BackMarket price tracker and alerter
Set the 'price_wanted' and the 'false_positive_price' variables, see README for more informations
If you find any bugs, please report them under 'issues' in github

Note: Notify_run doesn't work with safari, for iOS devices, the next release will feature PushOver app support (https://pushover.net/) !

Made by 0xlazY !
'''

import requests, re
#from notify_run import Notify ## TODO

def get_currency(url):

    currency_dic = {
        '€': ['fr', 'es', 'it', 'de', 'be', 'at'],
        '$': ['com'],
        '£': ['uk'] ## co.uk
    }

    splited_url = url.split('.')
    #print(splited_url) ## debug
    
    if splited_url[3].split("/")[0] == 'uk':
        splited_url = 'uk'
    else:
        splited_url = splited_url[2].split("/")[0]
    #print(splited_url) ## debug
    if splited_url == 'at':
        country = 'at'
    else:
        country = 'com'

    currency_symbole = "$" ## default, if failed
    
    for key, value in currency_dic.items():
        if splited_url in value:
            currency_symbole = key

    #print(currency_symbole, country) ##Debug
    return currency_symbole, country


def get_webcontent(url):

    page = requests.get(url)
    content = page.content.decode()
    currency_symbole, country = get_currency(url)

    pattern = 'price_with_currency.\".{0,9}.\"'
    raw_prices = re.findall(pattern, content) # Parse the entire WebPage, search 'price_with_currency*€'
    #print(raw_prices) ## debug

    price_lst = []

    for price in raw_prices:
        try: # because of potential problems when loading webpages and inconsistency, use 'try' before any index reference ([.])
            if currency_symbole == '€' and country != 'at': ## symbole after price
                parsed_price = float(price.strip().split('"')[1].split('\xa0')[0].replace(',', '.')) # get rid of all the junk
            elif country == 'at':
                parsed_price = float(price.strip().split('"')[1].split('\xa0')[1].replace(',', '.'))
            else: ## symbole before price
                parsed_price = float(price.strip().split('"')[1].replace(currency_symbole, ''))

            if parsed_price > false_positive_price:
                price_lst.append(parsed_price) # add the formated price to the price_lst
        except:
            print("Problem with parsing! {}".format(price))
    
    return price_lst, currency_symbole


def alerter(price_lst, currency_symbole):
    minimum_price = price_lst[0] # Initialize first minimum price

    for price in price_lst: # Gets the actual minimum price
        if price < minimum_price:
            minimum_price = price
    
    if minimum_price <= price_wanted:
        headers = {'Content-Type': 'text/text; charset=utf-8'} # needed to send specials char such as € ...
        data_text = '{}\'s price has drop to {}{} !'.format(device_name, minimum_price, currency_symbole)

        requests.post(notify_run_url, data = data_text.encode('utf-8'), headers = headers) # Send POST request to notidy_run channel

def get_notify_run_url(config_file):
    conf = open(config_file, 'r')
    conf_url = conf.readline().strip()
    conf.close()

    return conf_url


def main():
    for url in url_lst:
        #print(get_webcontent(url))
        price_lst, currency_symbole = get_webcontent(url)
        alerter(price_lst, currency_symbole)
        #print(price_lst)
        #print(currency_symbole)


if __name__ == '__main__':
    url_lst = ['https://www.backmarket.at/iphone-x-64-gb-space-grau-ohne-vertrag-gebraucht/36833.html']
    device_name = 'iPhone X'
    # i.e, iPhone X 64gb Black

    notify_run_url = get_notify_run_url('config.cfg')
    # Create a notify_run channel and replace the url in config file (https://notify.run)
    ## TODO add channel creation with notidy_run module

    false_positive_price = 100 # Impossible price for the specified product
    price_wanted = 400 # Price of the product below which you want to receive a notification

    main()

