from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from catalog_database import Base, Category, CategoryItem

engine = create_engine('sqlite:///catalog.db')
# Bind the engine to the metadata of the Base class so that the
# declaratives can be accessed through a DBSession instance
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
# A DBSession() instance establishes all conversations with the database
# and represents a "staging zone" for all the objects loaded into the
# database session object. Any change made against the objects in the
# session won't be persisted into the database until you call
# session.commit(). If you're not happy about the changes, you can
# revert all of them back to the last commit by calling
# session.rollback()
session = DBSession()


# Create dummy categories
Category1 = Category(name='Soccer')
session.add(Category1)
session.commit()

Category2 = Category(name='Basketball')
session.add(Category2)
session.commit()

Category3 = Category(name='Baseball')
session.add(Category3)
session.commit()

Category4 = Category(name='Frisbee')
session.add(Category4)
session.commit()

Category5 = Category(name='Snowboarding')
session.add(Category5)
session.commit()

Category6 = Category(name='Rock Climbing')
session.add(Category6)
session.commit()

Category7 = Category(name='Foosball')
session.add(Category7)
session.commit()

Category8 = Category(name='Skating')
session.add(Category8)
session.commit()

Category9 = Category(name='Hockey')
session.add(Category9)
session.commit()

# Create dummy items
CategoryItem1 = CategoryItem(title='Stick',
                             description="Hello",
                             cat_id=9)
session.add(CategoryItem1)
session.commit()

CategoryItem2 = CategoryItem(title='Goggles',
                             description="Hello",
                             cat_id=5)
session.add(CategoryItem2)
session.commit()

CategoryItem3 = CategoryItem(title='Snowboard',
                             description="Hello",
                             cat_id=5)
session.add(CategoryItem3)
session.commit()

CategoryItem4 = CategoryItem(title='Two shinguards',
                             description="Hello",
                             cat_id=1)
session.add(CategoryItem4)
session.commit()

CategoryItem5 = CategoryItem(title='Shinguards',
                             description="Hello",
                             cat_id=1)
session.add(CategoryItem5)
session.commit()

CategoryItem6 = CategoryItem(title='Frisbee',
                             description="Hello",
                             cat_id=4)
session.add(CategoryItem6)
session.commit()

CategoryItem7 = CategoryItem(title='Bat',
                             description="Hello",
                             cat_id=3)
session.add(CategoryItem7)
session.commit()

CategoryItem8 = CategoryItem(title='Jersey',
                             description="Hello",
                             cat_id=1)
session.add(CategoryItem8)
session.commit()

CategoryItem9 = CategoryItem(title='Soccer Cleats',
                             description="Hello",
                             cat_id=1)
session.add(CategoryItem9)
session.commit()

print "Populated the catalog database!"