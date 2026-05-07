from flask import Flask, render_template_string
import os

app = Flask(__name__)

@app.route("/")
def dashboard():
    return """
    <html>
        <head>
            <title>Agentic OCR Dashboard</title>
            <style>
                body { font-family: "Segoe UI", sans-serif; background: #f4f7f6; margin: 0; display: flex; }
                .sidebar { width: 250px; background: #2c3e50; color: white; height: 100vh; padding: 20px; }
                .main { flex-grow: 1; padding: 40px; }
                .card { background: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
                .btn { background: #3498db; color: white; padding: 10px 20px; border: none; border-radius: 4px; cursor: pointer; }
            </style>
        </head>
        <body>
            <div class="sidebar">
                <h2>OCR AI</h2>
                <p>?? Dashboard</p>
                <p>?? History</p>
                <p>?? Settings</p>
            </div>
            <div class="main">
                <h1>Agentic OCR Dashboard</h1>
                <div class="card">
                    <h3>Upload New Document</h3>
                    <input type="file">
                    <button class="btn">Start Extraction</button>
                </div>
            </div>
        </body>
    </html>
    """

handler = app

