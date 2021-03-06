import json

import yaml

client = None


# TODO put Everything in Database
# Emergency Solution
def get_client(_client):
    global client
    client = _client


with open('Data/server_config.yaml', 'r') as f:
    ss = yaml.load(f, Loader=yaml.FullLoader)

with open('Data/friend_list.yaml', 'r') as f:
    fl = yaml.load(f, Loader=yaml.FullLoader) or {}

with open('Data/user.yaml', 'r') as f:
    us = yaml.load(f, Loader=yaml.FullLoader) or {}

with open('Data/voice.json', 'r') as f:
    voice_backups = json.load(f) or {}

with open('Data/block.json', 'r') as f:
    bl = json.load(f) or {}

with open('Data/admins.yaml', 'r') as f:
    admins = yaml.load(f, Loader=yaml.FullLoader).get('Admin', {})


# Temp Data
voice = {}
temp_guild = {}
owner_vc_list = {}
