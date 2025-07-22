import requests
import os
import smtplib
import json
from email.mime.text import MIMEText
from email.utils import formatdate

FROM_ADDR = os.environ["FROM_ADDR"]
TO_ADDR = os.environ["TO_ADDR"]
GMAIL_PASS = os.environ["GMAIL_PASS"]

def get_novel_info(ncode):
    url = f"https://api.syosetu.com/novelapi/api/?out=json&ncode={ncode}"
    res = requests.get(url)
    return res.json()[1]

def load_last_update(ncode):
    fname = f"last_update_{ncode}.txt"
    if not os.path.exists(fname):
        return None
    with open(fname, "r") as f:
        return f.read().strip()

def save_last_update(ncode, timestamp):
    fname = f"last_update_{ncode}.txt"
    with open(fname, "w") as f:
        f.write(timestamp)

def send_email(subject, body):
    msg = MIMEText(body, "plain", "utf-8")
    msg["Subject"] = subject
    msg["From"] = FROM_ADDR
    msg["To"] = TO_ADDR
    msg["Date"] = formatdate()

    server = smtplib.SMTP("smtp.gmail.com", 587)
    server.starttls()
    server.login(FROM_ADDR, GMAIL_PASS)
    server.send_message(msg)
    server.quit()

def check_updates():
    with open("watch_list.json", "r", encoding="utf-8") as f:
        ncodes = json.load(f)

    for ncode in ncodes:
        info = get_novel_info(ncode)
        title = info["title"]
        lastup = info["general_lastup"]
        prev = load_last_update(ncode)

        if prev is None:
            print(f"{title}: 初回保存")
            save_last_update(ncode, lastup)
        elif lastup > prev:
            print(f"{title}: 更新あり！メール送信")
            body = f"『{title}』が更新されました！\n更新日時: {lastup}\nURL: https://ncode.syosetu.com/{ncode.lower()}/"
            send_email(f"[なろう更新] {title}", body)
            save_last_update(ncode, lastup)
        else:
            print(f"{title}: 更新なし")

if __name__ == "__main__":
    check_updates()
