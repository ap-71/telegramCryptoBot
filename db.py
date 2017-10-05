import sqlite3
from misc import db_name


global dict_answer
dict_answer = {
    'check': {
        0: 'ОК - запись есть в базе',
        1: 'Error - такой записи нет в базе',
    },
    'add': {
        1: 'ОК - запись успешно добавлена в базу',
        0: 'Error - такая запись уже есть в базе',
        2: 'Произошла ошибка записи'
    }
}


def query_to_db_many(name_query):
    result = []
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()
    for i in name_query:
        cursor.execute(i)
        result.append(cursor.fetchall()[0])
    conn.close()
    return result


def query_to_db(query_to_base):
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()
    cursor.execute(query_to_base)
    result = cursor.fetchall()
    conn.close()
    return result


def check_record_in_db(name_db, name):
    temp = query_to_db("SELECT count(*) FROM {} WHERE name='{}'".format(name_db, name))
    if temp[0][0] >= 1:
        return 1
    else:
        return 0


def add_to_db(name_db, name, value):
    add = 'add'
    global dict_answer
    temp = check_record_in_db(name_db, name)
    if temp != 1:
        conn = sqlite3.connect(db_name)
        cursor = conn.cursor()
        cursor.execute("INSERT INTO " + str(name_db) + " (name,value) VALUES ('" + str(name) + "','" + str(value) + "')")
        conn.commit()
        conn.close()
    else:
        return dict_answer[add][0]
    temp_check = check_record_in_db(name_db, name)
    return dict_answer[add][temp_check]


def get_text_from_menu(table):
    temp_text = query_to_db("SELECT * FROM "+str(table))
    result = ''
    for i in temp_text:
        result = result + str(i[0]) + ' ' + str(i[1]) + '\n'
    return result


config = {
        'pool': '',
        'pool_api_url': '',
        'workers': '',
        'miners': '',
        'course': ''
    }
temp_config = {}

test = "SELECT * FROM config WHERE name=({})".format("SELECT pool FROM user_wallet WHERE name='267064781'")


tt = query_to_db(test)
y = 0
for iii in config:
    temp_config[y] = iii
    y = y + 1
print(temp_config)
y = 0
for ii in tt[0]:

    config[temp_config[y]] = ii
    y = y + 1

print(config['pool'])
