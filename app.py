# importando 
from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy

# passando a instancia e a variavel 
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///ecommerce.db'

db = SQLAlchemy(app)

# Modelagem do BD
class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True) # Coluna 1, com identificador unico
    name = db.Column(db.String(120), nullable=False) #Não permite enviar vazio
    price = db.Column(db.Float, nullable=False)
    description = db.Column(db.Text, nullable=True) #Permite enviar vazio

@app.route('/api/product/add', methods=["POST"])
def create_product():
    data = request.json
    if 'name' in data and 'price' in data: #Verificando se ta enviando com essas informações
        product = Product(name=data['name'], price=data['price'], description=data.get("description", "")) #Parametrizando o que vai receber 
        db.session.add(product) # adiciona no banco
        db.session.commit() # envia pro banco
        return jsonify({"message": "Produto cadastrado com sucesso"}) 
    
    return jsonify({"message": "Dados do produto invalidos"}), 400 #Se enviar sem informação, vai mandar essa mensagem 


@app.route('/api/product/delete/<int:product_id>', methods=["DELETE"])
def delete_product(product_id):
    product = Product.query.get(product_id)#Busca o produto na tabela pelo id
    if product: #Verifica se existe 
        db.session.delete(product)#Se ele existe = delete
        db.session.commit()#envia
        return jsonify({"message": "Produto deletado com sucesso"}) 
    
    return jsonify({"message": "Dados do produto invalidos"}), 404



# definir uma rota raiz (pagina inicial) e a função executada ao requisitar
@app.route('/')
def hello_world():
    return 'Hello World'

if __name__ == "__main__":
    app.run(debug=True)