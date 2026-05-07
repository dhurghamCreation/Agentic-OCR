from flask import Flask, jsonify

app = Flask(__name__)

@app.route("/(.*)")
@app.route("/")
def home():
    return jsonify({
        "status": "online",
        "message": "Agentic OCR Engine is LIVE",
        "details": "Vercel entrypoint recognized successfully"
    })

# Your background logic can be imported here or added below

