from flask import Flask
import os

app = Flask(__name__)

@app.route("/")
def home():
    return """
    <div style="font-family:sans-serif; text-align:center; margin-top:100px;">
        <h1 style="color:#0070f3;">?? AGENTIC OCR IS LIVE</h1>
        <p>If you see this, the deployment is 100% working.</p>
        <hr style="width:200px">
        <p>Current Directory: {}</p>
    </div>
    """.format(os.getcwd())

handler = app

