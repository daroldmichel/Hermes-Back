from flask_sqlalchemy import SQLAlchemy
from cryptography.fernet import Fernet

import psycopg2
import ibm_db

db = SQLAlchemy()


class Usuario(db.Model):
    __tablename__ = 'usuario'
    __table_args__ = {"schema": "dba"}

    idusuario = db.Column(db.Integer, primary_key=True)
    nomeusuario = db.Column(db.VARCHAR(100))
    login = db.Column(db.VARCHAR(100))
    senha = db.Column(db.VARCHAR(300))
    keysenha = db.Column(db.VARCHAR(300))
    telefone = db.Column(db.VARCHAR(20))
    email = db.Column(db.VARCHAR(50))
    token = db.Column(db.String(100))
    ativo = db.Column(db.Boolean(), default=True)
    senhasemcripto = ''

    def __init__(self, nomeusuario, login, senha, telefone, email, ativo):
        self.nomeusuario = nomeusuario
        self.login = login
        self.senhasemcripto = senha
        self.telefone = telefone
        self.email = email
        self.ativo = ativo

    def __repr__(self):
        return f"<Usuario {self.nomeusuario}>"

    def criptar(self):
        chave = Fernet.generate_key()
        cripto = Fernet(chave)
        senha = cripto.encrypt(self.senhasemcripto.encode())
        self.senha = senha.decode()
        self.keysenha = chave.decode()

    def decriptar(self):
        chave = self.keysenha
        cripto = Fernet(chave.encode())
        senha = cripto.decrypt(self.senha.encode())
        self.senhasemcripto = senha.decode()

    def validar_login(self):
        user = db.session.query(Usuario).filter(Usuario.login == self.login).filter(Usuario.ativo == True).filter(Usuario.idusuario != self.idusuario ).all()
        if user:
            return 'Login já utilizado por outro usuário'

    def cadastrar(self):
        msg = self.validar_login()
        if msg:
            return msg

        if self.ativo:
            self.token = Fernet.generate_key().decode() + Fernet.generate_key().decode()
        else:
            self.token = None
        self.criptar()
        db.session.add(self)
        db.session.commit()

    def atualizar(self):
        msg = self.validar_login()
        if msg:
            return msg

        if not self.ativo:
            self.token = None
        db.session.add(self)
        db.session.commit()

    def deletar(self):
        db.session.delete(self)
        db.session.commit()

    def logar(login, senha):
        user = db.session.query(Usuario).filter(Usuario.login == login).filter(Usuario.ativo == True).all()
        if user:
            usuario_login = Usuario.query.get_or_404(user[0].idusuario)
            usuario_login.decriptar()
            if usuario_login.senhasemcripto == senha:
                return usuario_login.token
        return None

    def verificar_token(token):
        usuario_login = db.session.query(Usuario).filter(Usuario.token == token).filter(Usuario.ativo == True).all()
        if usuario_login:
            tokens = {
                usuario_login[0].token: usuario_login[0].login
            }
            if token in tokens:
                return tokens[token]
        return None

    def imprimir(self):
        return {
            "idusuario": self.idusuario,
            "nomeusuario": self.nomeusuario,
            "login": self.login,
            "senha": self.senha,
            "keysenha": self.keysenha,
            "telefone": self.telefone,
            "email": self.email,
            "token": self.token,
            "ativo": self.ativo,
            "senhasemcripto": self.senhasemcripto
        }

class Cliente(db.Model):
    __tablename__ = 'cliente'
    __table_args__ = {"schema": "dba"}

    idcliente = db.Column(db.Integer, primary_key=True)
    nomecliente = db.Column(db.VARCHAR(100))
    cnpj = db.Column(db.VARCHAR(14))
    ie = db.Column(db.VARCHAR(14))
    telefone = db.Column(db.VARCHAR(20))
    uf = db.Column(db.CHAR(2))
    endereco = db.Column(db.VARCHAR(100))
    numero = db.Column(db.Integer)
    cep = db.Column(db.VARCHAR(8))
    ativo = db.Column(db.Boolean(), default=True)

    def __init__(self, nomecliente, cnpj, ie, telefone, uf, endereco, numero, cep, ativo):
        self.nomecliente = nomecliente
        self.cnpj = cnpj
        self.ie = ie
        self.telefone = telefone
        self.uf = uf
        self.endereco = endereco
        self.numero = numero
        self.cep = cep
        self.ativo = ativo

    def __repr__(self):
        return f"<Cliente {self.nomecliente}>"


    def cadastrar(self):
        db.session.add(self)
        db.session.commit()

    def atualizar(self):
        db.session.add(self)
        db.session.commit()

    def deletar(self):
        db.session.delete(self)
        db.session.commit()

    def imprimir(self):
        return {
            "idcliente": self.idcliente,
            "nomecliente": self.nomecliente,
            "cnpj": self.cnpj,
            "ie": self.ie,
            "telefone": self.telefone,
            "uf": self.uf,
            "endereco": self.endereco,
            "numero": self.numero,
            "ativo": self.ativo,
            "cep": self.cep
        }

