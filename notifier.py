import requests
import os
import smtplib
from email.mime.text import MIMEText
from email.utils import formatdate
import json

FROM_ADDR = os.getenv("FROM_ADDR")
PASSWORD = os.getenv("GMAIL_PASS")
TO_ADDR = os.getenv("TO_ADDR")

def get_novel_info(novel_id):
    url = f"https://api.syosetu.com/novelapi/api/?out=json&ncode={novel_id}"
    response = requests.get(url)
    return response.json()

def get_last_saved_update_time(filename):
    if not os.path.exists(filename):
        return None
    with open(filename, "r") as f:
        return f.read().strip()

def save_update_time(filename, update_time):
    with open(filename, "w") as f:
        f.write(update_time)

def send_email(subject, body, to_addr):
    smtp_host = "smtp.gmail.com"
    smtp_port = 587

    msg = MIMEText(body, "plain", "utf-8")
    msg["Subject"] = subject
    msg["From"] = FROM_ADDR
    msg["To"] = to_addr
    msg["Date"] = formatdate()

    server = smtplib.SMTP(smtp_host, smtp_port)
    server.starttls()
    server.login(FROM_ADDR, PASSWORD)
    server.send_message(msg)
    server.quit()

def check_updates():
    with open("watch_list.json", "r", encoding="utf-8") as f:
        ncodes = json.load(f)

    result = []
    for ncode in ncodes:
        info = get_novel_info(ncode)
        title = info[1]['title']
        lastup = info[1]['general_lastup']
        filename = f"last_update_{ncode}.txt"

        last_saved = get_last_saved_update_time(filename)

        if last_saved is None:
            save_update_time(filename, lastup)
            result.append(f"{title} 初回保存")
            continue

        if lastup > last_saved:
            subject = f"【なろう更新通知】『{title}』が更新されました！"
            body = f"『{title}』が更新されました！\n最新更新日時: {lastup}\nhttps://ncode.syosetu.com/{ncode.lower()}/"
            send_email(subject, body, TO_ADDR)
            save_update_time(filename, lastup)
            result.append(f"{title} 更新あり → メール送信")
        else:
            result.append(f"{title} 更新なし")

    return "\n".join(result)
