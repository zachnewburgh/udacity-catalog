from flask import Flask
from flask import render_template, redirect, jsonify, url_for
from flask import request, flash
from flask import make_response
from flask import session as login_session
from sqlalchemy import create_engine, asc, desc
from sqlalchemy.orm import sessionmaker
from catalog_database import Base, Category, CategoryItem, User
from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError
import httplib2
import json
import requests
import random
import string

app = Flask(__name__)

CLIENT_ID = json.loads(open('google_client_secrets.json',
                            'r').read())['web']['client_id']
APPLICATION_NAME = "Catalog Application"


# Connect to Database and create database session
engine = create_engine('sqlite:///catalog.db')
Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)
session = DBSession()


# Create anti-forgery state token
@app.route('/login')
def login():
    state = ''.join(random.choice(string.ascii_uppercase + string.digits)
                    for x in xrange(32))
    login_session['state'] = state
    return render_template('login.html', STATE=state)


@app.route('/fbconnect', methods=['POST'])
def fbconnect():
    if request.args.get('state') != login_session['state']:
        response = make_response(json.dumps('Invalid state parameter.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    access_token = request.data
    print "access token received %s " % access_token

    app_id = json.loads(open('fb_client_secrets.json', 'r').read())[
        'web']['app_id']
    app_secret = json.loads(
        open('fb_client_secrets.json', 'r').read())['web']['app_secret']
    url = ("https://graph.facebook.com/oauth/access_token?"
           "grant_type=fb_exchange_token&client_id=%s&"
           "client_secret=%s&fb_exchange_token=%s") % (
        app_id, app_secret, access_token)
    h = httplib2.Http()
    result = h.request(url, 'GET')[1]

    # Use token to get user info from API
    userinfo_url = "https://graph.facebook.com/v2.4/me"
    # strip expire tag from access token
    token = result.split("&")[0]
    url = ("https://graph.facebook.com/v2.4/me?"
           "%s&fields=name,id,email") % token
    h = httplib2.Http()
    result = h.request(url, 'GET')[1]
    # print "url sent for API access:%s"% url
    # print "API JSON result: %s" % result
    data = json.loads(result)
    login_session['provider'] = 'facebook'
    login_session['username'] = data["name"]
    login_session['email'] = data["email"]
    login_session['facebook_id'] = data["id"]

    '''
    The token must be stored in the login_session in order to properly logout,
    let's strip out the information before the equals sign in our token
    '''
    stored_token = token.split("=")[1]
    login_session['access_token'] = stored_token

    # Get user picture
    url = ("https://graph.facebook.com/v2.4/me/picture?"
           "%s&redirect=0&height=200&width=200") % token
    h = httplib2.Http()
    result = h.request(url, 'GET')[1]
    data = json.loads(result)

    login_session['picture'] = data["data"]["url"]

    # see if user exists
    user_id = getUserID(login_session['email'])
    if not user_id:
        user_id = createUser(login_session)
    login_session['user_id'] = user_id

    output = ''
    output += '<h1>Welcome, '
    output += login_session['username']

    output += '!</h1>'
    output += '<img src="'
    output += login_session['picture']
    output += ' " style = "width: 300px; height: 300px;border-radius: 150px;'
    output += '-webkit-border-radius: 150px;-moz-border-radius: 150px;"> '

    flash("Now logged in as %s" % login_session['username'])
    return output


@app.route('/fbdisconnect')
def fbdisconnect():
    facebook_id = login_session['facebook_id']
    # The access token must me included to successfully logout
    access_token = login_session['access_token']
    url = ("https://graph.facebook.com/%s"
           "/permissions?access_token=%s") % (facebook_id, access_token)
    h = httplib2.Http()
    result = h.request(url, 'DELETE')[1]
    return "you have been logged out"


# CONNECT - Perform authorization check and issue a token to the user
@app.route('/gconnect', methods=['POST'])
def gconnect():
    # Validate state token
    if request.args.get('state') != login_session['state']:
        response = make_response(json.dumps('Invalid state parameter.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    # Obtain authorization code
    code = request.data

    try:
        # Upgrade the authorization code into a credentials object
        oauth_flow = flow_from_clientsecrets('google_client_secrets.json',
                                             scope='')
        oauth_flow.redirect_uri = 'postmessage'
        credentials = oauth_flow.step2_exchange(code)
    except FlowExchangeError:
        response = make_response(
            json.dumps('Failed to upgrade the authorization code.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Check that the access token is valid.
    access_token = credentials.access_token
    url = ('https://www.googleapis.com/oauth2/v1/tokeninfo?access_token=%s'
           % access_token)
    h = httplib2.Http()
    result = json.loads(h.request(url, 'GET')[1])
    # If there was an error in the access token info, abort.
    if result.get('error') is not None:
        response = make_response(json.dumps(result.get('error')), 500)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is used for the intended user.
    gplus_id = credentials.id_token['sub']
    if result['user_id'] != gplus_id:
        response = make_response(
            json.dumps("Token's user ID doesn't match given user ID."), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is valid for this app.
    if result['issued_to'] != CLIENT_ID:
        response = make_response(
            json.dumps("Token's client ID does not match app's."), 401)
        print "Token's client ID does not match app's."
        response.headers['Content-Type'] = 'application/json'
        return response

    stored_access_token = login_session.get('access_token')
    stored_gplus_id = login_session.get('gplus_id')
    if stored_access_token is not None and gplus_id == stored_gplus_id:
        response = make_response(json.dumps("""Current
                                            user is already connected."""),
                                 200)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Store the access token in the session for later use.
    login_session['access_token'] = credentials.access_token
    login_session['gplus_id'] = gplus_id

    # Get user info
    userinfo_url = "https://www.googleapis.com/oauth2/v1/userinfo"
    params = {'access_token': credentials.access_token, 'alt': 'json'}
    answer = requests.get(userinfo_url, params=params)

    data = answer.json()

    login_session['username'] = data['name']
    login_session['picture'] = data['picture']
    login_session['email'] = data['email']
    # ADD PROVIDER TO LOGIN SESSION
    login_session['provider'] = 'google'

    # see if user exists, if it doesn't make a new one
    user_id = getUserID(data["email"])
    if not user_id:
        user_id = createUser(login_session)
    login_session['user_id'] = user_id

    output = ''
    output += '<h1>Welcome, '
    output += login_session['username']
    output += '!</h1>'
    output += '<img src="'
    output += login_session['picture']
    output += ' " style = "width: 300px; height: 300px;border-radius: 150px;'
    output += '-webkit-border-radius: 150px;-moz-border-radius: 150px;"> '
    flash("you are now logged in as %s" % login_session['username'])
    print "done!"
    return output


# User Helper Functions
def createUser(login_session):
    newUser = User(name=login_session['username'],
                   email=login_session['email'],
                   picture=login_session['picture'])
    session.add(newUser)
    session.commit()
    user = session.query(User).filter_by(email=login_session['email']).one()
    return user.id


def getUserInfo(user_id):
    user = session.query(User).filter_by(id=user_id).one()
    return user


def getUserID(email):
    try:
        user = session.query(User).filter_by(email=email).one()
        return user.id
    except:
        return None


# DISCONNECT - Revoke a current user's token and reset their login_session
@app.route('/gdisconnect')
def gdisconnect():
    # Only disconnect a connected user.
    access_token = login_session.get('access_token')
    if access_token is None:
        response = make_response(json.dumps("""Current
                                            user not connected."""),
                                 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    url = 'https://accounts.google.com/o/oauth2/revoke?token=%s' % access_token
    h = httplib2.Http()
    result = h.request(url, 'GET')[0]
    if result['status'] != '200':
        # For whatever reason, the given token was invalid.
        response = make_response(
            json.dumps('Failed to revoke token for given user.'), 400)
        response.headers['Content-Type'] = 'application/json'
        return response


# JSON APIs to view Catalog, Category, and CategoryItem information
@app.route('/catalog/JSON')
def categoriesJSON():
    categories = session.query(Category).order_by(asc(Category.name))
    return jsonify(categories=[c.serialize for c in categories])


@app.route('/catalog/<string:category_name>/items/JSON')
def showCategoryJSON(category_name):
    category = session.query(Category).filter_by(name=category_name).one()
    return jsonify(Category=category.serialize)


@app.route('/catalog/<string:category_name>/<string:item_name>/JSON')
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
    return render_template('indexCategoryItem.html',
                           categories=categories,
                           items=items)


# Show a category
@app.route('/catalog/<string:category_name>/items/')
def showCategory(category_name):
    categories = session.query(Category).order_by(asc(Category.name))
    category = session.query(Category).filter_by(name=category_name).one()
    return render_template('showCategory.html',
                           category=category,
                           categories=categories)


# Create a new category item
@app.route('/catalog/new/', methods=['GET', 'POST'])
def newCategoryItem():
    categories = session.query(Category).order_by(asc(Category.name))
    if 'username' not in login_session:
        flash("You can only add an item if you are logged in.")
        return redirect(url_for('login'))
    if request.method == 'POST':
        title = request.form['title']
        description = request.form['description']
        category_id = request.form['category_id']
        category = session.query(Category).filter_by(id=category_id).one()
        if title and description and category_id:
            newCategoryItem = CategoryItem(title=title,
                                           description=description,
                                           cat_id=category_id)
            session.add(newCategoryItem)
            session.commit()
            return redirect(url_for('showCategory',
                                    category_name=category.name))
        else:
            return render_template('newCategoryItem.html',
                                   categories=categories)
    else:
        return render_template('newCategoryItem.html',
                               categories=categories)


# Show a category
@app.route('/catalog/<string:category_name>/<string:item_name>/')
def showCategoryItem(category_name, item_name):
    item = session.query(CategoryItem).filter_by(title=item_name).one()
    return render_template('showCategoryItem.html', item=item)


# Edit a category item
@app.route('/catalog/<string:category_name>/<string:item_name>/edit',
           methods=['GET', 'POST'])
def editCategoryItem(category_name, item_name):
    if 'username' not in login_session:
        flash("You can only edit an item if you are logged in.")
        return redirect(url_for('login'))
    categories = session.query(Category).order_by(asc(Category.name))
    itemToEdit = session.query(CategoryItem).filter_by(title=item_name).one()
    if request.method == 'POST':
        title = request.form['title']
        description = request.form['description']
        category = request.form['category']
        authorized = login_session['username'] == itemToEdit.user.name
        if title and description and category and authorized:
            itemToEdit.title = title
            itemToEdit.description = description
            itemToEdit.cat_id = category
            session.commit()
            return redirect(url_for('showCategory',
                                    category_name=category_name))
        else:
            if authorized == false:
                flash("You can only edit an item that you created.")
            return render_template('editCategoryItem.html',
                                   item=itemToEdit)
    else:
        if login_session['username'] == itemToEdit.user.name:
            return render_template('editCategoryItem.html',
                                   item=itemToEdit,
                                   categories=categories)
        else:
            flash("You can only edit an item that you created.")
            return redirect(url_for('showCategoryItem',
                                    category_name=category_name,
                                    item_name=item_name))


# Delete a category item
@app.route('/catalog/<string:category_name>/<string:item_name>/delete',
           methods=['GET', 'POST'])
def deleteCategoryItem(category_name, item_name):
    if 'username' not in login_session:
        flash("You can only delete an item if you are logged in.")
        return redirect(url_for('login'))
    category = session.query(Category).filter_by(name=category_name).one()
    itemToDelete = session.query(CategoryItem).filter_by(title=item_name).one()
    authorized = login_session['username'] == itemToDelete.user.name
    if request.method == 'POST':
        if authorized:
            session.delete(itemToDelete)
            session.commit()
        else:
            flash("You can only delete an item that you created.")
        return redirect(url_for('showCategory', category_name=category_name))
    else:
        if login_session['username'] == itemToDelete.user.name:
            return render_template('deleteCategoryItem.html',
                                   item=itemToDelete)
        else:
            flash("You can only delete an item that you created.")
            return redirect(url_for('showCategoryItem',
                                    category_name=category_name,
                                    item_name=item_name))


# Disconnect based on provider
@app.route('/logout')
def logout():
    if 'provider' in login_session:
        if login_session['provider'] == 'google':
            gdisconnect()
            del login_session['gplus_id']
            del login_session['access_token']
        if login_session['provider'] == 'facebook':
            fbdisconnect()
            del login_session['facebook_id']
        del login_session['username']
        del login_session['email']
        del login_session['picture']
        del login_session['user_id']
        del login_session['provider']
        flash("You have successfully been logged out.")
        return redirect(url_for('login'))
    else:
        flash("You were not logged in")
        return redirect(url_for('indexCategory'))


if __name__ == '__main__':
    app.secret_key = 'super_secret_key'
    app.debug = True
    app.run(host='0.0.0.0', port=5000)