class Banco(db.Model):
    __tablename__ = 'banco'
    __table_args__ = {"schema": "dba"}

    idbanco = db.Column(db.Integer, primary_key=True)
    nomebanco = db.Column(db.VARCHAR(60))
    protocolo = db.Column(db.VARCHAR(60), default='TCPIP')
    ip = db.Column(db.VARCHAR(100))
    porta = db.Column(db.VARCHAR(7))
    ativo = db.Column(db.Boolean(), default=True)
    usuario = db.Column(db.VARCHAR(100))
    senha = db.Column(db.VARCHAR(300))
    keysenha = db.Column(db.VARCHAR(300))
    tls = db.Column(db.Boolean(), default=False)
    tipo = db.Column(db.Integer, default=1)
    idcliente = db.Column(db.Integer, db.ForeignKey('dba.cliente.idcliente'))
    cliente = db.relationship("Cliente")

    senhasemcripto = ''

    def __init__(self, nomebanco, protocolo, ip, porta, ativo, usuario, senha, tls, tipo, idcliente):
        self.nomebanco = nomebanco
        self.protocolo = protocolo
        self.ip = ip
        self.porta = porta
        self.ativo = ativo
        self.usuario = usuario
        self.senhasemcripto = senha
        self.tls = tls
        self.tipo = tipo
        self.idcliente = idcliente

    def __repr__(self):
        return f"<Banco {self.nomebanco}>"

    def criptar(self):
        chave = Fernet.generate_key()
        cripto = Fernet(chave)
        senha = cripto.encrypt(self.senhasemcripto.encode())
        self.senha = senha.decode()
        self.keysenha = chave.decode()

    def decriptar(self):
        chave = self.keysenha
        cripto = Fernet(chave.encode())
        senha = cripto.decrypt(self.senha.encode())
        self.senhasemcripto = senha.decode()


    def cadastrar(self):
        db.session.add(self)
        db.session.commit()

    def atualizar(self):
        db.session.add(self)
        db.session.commit()

    def deletar(self):
        db.session.delete(self)
        db.session.commit()

    def imprimir(self):
        return {
            "idbanco": self.idbanco,
            "nomebanco": self.nomebanco,
            "protocolo": self.protocolo,
            "ip": self.ip,
            "porta": self.porta,
            "ativo": self.ativo,
            "usuario": self.usuario,
            "senha": self.senha,
            "keysenha": self.keysenha,
            "tls": self.tls,
            "tipo": self.tipo,
            "idcliente": self.idcliente
        }

    def verificar_status(self):
        self.decriptar()
        if self.tipo == 2:
            try:
                conection = psycopg2.connect(f'host={self.ip} user={self.usuario} dbname={self.nomebanco} port={self.porta} password={self.senhasemcripto}')
                conection.close()
                return
            except Exception as e:
                print(e)
                return e
        else:
            try:
                conection = ibm_db.connect(f'DATABASE={self.nomebanco};HOSTNAME={self.ip};PORT={self.porta};PROTOCOL={self.protocolo};UID={self.usuario};PWD={self.senhasemcripto};', '', '')
                ibm_db.close(conection)
                return
            except Exception as e:
                print(ibm_db.conn_errormsg())
                return e


class ClienteUsuario(db.Model):
    __tablename__ = 'relacionamento_cliente_usuario'
    __table_args__ = {"schema": "dba"}

    idcliente = db.Column(db.Integer, db.ForeignKey('dba.cliente.idcliente'), primary_key=True)
    idusuario = db.Column(db.Integer, db.ForeignKey('dba.usuario.idusuario'), primary_key=True)
    cliente = db.relationship("Cliente")
    usuario = db.relationship("Usuario")

    def __init__(self, idcliente, idusuario):
        self.idcliente = idcliente
        self.idusuario = idusuario

    def cadastrar(self):
        db.session.add(self)
        db.session.commit()

    def atualizar(self):
        db.session.add(self)
        db.session.commit()

    def deletar(self):
        db.session.delete(self)
        db.session.commit()

    def imprimir(self):
        return {
            "idcliente": self.idcliente,
            "idusuario": self.idusuario
        }

class StatusMonitoramento(db.Model):
    __tablename__ = 'status_monitoramento'
    __table_args__ = {"schema": "dba"}

    idstatus = db.Column(db.Integer, primary_key=True)
    descricaostatus = db.Column(db.VARCHAR(60))

    def __init__(self, idstatus, descricaostatus):
        self.idstatus = idstatus
        self.descricaostatus = descricaostatus
