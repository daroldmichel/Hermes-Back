from flask import Flask, request
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_httpauth import HTTPBasicAuth, HTTPTokenAuth

from objetos import Usuario

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = "postgresql://postgres:postgres@localhost:5432/hermes"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
migrate = Migrate(app, db)

basic_auth = HTTPBasicAuth()
token_auth = HTTPTokenAuth(scheme='Bearer')

tokens = {
    "abracadabra": "abracadabra"
}

@basic_auth.verify_password
def verify_password(username, password):
    user = db.session.query(Usuario).filter(Usuario.login == username).filter(Usuario.ativo == True).all()
    if user:
        usuario_login = Usuario.query.get_or_404(user[0].idusuario)
        usuario_login.decriptar()

        return usuario_login.logar(password)

@token_auth.verify_token
def verify_token(token):
    usuario_login = db.session.query(Usuario).filter(Usuario.token == token).filter(Usuario.ativo == True).all()
    if usuario_login:
        tokens = {
            usuario_login[0].token: usuario_login[0].login
        }
        if token in tokens:
            return tokens[token]

@app.route('/login')
@basic_auth.login_required
def login():
    return {"login": basic_auth.username(),  "token": basic_auth.current_user()}


@app.route('/usuario', methods=['POST', 'GET'])
@token_auth.login_required
def usuario():
    if request.method == 'POST':
        if request.is_json:
            data = request.get_json()
            novo_usuario = Usuario(nomeusuario=data['nomeusuario'], login=data['login'], senha=data['senha'], telefone=data['telefone'], email=data['email'], ativo=data['ativo'])
            novo_usuario.criptar()
            novo_usuario.cadastrar()
            return {"error": f"Usuario {novo_usuario.nomeusuario} Cadastrado com Sucesso."}
        else:
            return {"error": "The request payload is not in JSON format"}

    elif request.method == 'GET':
        usuarios = Usuario.query.all()
        results = [
            {
                "idusuario": usuario.idusuario,
                "nomeusuario": usuario.nomeusuario,
                "login": usuario.login,
                "senha": usuario.senha,
                "keysenha": usuario.keysenha,
                "telefone": usuario.telefone,
                "email": usuario.email,
                "token": usuario.token,
                "ativo": usuario.ativo

            } for usuario in usuarios]

        return {"count": len(results), "usuarios": results}


@app.route('/usuario/<usuario_id>', methods=['GET', 'PUT', 'DELETE'])
def usuario_especifico(usuario_id):
    usuario_escolhido = Usuario.query.get_or_404(usuario_id)
    usuario_escolhido.decriptar()
    if request.method == 'GET':
        response = {
            "idusuario": usuario_escolhido.idusuario,
            "nomeusuario": usuario_escolhido.nomeusuario,
            "login": usuario_escolhido.login,
            "senha": usuario_escolhido.senha,
            "keysenha": usuario_escolhido.keysenha,
            "telefone": usuario_escolhido.telefone,
            "email": usuario_escolhido.email,
            "token": usuario_escolhido.token,
            "ativo": usuario_escolhido.ativo,
            "senhasemcripto": usuario_escolhido.senhasemcripto
        }
        return {"message": "success", "car": response}

    elif request.method == 'PUT':
        data = request.get_json()
        usuario_escolhido.nomeusuario = data['nomeusuario']
        usuario_escolhido.login = data['login']
        usuario_escolhido.senha = data['senha']
        usuario_escolhido.keysenha = data['keysenha']
        usuario_escolhido.telefone = data['telefone']
        usuario_escolhido.email = data['email']
        usuario_escolhido.token = data['token']
        usuario_escolhido.ativo = data['ativo']

        usuario_escolhido.atualizar()
        return {"message": f"Usuário {usuario_escolhido.nomeusuario} Atualizado com Sucesso"}

    elif request.method == 'DELETE':
        usuario_escolhido.deletar()
        return {"message": f"Car {usuario_escolhido.nomeusuario} successfully deleted."}


@app.route('/')
def hello_world():
    return 'Hello World!'


if __name__ == '__main__':
    app.run()
