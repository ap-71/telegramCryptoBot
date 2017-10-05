from time import sleep
import requests
import misc
from db import get_text_from_menu, add_to_db, check_record_in_db, query_to_db
from pools import ethermine

token = misc.token
URL = 'https://api.telegram.org/bot' + token + '/'

global last_update_id
global commands
global dict_comm
last_update_id = 0

dict_comm = ''


def get_updates():
    url = URL + 'getupdates'
    r = requests.get(url)
    return r.json()


def check_get(update_id):
    url = URL + 'getupdates?offset=' + update_id
    requests.get(url)


def get_message():
    sleep(5)
    data = get_updates()
    print(data)
    last_object = data['result'][-1]
    update_id = last_object['update_id']
    global last_update_id
    if last_update_id != update_id:
        last_update_id = update_id
        user_id = last_object['message']['from']['id']
        user_full_name = str(last_object['message']['from']['first_name']) + ' ' + str(
            last_object['message']['from']['last_name'])
        chat_id = last_object['message']['chat']['id']
        message_text = last_object['message']['text']
        message = {'chat_id': chat_id,
                   'message_text': message_text,
                   'user_id': user_id,
                   'user_full_name': user_full_name
                   }
        check_get(str(update_id))
        return message
    return None


def send_message(chat_id, text='Необходимо подождать некоторое время...'):
    url = URL + 'sendmessage?chat_id={}&text={}'.format(chat_id, text)
    requests.get(url)


def update_user_info(chat_id, temp_user_id, temp_full_name, button=0):
    if check_record_in_db('user_wallet', temp_user_id) != 0:
        if button == 1:
            send_message(chat_id, 'Здравствуйте, ' + temp_full_name.upper() + '\n' + dict_comm)
        out_text_wallet = query_to_db("SELECT value FROM user_wallet WHERE name='{}'".format(temp_user_id))
        return out_text_wallet
    else:
        send_message(chat_id,
                     'Такого пользователя нет!\n При первом запуске бота, необходима ввести корректный номер кошелька ETH(без первых 2х символов - 0x). Если кошелек введен неверно, необходимо обратиться в личку к: @aleksandr_panarin')
        send_message(chat_id, 'Добавить(y)?')
        ff = 0
        while ff == 0:
            sleep(2)
            get_temp_main = get_message()
            if get_temp_main != None:
                message = get_temp_main['message_text']
                if message == 'да' or message == 'Да' or message == 'yes' or message == 'Yes' or message == 'y' or message == 'Y':
                    send_message(chat_id, 'Номер кошелька(вводится без 0x): ')
                    while ff == 0:
                        sleep(2)
                        get_temp = get_message()

                        if get_temp != None:
                            y = [['']]
                            message_wall = get_temp['message_text']
                            send_message(chat_id, add_to_db('user_wallet', temp_user_id, message_wall))
                            y[0][0] = message_wall

                            return y


def display_info(conf_dict, chat_id, text, namber_wallet):
    tttt = ''
    pool_api_url = conf_dict['pool_api_url']
    pool = conf_dict['pool']
    commands_api = conf_dict['workers']
    json_api_price = conf_dict['course']
    try:
        Workers, HR = ethermine.get_workers_and_HR(pool_api_url, namber_wallet, pool, commands_api)
        HR = round(HR, 2)
        upb = get_coin_information(pool_api_url, namber_wallet, pool, json_api_price)
        if text == '/workers':
            for rr in Workers:
                tttt = tttt + rr + '\n'
            send_message(chat_id, 'Воркеры: \n' + str(tttt) + '\n Общий хэш-рейт: ' + str(HR) + ' MH/s')

            tttt = ''
        else:
            USD_BTC_RUR = ethermine.get_USD_BTC(json_api_price, pool)
            if text == '/all':
                for rr in Workers:
                    tttt = tttt + rr + '\n'
                send_message(chat_id, 'ВОРКЕРЫ: \n' + str(tttt) + '\n Общий хэш-рейт: ' + str(
                    HR) + ' MH/s \n \n' + 'КУРСЫ ETH/USD, ETH/BTC, ETH/RUR: \nETH/USD: ' + str(
                    USD_BTC_RUR['usd']) + '\n' + 'ETH/BTC: ' + str(USD_BTC_RUR['btc'])+ '\n' + 'ETH/RUR: ' + str(USD_BTC_RUR['rur']) + '\n\nОЖИДАЕМАЯ ВЫПЛАТА: \n' + upb)
                tttt = ''

            if text == '/course':
                send_message(chat_id, 'КУРСЫ ETH/USD, ETH/BTC, ETH/RUR: \nETH/USD: ' + str(USD_BTC_RUR['usd']) + '\n' + 'ETH/BTC: ' + str(USD_BTC_RUR['btc'])+ '\n' + 'ETH/RUR: ' + str(USD_BTC_RUR['rur']))
            if text == '/up':
                send_message(chat_id, upb)
    except:
        send_message(chat_id)


def get_coin_information(url, wall, pool, json_api_price):
    eth = ethermine.get_coins_info(url, wall, pool)
    USD_BTC_RUR = ethermine.get_USD_BTC(json_api_price, pool)
    temptemp = ''
    courses_coin = {
        'Ethereum - невыплаченный баланс: ': eth,
        'ETH->USD: ': round(eth * float(USD_BTC_RUR['usd']), 2),
        'ETH->BTC: ': round(eth * float(USD_BTC_RUR['btc']), 4),
        'ETH->RUR: ': round(eth * float(USD_BTC_RUR['rur']), 2)
    }
    for gg in courses_coin:
        temptemp = temptemp + gg + str(courses_coin[gg]) + '\n'
    return temptemp


def start():
    x = 0
    y = 0
    global commands
    global dict_comm
    dict_comm = get_text_from_menu('query_commands')
    config = {
        'pool': '',
        'pool_api_url': '',
        'workers': '',
        'miners': '',
        'course': ''
    }
    temp_config = {}

    for iii in config:
        temp_config[y] = iii
        y = y + 1

    while True:
        try:
            answer = get_message()
            if answer != None:
                y = 0
                chat_id = answer['chat_id']
                temp = "SELECT * FROM config WHERE name=({})".format(
                    "SELECT pool FROM user_wallet WHERE name='{}'".format(answer['user_id']))
                temp_result = query_to_db(temp)
                for ii in temp_result[0]:
                    config[temp_config[y]] = ii
                    y = y + 1

                if x != 1:
                    text = '/start'
                    x = 1
                else:
                    text = answer['message_text']

                updating_info = str(update_user_info(chat_id, answer['user_id'], answer['user_full_name'])[0][0])
                if text == '/start':
                    update_user_info(chat_id, answer['user_id'], answer['user_full_name'], 1)[0][0]
                if text == '/workers' or text == '/all' or text == '/course' or text == '/up':
                    display_info(config, chat_id, text, updating_info)

            else:
                continue
        except:
            print('error')


def main():
    start()


if __name__ == '__main__':
    main()
