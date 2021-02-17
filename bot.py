import asyncio
import os
import re
from datetime import datetime, timedelta
import requests

import telepot as telepot
from telepot.aio.loop import MessageLoop
from helper import check_last_request, send_request, create_graph
from config import TOKEN
from models.currency import Currency


async def handle(msg):
    """ Function to handle user input
    Take user massage and return response
    """
    command = msg['text']
    # get datetime of massage
    date = datetime.now()
    # function from helper to check when was last request
    check_request = check_last_request(date)
    if command == '/list':
        # if last request more than 10 mn ago
        if check_request:
            # make request to server for all currency
            result = send_request(date)
            massage = '\n'.join(result)
            await bot.sendMessage(msg['from']['id'], massage)
        else:
            # if last request les then 10 mn. ago
            print('from db')
            # get all currency from db
            result = Currency.get_all()
            # send response to user
            massage = '\n'.join(result)
            await bot.sendMessage(msg['from']['id'], massage)
    elif command[:9] == '/exchange':
        # get currency from user massage
        currency = command[len(command)-3:]
        # get amount of currency what user want to change
        amount_str = re.findall(r'([0-9]+)', command)
        print(amount_str)
        # check if user use valid command
        if len(amount_str) == 0 or currency.isupper() != True:
            await bot.sendMessage(msg['from']['id'], "Please use valid command!\nExample:\n/exchange $10 to CAD")
        # convert amount to float
        amount = float(amount_str[0])
        # if request made more than 10 mn. ago
        if check_request:
            # send request to server
            result = send_request(date)
            print(result)
            # round currency
            # rate = round(result[currency], 2)
            item = [r for r in result if currency in r]
            rate = item[0][5:]
            exchanged = float(rate) * amount
            await bot.sendMessage(msg['from']['id'], '${}'.format(exchanged))
        else:
            # if request les then 10 mn, make request to db
            result = Currency.get_all()
            # search for currency in least
            item = [r for r in result if currency in r]
            rate = item[0][5:]
            exchanged = float(rate) * amount
            await bot.sendMessage(msg['from']['id'], '${}'.format(exchanged))
    elif command[:8] == '/history':
        # get all date from command for request
        # get base and symbol from command
        base_symbols = re.findall(r'\w{3}/\w{3}', command)
        # get base
        base = base_symbols[0][:3]
        # get symbol
        symbols = base_symbols[0][4:]
        # calculate start_at date
        start_at_datetime = date - timedelta(days=6)
        # convert start_at date to string
        start_at = datetime.strftime(start_at_datetime, "%Y-%m-%d")
        # convert end date (today) to string
        end_at = datetime.strftime(date, "%Y-%m-%d")
        response = requests.get('https://api.exchangeratesapi.io/history?start_at={}&end_at={}&base={}&symbols={}'.format(start_at, end_at, base, symbols)).json()
        # if not get response return massage
        if len(response['rates']) == 0:
            await bot.sendMessage(msg['from']['id'], 'No exchange rate data is available for the selected currency')
        else:
            # call create graph function from helper
            graph = create_graph(response['rates'], symbols)
            if graph:
                # send graph
                with open(graph, 'rb') as g:
                    await bot.sendPhoto(msg['from']['id'], (graph, g))
                os.remove(graph)
            else:
                await bot.sendMessage(msg['from']['id'], 'Something go wrong please try again later')
    # if user add any unrecognized command send list of commands
    else:
        massage = "Dear user please choose one from next commands:\n/list\nto get list of all currency\n/exchange " \
                  "$10 to CAD or /exchange 10 USD to CAD\nto exchange some currency\n/history USD/CAD for 7 days\n" \
                  "to get history of some currency for last 7 days"
        await bot.sendMessage(msg['from']['id'], massage)

TOKEN = TOKEN
bot = telepot.aio.Bot(TOKEN)
loop = asyncio.get_event_loop()
loop.create_task(MessageLoop(bot, handle).run_forever())
answerer = telepot.aio.helper.Answerer(bot)
print('listening ...')
loop.run_forever()