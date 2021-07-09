from flask_bcrypt import Bcrypt
from flask_sqlalchemy import SQLAlchemy

bcrypt = Bcrypt()
db = SQLAlchemy()

def connect_db(app):
    """Connect this database to provided Flask app.

    You should call this in your Flask app.
    """

    db.app = app
    db.init_app(app)

class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, unique = True, autoincrement = True, primary_key = True)
    name = db.Column(db.Text, nullable = False)
    username = db.Column(db.Text, unique = True, nullable = False)
    password = db.Column(db.Text, nullable = False)
    email = db.Column(db.Text, nullable = False)
    number = db.Column(db.String, nullable = False)
    spoon_username = db.Column(db.String)
    spoon_hash = db.Column(db.String)
    meal = db.relationship('weekly_meal', backref = "user")

    @classmethod
    def signup(cls, name, username, password, email, number, spoon_username, spoon_hash):
        hashed_pwd = bcrypt.generate_password_hash(password).decode('UTF-8')

        user = User(username=username, email=email, password=hashed_pwd, name = name, number = number, spoon_hash = spoon_hash, spoon_username = spoon_username)

        db.session.add(user)
        return user

    @classmethod
    def authenticate(cls, username, password):
        user = cls.query.filter_by(username=username).first()

        if user:
            is_auth = bcrypt.check_password_hash(user.password, password)
            if is_auth:
                return user

        return False

class weekly_meal(db.Model):
    __tablename__ = "meal"
    id = db.Column(db.Integer, primary_key = True)
    meal = db.Column(db.PickleType)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete = "CASCADE"))
    





