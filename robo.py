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
                # Captura o texto da mensagem recebida para o robô ler
                texto_recebido = ""
                mensagem_dados = dados.get('data', {}).get('message', {})
                if 'extendedTextMessage' in mensagem_dados:
                    texto_recebido = mensagem_dados['extendedTextMessage'].get('text', '')
                elif 'conversation' in mensagem_dados:
                    texto_recebido = mensagem_dados.get('conversation', '')
                
                mensagem = texto_recebido.lower()
                
                # Lógica de respostas do Jubileu
                if "taxa" in mensagem or "bairro" in mensagem or "entrega" in mensagem or "capão" in mensagem or "quilombo" in mensagem:
                    texto_resposta = "🛵 Entregamos em toda Nova Serrana e Capão com taxa de R$ 2,00.\nPara o Quilombo do Gaia, a taxa é R$ 5,00."
                elif "pedido" in mensagem or "açaí" in mensagem or "acai" in mensagem or "chocolate" in mensagem:
                    texto_resposta = "Pode me mandar o seu pedido por aqui mesmo (texto ou áudio)! 😋\n\nSe preferir, também pode usar nosso cardápio digital: https://jubilu-delivery.streamlit.app/"
                else:
                    texto_resposta = "Olá! 🪿 Aqui é o Jubileu!\n\nVocê prefere fazer o pedido pelo nosso site ou mandar por aqui mesmo (texto/áudio)?\n\n📲 Cardápio digital: https://jubilu-delivery.streamlit.app/\n\n(Digite *taxa* para ver os locais e valores de entrega)."

                # Prepara e envia a resposta
                url_envio = f"{API_URL}/message/sendText/{NOME_INSTANCIA}"
                headers = {"apikey": API_KEY, "Content-Type": "application/json"}
                payload = {
                    "number": remetente,
                    "text": texto_resposta
                }
                
                resposta = requests.post(url_envio, json=payload, headers=headers)
                print(f"Tentativa de envio -> Status: {resposta.status_code} | Resposta da API: {resposta.text}")
                
    except Exception as e:
        print("🚨 ERRO NO CÓDIGO:", e)

    return "OK", 200

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
