# database_setup.py

# sections:
# config - imports modules, creates declarative base instances

from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import create_engine
from sqlalchemy import DateTime

Base = declarative_base()


# class
class Creator(Base):
    """class representing a user"""
    __tablename__ = 'creator'

    id = Column(Integer, primary_key=True)
    name = Column(String(250), nullable=False)
    email = Column(String(250), nullable=False)
    picture = Column(String(250))


class Category(Base):
    """class representing a category"""
    __tablename__ = 'category'

    id = Column(Integer, primary_key=True)
    name = Column(String(80), nullable=False)
    creator_id = Column(Integer, ForeignKey('creator.id'))
    creator = relationship(Creator)

    # to create JSON API endpoint
    @property
    def serialize(self):

        return {
            'name': self.name,
            'id': self.id,
            'creator': self.creator,
        }


class Item(Base):
    """class representing an item"""
    __tablename__ = 'item'

    id = Column(Integer, primary_key=True)
    title = Column(String(80), nullable=False)
    description = Column(String(250))
    creator_id = Column(Integer, ForeignKey('creator.id'))
    creator = relationship(Creator)
    category_id = Column(Integer, ForeignKey('category.id'))
    category = relationship(Category)
    # creation_time = Column(DateTime)

    # to create JSON API endpoint
    @property
    def serialize(self):

        return {
            'title': self.title,
            'description': self.description,
            'id': self.id,
            'category': self.category_id,
            'creator': self.creator,
        }


engine = create_engine('sqlite:///categories.db')
Base.metadata.create_all(engine)
