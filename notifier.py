import os, json, requests, smtplib
from email.mime.text import MIMEText
from email.utils import formatdate

from dotenv import load_dotenv
load_dotenv()
FROM_ADDR = os.environ["FROM_ADDR"]
TO_ADDR = os.environ["TO_ADDR"]
GMAIL_PASS = os.environ["GMAIL_PASS"]

def get_novel_info(ncode):
    url = f"https://api.syosetu.com/novelapi/api/?out=json&ncode={ncode}"
    res = requests.get(url)
    return res.json()[1]

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

    if os.path.exists("last_updates.json"):
        with open("last_updates.json", "r", encoding="utf-8") as f:
            last_updates = json.load(f)
    else:
        last_updates = {}

    updated = False

    for ncode in ncodes:
        info = get_novel_info(ncode)
        title = info["title"]
        lastup = info["general_lastup"]
        prev = last_updates.get(ncode)

        if prev != lastup:
            print(f"{title}: 更新あり → メール送信")
            body = f"『{title}』が更新されました！\n更新日時: {lastup}\nURL: https://ncode.syosetu.com/{ncode.lower()}/"
            send_email(f"[なろう更新] {title}", body)
            last_updates[ncode] = lastup
            updated = True
        else:
            print(f"{title}: 更新なし")

    if updated:
        with open("last_updates.json", "w", encoding="utf-8") as f:
            json.dump(last_updates, f, ensure_ascii=False, indent=2)

    return updated

if __name__ == "__main__":
    check_updates()
