from flask import Flask, request
import requests
import os

app = Flask(__name__)

# --- PREENCHA COM SEUS DADOS ---
API_URL = "https://evolution-api-jubileu.onrender.com"
API_KEY_EVO = "JubileuForte123!"
NOME_INSTANCIA = "jubileu2" 
GEMINI_API_KEY = "AIzaSyBdLx666oye0YelPGl0-IubawNTbh0b-2M" # <-- Cole sua chave do Google aqui e mantenha as aspas!
# -------------------------------

historico_conversas = {}

def consultar_gemini(remetente, mensagem):
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={GEMINI_API_KEY}"
    
    instrucoes = """Você é o Jubileu, o simpático mascote e atendente virtual do 'Delivery Jubileu' em Nova Serrana. 
    Seu objetivo é atender os clientes pelo WhatsApp, anotar pedidos (como copos de açaí de 700ml, 500ml, chocolate quente, etc), tirar dúvidas e fechar a venda.
    - Cardápio digital: https://jubilu-delivery.streamlit.app/
    - Taxas: Toda Nova Serrana e Capão (R$ 2,00). Quilombo do Gaia (R$ 5,00).
    - Passo a passo: 1. Confirme os itens. 2. Liste o resumo. 3. Pergunte a forma de pagamento (Pix, Cartão ou Dinheiro). 4. Pergunte o endereço.
    Seja amigável, natural e use emojis 🪿🍧☕."""

    if remetente not in historico_conversas:
        historico_conversas[remetente] = []
    
    historico_conversas[remetente].append({"role": "user", "parts": [{"text": mensagem}]})
    
    # Formato corrigido para o Google Gemini
    payload = {
        "systemInstruction": {"parts": [{"text": instrucoes}]},
        "contents": historico_conversas[remetente]
    }
    
    try:
        resposta = requests.post(url, json=payload, headers={"Content-Type": "application/json"})
        dados = resposta.json()
        
        # Extrai a resposta
        texto_ia = dados['candidates'][0]['content']['parts'][0]['text']
        
        # Salva na memória
        historico_conversas[remetente].append({"role": "model", "parts": [{"text": texto_ia}]})
        return texto_ia
    except Exception as e:
        print("Erro no Gemini:", e)
        # Se der erro, imprime a resposta do Google no log do Render para sabermos o motivo
        print("Detalhes:", resposta.text if 'resposta' in locals() else "Sem resposta")
        return "Ops! Dei uma engasgada aqui. Pode repetir o que você disse, por favor? 🪿"

@app.route("/webhook", methods=["POST"])
def receber_mensagem():
    dados = request.json
    
    try:
        if dados.get('event') == 'messages.upsert':
            remetente = dados['data']['key']['remoteJid']
            enviado_por_mim = dados['data']['key']['fromMe']
            
            if not enviado_por_mim:
                if "@g.us" in remetente:
                    return "OK", 200
                    
                texto_recebido = ""
                mensagem_dados = dados.get('data', {}).get('message', {})
                if 'extendedTextMessage' in mensagem_dados:
                    texto_recebido = mensagem_dados['extendedTextMessage'].get('text', '')
                elif 'conversation' in mensagem_dados:
                    texto_recebido = mensagem_dados.get('conversation', '')
                
                if texto_recebido:
                    resposta_inteligente = consultar_gemini(remetente, texto_recebido)

                    url_envio = f"{API_URL}/message/sendText/{NOME_INSTANCIA}"
                    headers = {"apikey": API_KEY_EVO, "Content-Type": "application/json"}
                    payload = {
                        "number": remetente,
                        "text": resposta_inteligente
                    }
                    
                    requests.post(url_envio, json=payload, headers=headers)
                    
    except Exception as e:
        print("🚨 ERRO NO CÓDIGO:", e)

    return "OK", 200

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
