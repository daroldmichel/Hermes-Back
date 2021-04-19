from flask_sqlalchemy import SQLAlchemy
from cryptography.fernet import Fernet

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

    def cadastrar(self):
        if self.ativo:
            self.token = Fernet.generate_key().decode()
        else:
            self.token = None
        db.session.add(self)
        db.session.commit()

    def atualizar(self):
        if not self.ativo:
            self.token = None
        db.session.add(self)
        db.session.commit()

    def deletar(self):
        db.session.delete(self)
        db.session.commit()

    def logar(self, ls_senha):
        self.decriptar()

        if self.senhasemcripto == ls_senha:
            return self.token
        else:
            return None
