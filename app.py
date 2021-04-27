from flask import Flask, request
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_httpauth import HTTPBasicAuth, HTTPTokenAuth

from objetos import Usuario, Cliente, Banco, ClienteUsuario

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = "postgresql://postgres:postgres@localhost:5432/hermes"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
migrate = Migrate(app, db)

basic_auth = HTTPBasicAuth()
token_auth = HTTPTokenAuth(scheme='Bearer')


@basic_auth.verify_password
def verify_password(username, password):
    return Usuario.logar(username, password)

@token_auth.verify_token
def verify_token(token):
    return Usuario.verificar_token(token)

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
            msg = novo_usuario.cadastrar()
            if msg:
                return {"Erro": f"Falha ao cadastrar usuário: {novo_usuario.nomeusuario}. Mensagem de erro: {msg}"}, 418
            else:
                return {"Sucesso": f"Usuario {novo_usuario.nomeusuario} Cadastrado com Sucesso."}
        else:
            return {"Erro": "Formato invalido, enviar no formato JSON"}, 415

    elif request.method == 'GET':
        usuarios = Usuario.query.all()
        results = [
            usuario.imprimir() for usuario in usuarios]

        return {"Sucesso": len(results), "usuarios": results}


@app.route('/usuario/<usuario_id>', methods=['GET', 'PUT', 'DELETE'])
def usuario_especifico(usuario_id):
    usuario_escolhido = Usuario.query.get_or_404(usuario_id)
    usuario_escolhido.decriptar()
    if request.method == 'GET':
        response = usuario_escolhido.imprimir()
        return {"Sucesso": "1", "usuario": response}

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

        msg = usuario_escolhido.atualizar()
        if msg:
            return {"Erro": f"Falha ao atualizar usuário: {usuario_escolhido.nomeusuario}. Mensagem de erro: {msg}"}, 418
        else:
            return {"Sucesso": f"Usuario {usuario_escolhido.nomeusuario} Atualizado com Sucesso."}
    elif request.method == 'DELETE':
        usuario_escolhido.deletar()
        return {"Sucesso": f"Usuario {usuario_escolhido.nomeusuario} Deletado com sucesso."}

@app.route('/cliente', methods=['POST', 'GET'])
@token_auth.login_required
def cliente():
    if request.method == 'POST':
        if request.is_json:
            data = request.get_json()
            novo_cliente = Cliente(nomecliente=data['nomecliente'], cnpj=data['cnpj'], ie=data['ie'], telefone=data['telefone'], uf=data['uf'], endereco=data['endereco'], numero=data['numero'], ativo=data['ativo'], cep=data['cep'])
            msg = novo_cliente.cadastrar()
            if msg:
                return {"Erro": f"Falha ao cadastrar cliente: {novo_cliente.nomecliente}. Mensagem de erro: {msg}"}, 418
            else:
                return {"Sucesso": f"Cliente {novo_cliente.nomecliente} Cadastrado com Sucesso."}
        else:
            return {"Erro": "Formato invalido, enviar no formato JSON"}, 415

    elif request.method == 'GET':
        clientes = Cliente.query.all()
        results = [
            cliente.imprimir() for cliente in clientes]

        return {"Sucesso": len(results), "cliente": results}


@app.route('/cliente/<cliente_id>', methods=['GET', 'PUT', 'DELETE'])
def cliente_especifico(cliente_id):
    cliente_escolhido = Cliente.query.get_or_404(cliente_id)
    if request.method == 'GET':
        response = cliente_escolhido.imprimir()
        return {"Sucesso": "1", "cliente": response}

    elif request.method == 'PUT':
        data = request.get_json()
        cliente_escolhido.nomecliente = data['nomecliente']
        cliente_escolhido.cnpj = data['cnpj']
        cliente_escolhido.ie = data['ie']
        cliente_escolhido.telefone = data['telefone']
        cliente_escolhido.uf = data['uf']
        cliente_escolhido.endereco = data['endereco']
        cliente_escolhido.numero = data['numero']
        cliente_escolhido.ativo = data['ativo']
        cliente_escolhido.cep = data['cep']

        msg = cliente_escolhido.atualizar()
        if msg:
            return {"Erro": f"Falha ao atualizar cliente: {cliente_escolhido.nomecliente}. Mensagem de erro: {msg}"}, 418
        else:
            return {"Sucesso": f"Cliente {cliente_escolhido.nomecliente} Atualizado com Sucesso."}
    elif request.method == 'DELETE':
        cliente_escolhido.deletar()
        return {"Sucesso": f"Cliente {cliente_escolhido.nomecliente} Deletado com sucesso."}


