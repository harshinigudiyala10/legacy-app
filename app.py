"""app.py - a small web service standing in for your legacy VM app."""
import os
import socket
import time
from flask import Flask, jsonify
app = Flask(__name__)
APP_VERSION = os.environ.get("APP_VERSION", "4.0.0")
# In the legacy world this came from a config file edited by hand on the VM.
GREETING = os.environ.get("GREETING", "Hello World")
# A secret we will later source from Key Vault (never hard-code real secrets):
API_TOKEN = os.environ.get("API_TOKEN", "not-set")
@app.get("/")
def home():
    return jsonify(
        message=GREETING,
        version=APP_VERSION,
        served_by=socket.gethostname(),   # shows which replica answered
        token_loaded=(API_TOKEN != "not-set"),
    )
@app.get("/health")
def health():
    """Liveness/readiness probe target - cheap and dependency-free."""
    return jsonify(status="healthy"), 200
@app.get("/work")
def work():
    """Burns CPU for ~200ms so we can generate load and watch autoscaling."""
    start = time.time()
    x = 0
    while time.time() - start < 0.2:
        x += 1
    return jsonify(iterations=x, served_by=socket.gethostname())
if __name__ == "__main__":
    # 0.0.0.0 so the process is reachable from outside the container
    app.run(host="0.0.0.0", port=8000)
