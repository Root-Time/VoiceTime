import json


def language(text, l="de") -> str:
    with open("Data/language.json", 'r') as f:
        voice_file = json.load(f)
    if not voice_file:
        voice_file = {}
    if text not in voice_file.keys():
        voice_file[text] = {'de': text}

    with open("Data/language.json", 'w') as f:
        json.dump(voice_file, f, indent=4)

    if not voice_file[text].get(l, None):
        return voice_file[text]['de']  # Change to en

    return voice_file[text][l]
