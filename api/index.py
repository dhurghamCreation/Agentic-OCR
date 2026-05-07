from flask import Flask, jsonify, request
import os
import sys

# Crucial: This lets this file "see" your other scripts in the main folder
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

app = Flask(__name__)

@app.route("/")
def home():
    # This is the landing page. 
    # You can return HTML here or just a status report.
    return """
    <html>
        <head><title>Agentic OCR</title></head>
        <body style="font-family: sans-serif; text-align: center; padding-top: 50px;">
            <h1>?? Agentic OCR Engine is LIVE</h1>
            <p>Status: <span style="color: green;">Online</span></p>
            <p>Ready to process documents.</p>
        </body>
    </html>
    """

@app.route("/process", methods=["POST"])
def process():
    # This is where you would call your extractor logic
    # Example: import extractor; return extractor.process_image(request.files["image"])
    return jsonify({"message": "Processing endpoint ready"})

handler = app

