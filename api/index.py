from flask import Flask, request, jsonify
import os
import sys

# This tells the API where your other files are
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

app = Flask(__name__)

@app.route("/")
def home():
    return """
    <html>
        <body style="font-family:sans-serif; text-align:center; padding:50px;">
            <h1>?? Agentic OCR Workspace</h1>
            <p>Upload an image to let the AI Agent extract data.</p>
            <form action="/upload" method="post" enctype="multipart/form-data">
                <input type="file" name="file">
                <input type="submit" value="Analyze Image">
            </form>
        </body>
    </html>
    """

@app.route("/upload", methods=["POST"])
def upload():
    # This is where you call your REAL extractor code
    # Example: import extractor; return extractor.process(request.files["file"])
    return "Image received! (Logic connection in progress...)"

handler = app

