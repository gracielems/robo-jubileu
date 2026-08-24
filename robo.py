from flask import Flask, request
import requests
import os
import google.generativeai as genai

app = Flask(__name__)

# --- PREENCHA COM SEUS DADOS ---
API_URL = "https://evolution-api-jubileu.onrender.com"
API_KEY_EVO = "JubileuForte123!"
NOME_INSTANCIA = "jubileu2" 
GEMINI_API_KEY = "COLE_SUA_CHAVE_AQUI" # <-- Cole sua chave do Google aqui
# -------------------------------

# Configura a inteligência do Google
genai.configure(api_key=GEMINI_API_KEY)

# Configura o cérebro do Jubileu
instrucoes_sistema = """Você é o Jubileu, o simpático mascote e atendente virtual do 'Delivery Jubileu' em Nova Serrana. 
Seu objetivo é atender os clientes pelo WhatsApp, anotar pedidos (como copos de açaí de 700ml, 500ml, chocolate quente, etc), tirar dúvidas e fechar a venda.
- Cardápio digital: https://jubilu-delivery.streamlit.app/
- Taxas: Toda Nova Serrana e Capão (R$ 2,00). Quilombo do Gaia (R$ 5,00).
- Passo a passo: 1. Confirme os itens. 2. Liste o resumo. 3. Pergunte a forma de pagamento (Pix, Cartão ou Dinheiro). 4. Pergunte o endereço.
Seja amigável, natural e use emojis 🪿🍧☕."""

model = genai.GenerativeModel(
    model_name="gemini-1.5-flash",
    system_instruction=instrucoes_sistema
)

# Memória de chat por cliente
chats = {}

@app.route("/webhook", methods=["POST"])
def receber_mensagem():
    dados = request.json
    
    try:
        if dados.get('event') == 'messages.upsert':
            remetente = dados['data']['key']['remoteJid']
            enviado_por_mim = dados['data']['key']['fromMe']
            
            if not enviado_por_mim:
                # Ignora grupos
                if "@g.us" in remetente:
                    return "OK", 200
                    
                texto_recebido = ""
                mensagem_dados = dados.get('data', {}).get('message', {})
                if 'extendedTextMessage' in mensagem_dados:
                    texto_recebido = mensagem_dados['extendedTextMessage'].get('text', '')
                elif 'conversation' in mensagem_dados:
                    texto_recebido = mensagem_dados.get('conversation', '')
                
                if texto_recebido:
                    # Cria ou recupera o histórico da conversa com esse cliente
                    if remetente not in chats:
                        chats[remetente] = model.start_chat(history=[])
                    
                    chat = chats[remetente]
                    resposta_ia = chat.send_message(texto_recebido)
                    texto_resposta = resposta_ia.text

                    # Envia de volta para o WhatsApp via Evolution API
                    url_envio = f"{API_URL}/message/sendText/{NOME_INSTANCIA}"
                    headers = {"apikey": API_KEY_EVO, "Content-Type": "application/json"}
                    payload = {
                        "number": remetente,
                        "text": texto_resposta
                    }
                    
                    requests.post(url_envio, json=payload, headers=headers)
                    
    except Exception as e:
        print("🚨 ERRO NO CÓDIGO:", e)

    return "OK", 200

if __name__ == "__main__":
    port = int(os.environ.com.get("PORT", 5000) if hasattr(os, "environ") else 5000)
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
