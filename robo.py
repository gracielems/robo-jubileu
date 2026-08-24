from flask import Flask, request
import requests
import os

app = Flask(__name__)

# --- PREENCHA COM SEUS DADOS ---
API_URL = "https://evolution-api-jubileu.onrender.com"
API_KEY = "JubileuForte123!"
NOME_INSTANCIA = "jubileu2" 
# -------------------------------

@app.route("/webhook", methods=["POST"])
def receber_mensagem():
    dados = request.json
    print("Mensagem recebida do WhatsApp:", dados)
    
    try:
        if dados.get('event') == 'messages.upsert':
            remetente = dados['data']['key']['remoteJid']
            enviado_por_mim = dados['data']['key']['fromMe']
            
            if not enviado_por_mim:
                url_envio = f"{API_URL}/message/sendText/{NOME_INSTANCIA}"
                headers = {"apikey": API_KEY, "Content-Type": "application/json"}
                payload = {
                    "number": remetente,
                    "text": "Olá! 🐦 Aqui é o Jubileu! Nosso cardápio:\n\n🍧 Açaí no capricho\n☕ Chocolate Quente especial\n\nO que vai ser hoje?"
                }
                
                resposta = requests.post(url_envio, json=payload, headers=headers)
                print(f"Tentativa de envio -> Status: {resposta.status_code} | Resposta da API: {resposta.text}")
                
    except Exception as e:
        print("🚨 ERRO NO CÓDIGO:", e)

    return "OK", 200

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
