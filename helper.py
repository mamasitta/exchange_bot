import os
from datetime import datetime
import matplotlib
import matplotlib.pyplot as plt

import requests

from models.currency import Currency


def check_last_request(date):
    """ Function to check last request
    take date of request get from txt file date of last request to server,
    return True if request made more than 10 mn. False if les than 10 mn.
    """
    with open('date.txt', 'r') as file:
        last_request = file.read()
    minutes_diff = (date - datetime.strptime(last_request, '%Y-%m-%d %H:%M:%S')).total_seconds() / 60.0
    if minutes_diff > 10:
        return True
    else:
        return False


def send_request(date):
    """ Function to send request to server save last date of request in txt file, save currency in db
    :param date
    :return list of currency
    """
    # making request tos server
    response = requests.get('https://api.exchangeratesapi.io/latest?base=USD').json()
    result = response['rates']
    list_currency = []
    # save all currency in db, send response to user with all currency
    for currency in result:
        value = round(result[currency], 2)
        item = '{}: {}'.format(currency, value)
        list_currency.append(item)
    # save date of request in txt file
    with open('date.txt', 'wt') as file:
        file.write(str(date)[:19])
    # save all currency in db
    Currency.add_currency(list_currency)
    return list_currency


def create_graph(result, currency):
    """ function to generate graph
    :param result obj, currency
    :return name of file graph if created, else False
    """
    # get tuple of dates in datetime type
    obj = tuple(datetime.strptime(r, '%Y-%m-%d') for r in result)
    # sort list of dates
    date_sort = sorted(obj)
    # convert list of datetime type to string
    date = tuple(datetime.strftime(r, '%Y-%m-%d') for r in date_sort)
    # get tuple of prices
    price = tuple(result[d][currency] for d in date)
    # creating graph
    fig, ax = plt.subplots()
    ax.plot(date, price)
    ax.set(xlabel='Date', ylabel='Rate',
           title='Graph for {} from {} till {}'.format(currency, date[0], date[len(date)-1]))
    ax.grid()
    name = '{}{}.png'.format(datetime.strftime(datetime.now(), '%Y%m%d%H%M%S%f'), currency)
    fig.savefig(name)
    # if created return name else False
    if os.path.exists(name):
        return name
    else:
        return False

