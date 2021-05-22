# initliazing our flask app, SQLAlchemy and Marshmallow
from flask import Flask, jsonify, request
from flask_marshmallow import Marshmallow
from flask_sqlalchemy import SQLAlchemy
from marshmallow import fields
from sqlalchemy import Column, Integer, String

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///user.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
ma = Marshmallow(app)


# this is our database model
class UserModel(db.Model):
    __tablename__ = 'users'
    # id = db.Column(db.Integer, primary_key=True)
    # name = db.Column(db.String(80), unique=True, nullable=False)
    # email = db.Column(db.String(120), unique=True, nullable=False)
    # password = db.Column(db.String(120))
    id = Column(Integer, primary_key=True)
    name = Column(String(80), unique=True, nullable=False)
    email = Column(String(120), unique=True, nullable=False)
    password = Column(String(120))

    def __init__(self, name, email, password):
        self.name = name
        self.email = email
        self.password = password


class UserSchema(ma.Schema):
    id = fields.Integer()
    name = fields.Str()
    email = fields.Email()
    password = fields.Str()
    # class Meta:
    #     model = UserModel


post_schema = UserSchema()
posts_schema = UserSchema(many=True)


# adding a post
@app.route('/post', methods=['POST'])
def add_post():
    result = post_schema.load(request.json)

    name = result['name']
    email = result['email']
    password = result['password']
    # name = request.json['name']
    # email = request.json['email']
    # password = request.json['password']

    my_posts = UserModel(name, email, password)
    db.session.add(my_posts)
    db.session.commit()

    return post_schema.jsonify(my_posts)


# getting posts
@app.route('/get', methods=['GET'])
def get_post():
    all_posts = UserModel.query.all()
    result = posts_schema.dumps(all_posts)
    # print(f"result: {result}")
    #
    # for op in all_posts:
    #     print(op.id)
    #     print(op.name)
    #     print(op.email)
    #     print(op.password)

    return posts_schema.jsonify(all_posts)


# getting particular post
@app.route('/post_details/<id>/', methods=['GET'])
def post_details(id):
    post = UserModel.query.get(id)
    # print(f"post: {post_schema.jsonify(post)}")
    # return post_schema.jsonify(post)
    return post_schema.dumps(post)


# updating post
@app.route('/post_update/<id>/', methods=['PUT'])
def post_update(id):
    post = UserModel.query.get(id)

    name = request.json['name']
    email = request.json['email']
    password = request.json['password']

    post.name = name
    post.email = email
    post.password = password

    db.session.commit()

    print(f"post: {post}")
    return post_schema.jsonify(post)


# deleting post
@app.route('/post_delete/<id>/', methods=['DELETE'])
def post_delete(id):
    post = UserModel.query.get(id)
    db.session.delete(post)
    db.session.commit()

    return post_schema.jsonify(post)


if __name__ == "__main__":
    app.run(debug=True)
