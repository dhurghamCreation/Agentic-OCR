from flask import Flask
import os
import sys

# This allows api/index.py to see your files in the folder above it
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# --- IMPORT YOUR REAL CODE HERE ---
# import extractor 
# ----------------------------------

app = Flask(__name__)

@app.route("/")
def home():
    # Example: call a function from your real code
    # result = extractor.run_analysis()
    return "<h1>Your Agentic OCR is ready to work!</h1>"

handler = app