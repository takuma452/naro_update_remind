from flask import Flask, render_template
from apscheduler.schedulers.background import BackgroundScheduler
from notifier import check_updates

app = Flask(__name__)

# 定期実行ジョブ
scheduler = BackgroundScheduler()
scheduler.add_job(func=check_updates, trigger="interval", minutes=30)  # 30分おき
scheduler.start()

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/check")
def check():
    result = check_updates()
    return f"手動チェック完了！\n{result}"

if __name__ == "__main__":
    app.run()
