from flask import Flask, request
import os
import sys

# Add the current directory to path so it can find your other scripts
sys.path.append(os.path.dirname(__file__))

app = Flask(__name__)

@app.route("/", defaults={"path": ""})
@app.route("/<path:path>")
def catch_all(path):
    # This is a placeholder. 
    # To show your REAL app, you need to import your main function here.
    return "Agentic OCR is Active. Path reached: " + path

# Vercel needs this variable
handler = app

