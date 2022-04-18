import json

conf = json.load(open('moon_config.json'))

def get_mail_user() -> str:
    return conf

