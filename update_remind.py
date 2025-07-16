import requests
import os
import smtplib
from email.mime.text import MIMEText
from email.utils import formatdate

WATCH_LIST = [
    {"ncode": "NN8760EI", "title": "異世界黙示録マイノグーラ"},
]
