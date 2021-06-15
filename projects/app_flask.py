from flask import Flask, render_template, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)

# MySql datebase
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///product.database'

db = SQLAlchemy(app)


# 模型( model )定義
class Product(db.Model):
    __tablename__ = 'product'
    pid = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(30), unique=True, nullable=False)
    price = db.Column(db.Integer, nullable=False)
    img = db.Column(db.String(100), unique=True, nullable=False)
    description = db.Column(db.String(255), nullable=False)
    state = db.Column(db.String(10), nullable=False)
    insert_time = db.Column(db.DateTime, default=datetime.now)
    update_time = db.Column(db.DateTime, onupdate=datetime.now, default=datetime.now)

    def __init__(self, name, price, img, description, state):
        self.name = name
        self.price = price
        self.img = img
        self.description = description
        self.state = state


@app.route('/')
def index():
    # Create data
    db.create_all()

    return 'ok'


# @app.route('/add')
# def add():
#     # Add data
#     product_max = Product('Max', 8888, 'https://picsum.photos/id/1047/1200/600', '', '')
#     database.session.add(product_max)
#     database.session.commit()
#     return 'ok'


@app.route('/add_lot')
def add_lot():
    p1 = Product('Isacc', 8888, 'https://picsum.photos/id/1047/1200/600', '', '')
    p2 = Product('Dennis', 9999, 'https://picsum.photos/id/1049/1200/600', '', '')
    p3 = Product('Joey', 7777, 'https://picsum.photos/id/1033/1200/600', '', '')
    p4 = Product('Fergus', 6666, 'https://picsum.photos/id/1041/1200/600', '', '')
    p5 = Product('Max', 5555, 'https://picsum.photos/id/1070/1200/600', '', '')
    p6 = Product('Jerry', 4444, 'https://picsum.photos/id/1044/1200/600', '', '')
    p = [p1, p2, p3, p4, p5, p6]

    db.session.add_all(p)
    db.session.commit()
    return 'ok'


@app.route('/read')
def read():
    # Read data
    query = Product.query.filter_by(name='Fergus').first()
    print(query.name)
    print(query.price)
    return 'ok'


if __name__ == "__main__":
    app.run(debug=True)
