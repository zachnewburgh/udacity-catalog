from flask import Flask, render_template, request, redirect, jsonify, url_for, flash
from sqlalchemy import create_engine, asc
from sqlalchemy.orm import sessionmaker
# from database_setup import Base, Catalog, Item, User
from flask import session as login_session
import random
import string
from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError
import httplib2
import json
from flask import make_response
import requests

app = Flask(__name__)

# CLIENT_ID = json.loads(open('client_secrets.json', 'r').read())['web']['client_id']
# APPLICATION_NAME = "Catalog Application"


# Connect to Database and create database session
# engine = create_engine('sqlite:///catalog.db')
# Base.metadata.bind = engine
# DBSession = sessionmaker(bind=engine)
# session = DBSession()


# Show all categories
@app.route('/')
@app.route('/categories/')
def showCategories():
    return "category index"
    # categories = session.query(Category).order_by(asc(Category.name))
    # return render_template('categories.html', categories=categories)


# Create a new category
@app.route('/categories/new/', methods=['GET', 'POST'])
def newCategory():
    return "category new"
    # return render_template('newCategory.html')


# Edit a category
@app.route('/categories/<int:category_id>/edit/', methods=['GET', 'POST'])
def editCategory(category_id):
    return "category edit"
    # categoryToEdit = session.query(Category).filter_by(id=category_id).one()
    # return render_template('editCategory.html', category=categoryToEdit)


# Delete a category
@app.route('/categories/<int:category_id>/delete/', methods=['GET', 'POST'])
def deleteCategory(category_id):
    return "category delete"
    # categoryToDelete = session.query(Category).filter_by(id=category_id).one()
    # return render_template('deleteCategory.html', category=categoryToDelete)


# Show a category
@app.route('/categories/<int:category_id>/')
@app.route('/categories/<int:category_id>/items/')
def showCategory(category_id):
    return "category show"
    # category = session.query(Category).filter_by(id=category_id).one()
    # items = session.query(CategoryItem).filter_by(category_id=category_id).all()
    # return render_template('category.html', items=items, category=category)


# Create a new category item
@app.route('/categories/<int:category_id>/items/new/', methods=['GET', 'POST'])
def newCategoryItem(category_id):
    return "category item new"
    # category = session.query(Category).filter_by(id=category_id).one()
    # return render_template('newCategoryItem.html', category_id=category_id)


# Edit a category item
@app.route('/categories/<int:category_id>/items/<int:item_id>/edit', methods=['GET', 'POST'])
def editCategoryItem(category_id, item_id):
    return "category item edit"
    # itemToEdit = session.query(CategoryItem).filter_by(id=item_id).one()
    # return render_template('editCategoryItem.html', category_id=category_id, item_id=item_id, item=itemToEdit)


# Delete a category item
@app.route('/categories/<int:category_id>/items/<int:item_id>/delete', methods=['GET', 'POST'])
def deleteCategoryItem(category_id, item_id):
    return "category item delete"
    # category = session.query(Category).filter_by(id=category_id).one()
    # itemToDelete = session.query(CategoryItem).filter_by(id=item_id).one()
    # return render_template('deleteCategoryItem.html', item=itemToDelete)


if __name__ == '__main__':
    app.secret_key = 'super_secret_key'
    app.debug = True
    app.run(host='0.0.0.0', port=5000)