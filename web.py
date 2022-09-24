import flask
from threading import Thread

app = flask.Flask('')

@app.route('/') 
def home():
  return "I'm alive"

def open_web():
  t = Thread(target=lambda: app.run("0.0.0.0", 8080), daemon=True)
  t.start()