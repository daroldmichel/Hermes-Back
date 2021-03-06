from flask import Flask, request
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_httpauth import HTTPBasicAuth, HTTPTokenAuth

from objetos import Usuario, Cliente, Banco, ClienteUsuario, Monitoramento

app = Flask(__name__)
url = "postgresql://postgres:postgres@localhost:5432/hermes"

app.config['SQLALCHEMY_DATABASE_URI'] = url
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_POOL_SIZE'] = 9999999999
app.config['SQLALCHEMY_ECHO'] = True
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
        usuarios = Usuario.query.order_by(Usuario.idusuario).all()
        results = [
            usuario.imprimir() for usuario in usuarios]

        return {"Sucesso": len(results), "usuarios": results}


@app.route('/usuario/<usuario_id>', methods=['GET', 'PUT', 'DELETE'])
@token_auth.login_required
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
        usuario_escolhido.senhasemcripto = data['senha']
        usuario_escolhido.telefone = data['telefone']
        usuario_escolhido.email = data['email']
        usuario_escolhido.ativo = data['ativo']

        msg = usuario_escolhido.atualizar()
        if msg:
            return {"Erro": f"Falha ao atualizar usuário: {usuario_escolhido.nomeusuario}. Mensagem de erro: {msg}"}, 418
        else:
            return {"Sucesso": f"Usuario {usuario_escolhido.nomeusuario} Atualizado com Sucesso."}
    elif request.method == 'DELETE':
        usuario_escolhido.deletar()
        return {"Sucesso": f"Usuario {usuario_escolhido.nomeusuario} Deletado com sucesso."}

@app.route('/usuario_login/<usuario_login>', methods=['GET'])
@token_auth.login_required
def usuario_login(usuario_login):
    user = db.session.query(Usuario).filter(Usuario.login == usuario_login).filter(Usuario.ativo == True).first()
    response = None
    if user:
        response = user.imprimir()
    if response:
        return dict(response), 200
    else:
        return {"Erro": "Falha ao buscar Usuário"}, 418

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
        clientes = Cliente.query.order_by(Cliente.idcliente).all()
        results = [
            cliente.imprimir() for cliente in clientes]

        return {"Sucesso": len(results), "clientes": results}

@app.route('/cliente/ativos', methods=['GET'])
@token_auth.login_required
def cliente_ativos():
    clientes = Cliente.query.filter(Cliente.ativo==True).order_by(Cliente.nomecliente).all()
    results = [
        cliente.imprimir() for cliente in clientes]

    return {"Sucesso": len(results), "clientes": results}

@app.route('/cliente/<cliente_id>', methods=['GET', 'PUT', 'DELETE'])
@token_auth.login_required
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
            novo_banco = Banco(nomebanco=data['nomebanco'], protocolo=data['protocolo'], ip=data['ip'], porta=data['porta'], ativo=data['ativo'], usuario=data['usuario'], senha=data['senha'], tls=data['tls'], tipo=data['tipo'], idcliente=data['idcliente'])
            novo_banco.criptar()
            msg = novo_banco.cadastrar()
            if msg:
                return {"Erro": f"Falha ao cadastrar banco: {novo_banco.nomebanco}. Mensagem de erro: {msg}"}, 418
            else:
                return {"Sucesso": f"Banco {novo_banco.nomebanco} Cadastrado com Sucesso."}
        else:
            return {"Erro": "Formato invalido, enviar no formato JSON"}, 415

    elif request.method == 'GET':
        bancos = Banco.query.order_by(Banco.idbanco).all()
        results = [
            banco.imprimir() for banco in bancos]

        return {"Sucesso": len(results), "bancos": results}


@app.route('/banco/<banco_id>', methods=['GET', 'PUT', 'DELETE'])
@token_auth.login_required
def banco_especifico(banco_id):
    banco_escolhido = Banco.query.get_or_404(banco_id)
    banco_escolhido.decriptar()
    if request.method == 'GET':
        response = banco_escolhido.imprimir()
        return {"Sucesso": "1", "banco": response}

    elif request.method == 'PUT':
        data = request.get_json()
        banco_escolhido.nomebanco = data['nomebanco']
        banco_escolhido.protocolo = data['protocolo']
        banco_escolhido.ip = data['ip']
        banco_escolhido.porta = data['porta']
        banco_escolhido.ativo = data['ativo']
        banco_escolhido.usuario = data['usuario']
        banco_escolhido.senhasemcripto = data['senha']
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

@app.route('/historico_banco', methods=['GET'])
@token_auth.login_required
def historico_banco():
    bancos = Banco.query.order_by(Banco.idbanco).all()
    results = [
        banco.imprimir_monitoramento() for banco in bancos]

    return {"Sucesso": len(results), "bancos": results}

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


@app.route('/monitoramento', methods=['GET'])
@token_auth.login_required
def monitoramento():

    monitoramentos = db.session.query(Monitoramento).filter(Monitoramento.idstatus == 2).filter(Monitoramento.idusuarioalocado == None).filter(Monitoramento.dhfinal == None).order_by(Monitoramento.idmonitoramento).all()
    results = [
        monitoramento.imprimir() for monitoramento in monitoramentos]

    return {"Sucesso": len(results), "monitoramentos": results}


@app.route('/monitoramento/<monitoramento_id>', methods=['PUT'])
@token_auth.login_required
def monitoramento_especifico(monitoramento_id):
    monitoramento = Monitoramento.query.get_or_404(monitoramento_id)
    if request.method == 'GET':
        response = monitoramento.imprimir()
        return {"Sucesso": "1", "Monitoramento": response}

    else:
        data = request.get_json()
        monitoramento.idusuarioalocado = data['idusuarioalocado']
        msg = monitoramento.atualizar()

        if msg:
            return {"Erro": f"Falha ao atualizar Monitoramento"}, 418
        else:
            return {"Sucesso": "Monitoramento Atualizado com Sucesso."}


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
