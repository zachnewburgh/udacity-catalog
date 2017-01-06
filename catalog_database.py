from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import create_engine
 
Base = declarative_base()

class User(Base):
  __tablename__ = 'user'
  id = Column(Integer, primary_key=True)
  name = Column(String(80), nullable = False)
  email = Column(String(80))
  picture = Column(String(250))

class Category(Base):
  __tablename__ = 'category'
  id = Column(Integer, primary_key=True)
  name = Column(String(250), nullable=False)
  items = relationship("CategoryItem", backref="category")

  @property
  def serialize(self):
      return {
        'id': self.id,
        'name': self.name,
        'Item': [item.serialize for item in self.items]
      }

  @property
  def serialize_items(self):
    return [item.serialize for item in self.items]

class CategoryItem(Base):
  __tablename__ = 'category_item'
  id = Column(Integer, primary_key = True)
  title = Column(String(80), nullable = False)
  description = Column(String(250))
  cat_id = Column(Integer, ForeignKey('category.id'))

  @property
  def serialize(self):
      return {
         'id': self.id,
         'title': self.title,
         'description': self.description,
         'cat_id': self.cat_id
      }


engine = create_engine('sqlite:///catalog.db')
Base.metadata.create_all(engine)
