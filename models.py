from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import backref
from flask_bcrypt import Bcrypt

db = SQLAlchemy()

bcrypt = Bcrypt()

def connect_db(app):
    db.app = app
    db.init_app(app)
    
class User(db.Model):
    """User model"""
    
    __tablename__ = 'users'
    
    def __repr__(self):
        u = self
        return f"<id={u.username}"    
   
    username = db.Column(db.Text,
                         primary_key=True,                         
                         unique=True,
                         )
    password = db.Column(db.Text,
                         nullable=False,
                         )
    email = db.Column(db.Text,
                      nullable=False)
    first_name = db.Column(db.Text,
                           nullable=False)
    last_name = db.Column(db.Text,
                           nullable=False)
    
    feedback = db.relationship("Feedback", backref="user", cascade="all,delete")
    
    @classmethod
    def register(cls, username, pw, email, first_name, last_name):
        """Register and create new user with hashed pw."""
        
        hashed = bcrypt.generate_password_hash(pw)
        hashed_utf8 = hashed.decode("utf8")
        user = cls(
            username=username,
            password=hashed_utf8,
            email=email,
            first_name=first_name,
            last_name=last_name
        )
        db.session.add(user)        
        return user
    
    @classmethod
    def authenticate(cls, username, password):
        """Authenticate username and password."""
        
        user = User.query.filter_by(username=username).first()
        
        if user and bcrypt.check_password_hash(user.password, password):
            # return user instance
            return user
        else:
            return False   

class Feedback(db.Model):
    """Feedbacl model"""
    
    __tablename__ = 'feedback'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(150),
                      nullable=False)
    content = db.Column(db.Text,
                        nullable=False)
    username = db.Column(db.String(20),
                         db.ForeignKey('users.username'),
                         nullable=False)
        
        