from flask import Flask, request
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_httpauth import HTTPBasicAuth, HTTPTokenAuth

from objetos import Usuario, Cliente, Banco, ClienteUsuario

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = "postgresql://postgres:postgres@localhost:5432/hermes"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app, session_options={'autocommit': True})
migrate = Migrate(app, db)

@app.route('/monitoramento')
def monitoramento():
    bancos = Banco.query.filter(Banco.ativo == True).order_by(Banco.idbanco).all()
    results = [
        banco.verificar_status() for banco in bancos]

    return 'OK', 200

if __name__ == '__main__':
    app.run(host="localhost", port=4999)
