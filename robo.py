import os
from flask import Flask, request

app = Flask(__name__)

@app.route("/webhook", methods=["POST"])
def receber_mensagem():
    dados = request.json
    print("Nova mensagem do cliente:", dados)
    return "OK", 200

if __name__ == "__main__":
    porta = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=porta)
