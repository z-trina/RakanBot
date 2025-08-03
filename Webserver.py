#Webserver to trick render into thinking the bot is a webservice so we can use the free tier

from flask import Flask
from threading import Thread

app = Flask('')

@app.route('/')
def home():
    return "Discord bot ok"

def run():
    app.run(host='0.0.0.0', port=8080)

def keep_alive():
    t = Thread(target=run)
    t.start()
