import json
import os

conf = json.load(open(os.path.join(os.path.dirname(__file__), '..', 'moon_config.json')))


def mail_user() -> str:
    return str(conf['mail-user'])


def mail_pwd() -> str:
    return str(conf['mail-pwd'])


def mail_receiver() -> str:
    return str(conf['mail-receiver'])


def mail_server_smtp_adr() -> str:
    return str(conf['mail-server-smtp-adr'])


def mail_server_smtp_port() -> int:
    return int(conf['mail-server-smtp-port'])


def mail_from() -> str:
    return str(conf['mail-from'])


def mail_to() -> str:
    return str(conf['mail-to'])
