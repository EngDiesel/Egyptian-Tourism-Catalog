# These modules to create the columns.
from sqlalchemy import Column, String, Integer, ForeignKey

# This module to create relationship between tables.
from sqlalchemy.orm import relationship

# This module for classes to inhiret from.
from sqlalchemy.ext.declarative import declarative_base

# This module to create a database engine.
from sqlalchemy import create_engine

# password hashing modules
from passlib.apps import custom_app_context as pwd_context

# Base Instance.
Base = declarative_base()

class User(Base):
    __tablename__ = "user"

    id = Column(Integer, primary_key=True)
    name = Column(String(50), nullable=False)
    email = Column(String(100), nullable=False)
    username = Column(String(32), index=True)
    password_hash = Column(String(64))


    def hash_password(self, password):
        self.password_hash = pwd_context.hash(password)


    def verify_password(self, password):
        return pwd_context.verify(password, self.password_hash)


    @property
    def serialize(self):
        return {
            'name': self.name,
            'email': self.email,
            'id': self.id
        }


class Category(Base):
    __tablename__ = "category"

    id = Column(Integer, primary_key=True)
    name = Column(String(50), nullable=False)
    picture = Column(String(250))

    @property
    def serialize(self):
        return {
            'id': self.id,
            'name': self.name,
            'picture': self.picture
        }

class Item(Base):
    __tablename__ = 'item'

    id = Column(Integer, primary_key=True)
    name = Column(String(50), nullable=False)
    picture = Column(String(250))
    description = Column(String)

    # set relationships
    user_id = Column(Integer, ForeignKey(User.id))
    user = relationship(User)
    category_id = Column(Integer, ForeignKey(Category.id))
    category = relationship(Category)


    @property
    def serialize(self):
        return {
            'id': self.id,
            'name': self.name,
            'picture': self.picture
        }

# Create the database
engine = create_engine('sqlite:///catalog.db')
Base.metadata.create_all(engine)
