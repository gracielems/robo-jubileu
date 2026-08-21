from flask import Flask, request

app = Flask(__name__)

@app.route("/webhook", methods=["POST"])
def receber_mensagem():
    dados = request.json
    print("Nova mensagem do cliente:", dados)
    
    # É aqui que vamos colocar a lógica para responder automaticamente 
    # com o cardápio de açaí e chocolate quente do Delivery Jubileu!
    
    return "OK", 200

if __name__ == "__main__":
    print("Robô do Jubileu rodando na porta 5000...")
    app.run(port=5000)