# importando 
from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from flask_login import UserMixin, login_user, LoginManager, login_required,logout_user, current_user
# passando a instancia e a variavel 
app = Flask(__name__)
app.config['SECRET_KEY'] = "minha_chave"
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///ecommerce.db'

login_manager = LoginManager()
db = SQLAlchemy(app)
login_manager.init_app(app)
login_manager.login_view = 'login'
CORS(app)

class User (db.Model, UserMixin):  
    id = db.Column(db.Integer, primary_key=True)
    userName = db.Column(db.String(80), nullable=False, unique=True)
    password = db.Column(db.String(80), nullable=True)
# Modelagem do BD
class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True) # Coluna 1, com identificador unico
    name = db.Column(db.String(120), nullable=False) #Não permite enviar vazio
    price = db.Column(db.Float, nullable=False)
    description = db.Column(db.Text, nullable=True) #Permite enviar vazio
    
class CartItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)
    
    # Relacionamentos com os modelos User e Product
    user = db.relationship('User', backref=db.backref('cart_items', lazy=True))
    product = db.relationship('Product', backref=db.backref('cart_items', lazy=True))
    
#Autenticação
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))#toda vez que foi usada uma rota que tenha proteção, essa fumção busca user 

@app.route('/login', methods=["POST"])
def login():
    data = request.json
    
    user = User.query.filter_by(userName=data.get("userName")).first() #vai puxar a lista, mas com o .first vai puxar o primeiro só
    
    if user and  data.get("password") == user.password:
        login_user(user)
        return jsonify({"message": "Logado com sucesso"})# Se existir retorna
    return jsonify({"message": "Informações incorretas"}), 401

@app.route('/logout', methods = ["POST"])
@login_required 
def logout(): 
    logout_user();
    return jsonify("Logout feito com sucesso")


@app.route('/api/product/add', methods=["POST"])
@login_required #Pra usar essa rota precisa estar autenticado
def create_product():
    data = request.json 
    if 'name' in data and 'price' in data: #Verificando se ta enviando com essas informações
        product = Product(name=data['name'], price=data['price'], description=data.get("description", "")) #Parametrizando o que vai receber 
        db.session.add(product) # adiciona no banco
        db.session.commit() # envia pro banco
        return jsonify({"message": "Produto cadastrado com sucesso"}) 
    
    return jsonify({"message": "Dados do produto invalidos"}), 400 #Se enviar sem informação, vai mandar essa mensagem 


@app.route('/api/product/delete/<int:product_id>', methods=["DELETE"])
@login_required #Pra usar essa rota precisa estar autenticado
def delete_product(product_id):
    product = Product.query.get(product_id)#Busca o produto na tabela pelo id
    if product: #Verifica se existe 
        db.session.delete(product)#Se ele existe = delete
        db.session.commit()#envia
        return jsonify({"message": "Produto deletado com sucesso"}) 
    
    return jsonify({"message": "Dados do produto invalidos"}), 404

@app.route('/api/product/<int:product_id>', methods=["GET"])
def get_product_details(product_id):
    product = Product.query.get(product_id)
    if product:
        return jsonify({
            "id": product.id,
            "name": product.name,
            "price": product.price,
            "description": product.description
        }) #função do que deve retornar 
    return jsonify({"message": "Produto não encontrado"}), 404

@app.route('/api/product/update/<int:product_id>', methods=["PUT"])
@login_required #Pra usar essa rota precisa estar autenticado
def update_product(product_id):
    product = Product.query.get(product_id)
    if not product: #Se não tiver nada, vai retornar isso
         return jsonify({"message": "Produto não encontrado"}), 404
     
    data = request.json
    if 'name' in data:
        product.name = data['name'] 
    if 'price' in data:
        product.price = data['price']
    if 'description' in data:
        product.description = data['description']
        
        db.session.commit()#obrigatorio para atualizar no bd
    return jsonify({'massage': 'Produto atualizado com sucesso'})

@app.route('/api/products', methods=['GET'])
def get_products():
    products = Product.query.all()
    product_list = []
    print(products)
    for product in products:
        product_data ={
            "id": product.id,
            "name": product.name,
            "price": product.price,
        }
        product_list.append(product_data) #pega as info do for e retorna
    return jsonify(product_list)

#CheckOut
@app.route('/api/cart/add/<int:product_id>', methods=['POST'])
@login_required
def add_to_cart(product_id):
    user = User.query.get(int(current_user.id)) #Verifica se o user esta logado
    
    product = Product.query.get(product_id)
    
    if user and product:
        cart_item = CartItem(user_id=user.id, product_id=product.id)
        db.session.add(cart_item)
        db.session.commit()
        return jsonify ({'message': "Produto add"})
    return jsonify({'message': "Produto não add"})
        
@app.route('/api/cart/remove/int<product_id>', methods=['DELETE'])
@login_required
def removeCart(product_id):
    cart_item = CartItem.query.filter_by(user_id=current_user.id, product_id=product_id).first()
    if cart_item:
        db.session.delete(cart_item)
        db.session.commit()
        return jsonify({'message': "Item removido do carrinho com sucesso"})
    return jsonify({'message': "Falha ao remover item do carrinho"}),400


@app.route('/api/cart', methods=['GET'])
@login_required
def view_cart():
    user = User.query.get(int(current_user.id))
    cart_itens = user.cart
    cart_content = []
    for cart_item in cart_itens:
        product = Product.query.get(cart_item.product.id)
        cart_content.append({
                            "id": cart_item.id,
                            "user_id": cart_item.user.id,
                            "product_id":  cart_item.product.id,
                            "product_name": product.name,
                            "product_price": product.price
        })
    return jsonify (cart_content)

@app.route('/api/cart/checkout', methods=['POST'])
@login_required
def checkout():
    user = User.query.get(int(current_user.id))
    cart_itens = user.cart
    for cart_item in cart_itens:
        db.session.delete(cart_item)
    db.session.commit()
    return jsonify({'message': "Checkout autorizado"})

# definir uma rota raiz (pagina inicial) e a função executada ao requisitar
@app.route('/')
def hello_world():
    return 'Hello World'

if __name__ == "__main__":
    app.run(debug=True)