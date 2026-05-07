from flask import Flask, jsonify
import sys
import os

# This tells Python to look in the parent folder for your scripts
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# --- IMPORT YOUR LOGIC HERE ---
# Example: import extractor
# ------------------------------

app = Flask(__name__)

@app.route("/")
def home():
    try:
        # Replace this with a call to your real logic
        # Example: result = extractor.run_ocr()
        return "Agentic OCR System: Ready for processing."
    except Exception as e:
        return str(e), 500

handler = app

