from flask import Flask, render_template, request, redirect, jsonify, url_for, flash
from sqlalchemy import create_engine, asc, desc
from sqlalchemy.orm import sessionmaker
from catalog_database import Base, Category, CategoryItem
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
engine = create_engine('sqlite:///catalog.db')
Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)
session = DBSession()


# JSON APIs to view Catalog, Category, and CategoryItem information
@app.route('/catalog.json')
def categoriesJSON():
    categories = session.query(Category).all()
    return jsonify(categories=[c.serialize for c in categories])


@app.route('/catalog/<string:category_name>/items.json')
def showCategoryJSON(category_name):
    category = session.query(Category).filter_by(name=category_name).one()
    return jsonify(Category=category.serialize)


@app.route('/catalog/<string:category_name>/<string:item_name>.json')
def showCategoryItemJSON(category_name, item_name):
    item = session.query(CategoryItem).filter_by(title=item_name).one()
    return jsonify(Item=item.serialize)


# Redirect root to indexCategory
@app.route('/')
def root():
    return redirect(url_for('indexCategory'))


# Show all categories
@app.route('/catalog/')
def indexCategory():
    categories = session.query(Category).order_by(asc(Category.name))
    items = session.query(CategoryItem).order_by(desc(CategoryItem.id))
    return render_template('indexCategoryItem.html', categories=categories, items=items)


# Show a category
@app.route('/catalog/<string:category_name>/items/')
def showCategory(category_name):
    categories = session.query(Category).all()
    category = session.query(Category).filter_by(name=category_name).one()
    items = session.query(CategoryItem).filter_by(cat_id=category.id).order_by(asc(CategoryItem.title))
    return render_template('showCategory.html', items=items, category=category, categories=categories)


# Create a new category item
@app.route('/catalog/<string:category_name>/new/', methods=['GET', 'POST'])
def newCategoryItem(category_name):
    category = session.query(Category).filter_by(name=category_name).one()
    if request.method == 'POST':
        newCategoryItem = CategoryItem(title=request.form['title'],
                                       description=request.form['description'],
                                       cat_id=category.id)
        session.add(newCategoryItem)
        session.commit()
        return redirect(url_for('showCategory', category_name=category.name))
    else:
        return render_template('newCategoryItem.html', category_name=category_name)


# Show a category
@app.route('/catalog/<string:category_name>/<string:item_name>/')
def showCategoryItem(category_name, item_name):
    category = session.query(Category).filter_by(name=category_name).one()
    item = session.query(CategoryItem).filter_by(title=item_name).one()
    return render_template('showCategoryItem.html', item=item, category=category)


# Edit a category item
@app.route('/catalog/<string:category_name>/<string:item_name>/edit', methods=['GET', 'POST'])
def editCategoryItem(category_name, item_name):
    itemToEdit = session.query(CategoryItem).filter_by(title=item_name).one()
    if request.method == 'POST':
        if request.form['title'] and request.form['description']:
            itemToEdit.title = request.form['title']
            itemToEdit.description = request.form['description']
            return redirect(url_for('showCategory', category_name=category_name))
    else:
        return render_template('editCategoryItem.html', item=itemToEdit)


# Delete a category item
@app.route('/catalog/<string:category_name>/<string:item_name>/delete', methods=['GET', 'POST'])
def deleteCategoryItem(category_name, item_name):
    category = session.query(Category).filter_by(name=category_name).one()
    itemToDelete = session.query(CategoryItem).filter_by(title=item_name).one()
    if request.method == 'POST':
        session.delete(itemToDelete)
        session.commit()
        return redirect(url_for('showCategory', category_name=category_name))
    else:
        return render_template('deleteCategoryItem.html', item=itemToDelete)


if __name__ == '__main__':
    app.secret_key = 'super_secret_key'
    app.debug = True
    app.run(host='0.0.0.0', port=5000)