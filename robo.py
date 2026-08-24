from flask import Flask, request
import requests
import os

app = Flask(__name__)

# --- PREENCHA COM SEUS DADOS ---
API_URL = "https://evolution-api-jubileu.onrender.com"
API_KEY_EVO = "JubileuForte123!"
NOME_INSTANCIA = "jubileu2" 
GEMINI_API_KEY = "AIzaSyBdLx666oye0YelPGl0-IubawNTbh0b-2M" # <-- Cole a chave gerada no Google AI Studio aqui!
# -------------------------------

# Memória do robô para lembrar dos pedidos de cada cliente
historico_conversas = {}

def consultar_gemini(remetente, mensagem):
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={GEMINI_API_KEY}"
    
    # Instruções de como o Jubileu deve se comportar
    instrucoes = """Você é o Jubileu, o simpático mascote e atendente virtual do 'Delivery Jubileu' em Nova Serrana. 
    Seu objetivo é atender os clientes pelo WhatsApp, anotar pedidos (como copos de açaí de 700ml, 500ml, chocolate quente, etc), tirar dúvidas e fechar a venda.
    - Cardápio digital opcional: https://jubilu-delivery.streamlit.app/
    - Bairros de entrega: Entregamos em toda Nova Serrana e no Capão com taxa de R$ 2,00. Para o Quilombo do Gaia, a taxa é R$ 5,00.
    - Regras de ouro: Seja amigável, natural, use emojis 🪿🍧☕ e responda de forma curta, como uma pessoa de verdade no WhatsApp. 
    - Passo a passo do pedido: 1. Confirme os itens. 2. Calcule o valor (se o cliente disser os preços) ou apenas liste o resumo. 3. Pergunte a forma de pagamento (Pix, Cartão ou Dinheiro). 4. Pergunte o endereço completo.
    Nunca diga que você é uma IA, você é o Jubileu!"""

    # Se é um cliente novo, cria a memória dele com as instruções
    if remetente not in historico_conversas:
        historico_conversas[remetente] = []
    
    # Adiciona a mensagem do cliente na memória
    historico_conversas[remetente].append({"role": "user", "parts": [{"text": mensagem}]})
    
    payload = {
        "system_instruction": {"parts": {"text": instrucoes}},
        "contents": historico_conversas[remetente]
    }
    
    try:
        resposta = requests.post(url, json=payload, headers={"Content-Type": "application/json"})
        dados = resposta.json()
        texto_ia = dados['candidates'][0]['content']['parts'][0]['text']
        
        # Adiciona a resposta do Jubileu na memória
        historico_conversas[remetente].append({"role": "model", "parts": [{"text": texto_ia}]})
        return texto_ia
    except Exception as e:
        print("Erro no Gemini:", e)
        return "Ops! Dei uma engasgada aqui. Pode repetir o que você disse, por favor? 🪿"

@app.route("/webhook", methods=["POST"])
def receber_mensagem():
    dados = request.json
    
    try:
        if dados.get('event') == 'messages.upsert':
            remetente = dados['data']['key']['remoteJid']
            enviado_por_mim = dados['data']['key']['fromMe']
            
            if not enviado_por_mim:
                # Trava para ignorar mensagens de grupos
                if "@g.us" in remetente:
                    return "OK", 200
                    
                texto_recebido = ""
                mensagem_dados = dados.get('data', {}).get('message', {})
                if 'extendedTextMessage' in mensagem_dados:
                    texto_recebido = mensagem_dados['extendedTextMessage'].get('text', '')
                elif 'conversation' in mensagem_dados:
                    texto_recebido = mensagem_dados.get('conversation', '')
                
                # Se houver texto, manda para a Inteligência Artificial processar
                if texto_recebido:
                    resposta_inteligente = consultar_gemini(remetente, texto_recebido)

                    # Envia a resposta final para o WhatsApp
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
