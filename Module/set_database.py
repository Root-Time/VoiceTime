import json

# TODO CONVERT TO DATABASE
import yaml

from Module.get_database import voice_backups, fl


def create_voice_backup(vc_id, voice_backup):
    voice_backups[vc_id] = voice_backup
    with open('Data/voice.json', 'w') as f:
        json.dump(voice_backups, f)


def update_voice_backup(vc_id, update_param, value):
    if vc_id not in voice_backups.keys():
        return
    voice_backups[vc_id][update_param] = value

    with open('Data/voice.json', 'w') as f:
        json.dump(voice_backups, f)


def update_fl():
    with open('Data/friend_list', 'w') as f:
        yaml.dump(fl, f)


def delete_voice_backup(vc_id):
    if str(vc_id) in voice_backups.keys():
        del voice_backups[str(vc_id)]
    with open('Data/voice.json', 'w') as f:
        json.dump(voice_backups, f)