@app.route('/banco', methods=['POST', 'GET'])
@token_auth.login_required
def banco():
    if request.method == 'POST':
        if request.is_json:
            data = request.get_json()
            novo_banco = Banco(nomebanco=data['nomebanco'], protocolo=data['protocolo'], ip=data['ip'], porta=data['porta'], ativo=data['ativo'], usuario=data['usuario'], senha=data['senha'], tls=data['tls'], idcliente=data['idcliente'])
            novo_banco.criptar()
            msg = novo_banco.cadastrar()
            if msg:
                return {"Erro": f"Falha ao cadastrar banco: {novo_banco.nomebanco}. Mensagem de erro: {msg}"}, 418
            else:
                return {"Sucesso": f"Banco {novo_banco.nomebanco} Cadastrado com Sucesso."}
        else:
            return {"Erro": "Formato invalido, enviar no formato JSON"}, 415

    elif request.method == 'GET':
        bancos = Banco.query.all()
        results = [
            banco.imprimir() for banco in bancos]

        return {"Sucesso": len(results), "bancos": results}


@app.route('/banco/<banco_id>', methods=['GET', 'PUT', 'DELETE'])
def banco_especifico(banco_id):
    banco_escolhido = Banco.query.get_or_404(banco_id)
    banco_escolhido.decriptar()
    if request.method == 'GET':
        response = banco_escolhido.imprimir()
        return {"Sucesso": "1", "Banco": response}

    elif request.method == 'PUT':
        data = request.get_json()
        banco_escolhido.nomebanco = data['nomebanco']
        banco_escolhido.protocolo = data['protocolo']
        banco_escolhido.ip = data['ip']
        banco_escolhido.porta = data['porta']
        banco_escolhido.ativo = data['ativo']
        banco_escolhido.usuario = data['usuario']
        banco_escolhido.senha = data['senha']
        banco_escolhido.keysenha = data['keysenha']
        banco_escolhido.tls = data['tls']
        banco_escolhido.idcliente = data['idcliente']

        msg = banco_escolhido.atualizar()
        if msg:
            return {"Erro": f"Falha ao atualizar banco: {banco_escolhido.nomebanco}. Mensagem de erro: {msg}"}, 418
        else:
            return {"Sucesso": f"Banco {banco_escolhido.nomebanco} Atualizado com Sucesso."}
    elif request.method == 'DELETE':
        banco_escolhido.deletar()
        return {"Sucesso": f"Usuario {banco_escolhido.nomebanco} Deletado com sucesso."}

@app.route('/cliente-usuario', methods=['POST', 'GET'])
@token_auth.login_required
def clienteUsuario():
    if request.method == 'POST':
        if request.is_json:
            data = request.get_json()
            novo_cliente_usuario = ClienteUsuario(idcliente=data['idcliente'], idusuario=data['idusuario'])
            msg = novo_cliente_usuario.cadastrar()
            if msg:
                return {"Erro": f"Falha ao relacionar cliente: {novo_cliente_usuario.idcliente}, ao usuário: {novo_cliente_usuario.idusuario}. Mensagem de erro: {msg}"}, 418
            else:
                return {"Sucesso": f"Relacionamento cliente: {novo_cliente_usuario.idcliente}, ao usuário: {novo_cliente_usuario.idusuario} Cadastrado com Sucesso."}
        else:
            return {"Erro": "Formato invalido, enviar no formato JSON"}, 415

    elif request.method == 'GET':
        cliente_usuarios = ClienteUsuario.query.all()
        results = [
            cliente_usuario.imprimir() for cliente_usuario in cliente_usuarios]

        return {"Sucesso": len(results), "relacionamentos": results}


# @app.route('/banco/<banco_id>', methods=['GET', 'PUT', 'DELETE'])
# def banco_especifico(banco_id):
#     banco_escolhido = Banco.query.get_or_404(banco_id)
#     banco_escolhido.decriptar()
#     if request.method == 'GET':
#         response = banco_escolhido.imprimir()
#         return {"Sucesso": "1", "Banco": response}
#
#     elif request.method == 'PUT':
#         data = request.get_json()
#         banco_escolhido.nomebanco = data['nomebanco']
#         banco_escolhido.protocolo = data['protocolo']
#         banco_escolhido.ip = data['ip']
#         banco_escolhido.porta = data['porta']
#         banco_escolhido.ativo = data['ativo']
#         banco_escolhido.usuario = data['usuario']
#         banco_escolhido.senha = data['senha']
#         banco_escolhido.keysenha = data['keysenha']
#         banco_escolhido.tls = data['tls']
#         banco_escolhido.idcliente = data['idcliente']
#
#         msg = banco_escolhido.atualizar()
#         if msg:
#             return {"Erro": f"Falha ao atualizar banco: {banco_escolhido.nomebanco}. Mensagem de erro: {msg}"}, 418
#         else:
#             return {"Sucesso": f"Banco {banco_escolhido.nomebanco} Atualizado com Sucesso."}
#     elif request.method == 'DELETE':
#         banco_escolhido.deletar()
#         return {"Sucesso": f"Usuario {banco_escolhido.nomebanco} Deletado com sucesso."}

@app.route('/status')
def hello_world():
    return 'OK!'


if __name__ == '__main__':
    app.run()
