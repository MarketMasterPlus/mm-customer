from werkzeug.security import generate_password_hash, check_password_hash
from . import db  # Import the shared db instance

class Customer(db.Model):
    __tablename__ = 'customers'

    id = db.Column(db.Integer, primary_key=True)
    fullname = db.Column(db.String(100), nullable=False)
    cpf = db.Column(db.String(14), unique=True, nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)  # Use password_hash to store the hashed password
    addressid = db.Column(db.String(128), nullable=False)

    @property
    def password(self):
        raise AttributeError('password is not a readable attribute')

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)  # Set password_hash here

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)  # Check against the hashed password
