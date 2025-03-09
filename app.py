from flask import Flask, request, jsonify, render_template
from openai import OpenAI
import os
import time
import requests
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

app = Flask(__name__)

# Configuration from environment variables
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "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")
DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY", "sk-50fb68a091ff437d91a9689f34894201")

# Initialize clients
openai_client = OpenAI(api_key=OPENAI_API_KEY)

def handle_errors(func):
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            return f"Error: {str(e)}"
    return wrapper

@handle_errors
def ask_openai(prompt):
    response = openai_client.chat.completions.create(
        model="gpt-4-turbo",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.7,
        max_tokens=1000
    )
    return response.choices[0].message.content

@handle_errors
def ask_deepseek(prompt):
    headers = {
        "Authorization": f"Bearer {DEEPSEEK_API_KEY}",
        "Content-Type": "application/json"
    }
    data = {
        "model": "deepseek-chat",
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.7,
        "max_tokens": 1000
    }
    response = requests.post(
        "https://api.deepseek.com/v1/chat/completions",
        headers=headers,
        json=data,
        timeout=30
    )
    return response.json()['choices'][0]['message']['content']

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/ask", methods=["POST"])
def handle_query():
    data = request.get_json()
    prompt = data.get("prompt", "")
    model = data.get("model", "openai")

    if not prompt:
        return jsonify({"error": "Empty prompt"}), 400

    start_time = time.time()
    
    try:
        if model == "openai":
            response = ask_openai(prompt)
        elif model == "deepseek":
            response = ask_deepseek(prompt)
        else:
            return jsonify({"error": "Invalid model"}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500

    processing_time = round(time.time() - start_time, 2)

    return jsonify({
        "response": response,
        "processing_time": processing_time,
        "model": model.upper()
    })

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, debug=True)