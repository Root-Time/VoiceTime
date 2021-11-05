import json

import yaml
import sqlite3

client = None


# TODO put Everything in Database
# Emergency Solution
def get_client(_client):
    global client
    client = _client


def dict_factory(cursor, row):
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return d


con = sqlite3.connect('Data/database.db')
con.row_factory = dict_factory
cur = con.cursor()


# cursor.execute(f"INSERT INTO server_setting VALUES ('{410475041277345853}', '{881237546040979486}',
# '{881237546909184020}','{902263339990794261}','{902263379413041153}','{881237752920801342}','{True}','de')")

def _ss(guild_id):
    cur.execute('SELECT * FROM server_setting WHERE id = \'{}\''.format(guild_id))
    return cur.fetchone()


def us(user_id):
    cur.execute('SELECT * FROM user_setting WHERE id = \'{}\''.format(user_id))


with open('Data/server_config.yaml', 'r') as f:
    ss = yaml.load(f, Loader=yaml.FullLoader)

with open('Data/friend_list.yaml', 'r') as f:
    fl = yaml.load(f, Loader=yaml.FullLoader) or {}

with open('Data/user.yaml', 'r') as f:
    us = yaml.load(f, Loader=yaml.FullLoader) or {}

voice = {}


# TODO CONVERT TO DATABASE
def saved_voice(_id, _voice):
    with open('Data/voice.json', 'r') as fr:
        voices = json.load(fr)

    voices[_id] = _voice

    with open('Data/voice.json', 'w') as fw:
        json.dump(voices, fw)



temp_guild = {}
