from flask import Flask
from threading import Thread

app = Flask("")

@app.route("/")
def index():
    return "Hello from Flask"

def run():
    # Desactiva el reloader y debug para que arranque en este mismo hilo
    app.run(host="0.0.0.0", port=8000, debug=False, use_reloader=False)

def keep_alive():
    Thread(target=run, daemon=True).start()
    print(">>> webserver: hilo de Flask arrancado")