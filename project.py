from flask import Flask, render_template, request
from flask import redirect, url_for, flash, jsonify
from flask import session as login_session
import random
import string
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database_setup import Base, Creator, Category, Item

# oAuth imports
from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError
import httplib2
import json
from flask import make_response
import requests

app = Flask(__name__)

CLIENT_ID = json.loads(
    open('client_secrets.json', 'r').read())['web']['client_id']
APPLICATION_NAME = "Catalog Udacity"

engine = create_engine('sqlite:///categories.db')
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()


##############################################################################
# User Helper Functions - from class notes
##############################################################################


def createUser(login_session):
    newUser = Creator(name=login_session['username'], email=login_session[
                   'email'], picture=login_session['picture'])
    session.add(newUser)
    session.commit()
    user = session.query(Creator).filter_by(email=login_session['email']).one()
    return user.id


def getUserInfo(user_id):
    user = session.query(Creator).filter_by(id=user_id).one()
    return user


def getUserID(email):
    try:
        user = session.query(Creator).filter_by(email=email).one()
        return user.id
    except:
        return None

##############################################################################
# End User Helper Functions
##############################################################################


##############################################################################
# API Endpoints using JSON
##############################################################################

# # API Endpoint using JSON for all categories
@app.route('/catalog/JSON/')
def catalogJSON():
    categories = session.query(Category).all()
    return jsonify(Categories=[i.serialize for i in categories])


# API Endpoint using JSON for single item
@app.route('/catalog/<category_name>/<item_id>/JSON')
def singleItemJSON(category_name, item_id):
    item_JSON = session.query(Item).filter_by(id=item_id).one()
    # return item.title
    return jsonify(item_JSON=item_JSON.serialize)


# # API Endpoint using JSON for single category & associated items
@app.route('/catalog/<category_name>/JSON')
def singleCategoryJSON(category_name):
    category = session.query(Category).filter_by(name=category_name).one()
    items = session.query(Item).filter_by(category_id=category.id).all()
    return jsonify(catItems=[i.serialize for i in items])

##############################################################################
# End API Endpoints using JSON
##############################################################################

##############################################################################
# Categories
##############################################################################


@app.route('/')
@app.route('/catalog/')
def categoryList():
    categories = session.query(Category).all()
    items = session.query(Item).order_by(Item.title).limit(7)
    # list to hold category names
    g = []
    l = []
    for i in items:
        # get category name
        catname = session.query(Category).filter_by(id=i.category_id).one()
        g.append(i.title)
        g.append(catname.name)
        # add to new list
        l.append(g)
        g = []  # reset g for next name value pair
    d = dict(l)  # make dictionary of name/value pairs
    if 'username' not in login_session:
        return render_template('index_public.html', categories=categories,
                               items=items, cats=d)
    else:
        return render_template('index.html', categories=categories,
                               items=items, cats=d)


@app.route('/catalog/new/', methods=['GET', 'POST'])
def newCategory():
    if 'username' not in login_session:
        return redirect('/login')
    if request.method == 'POST':
        cat_name = request.form['name']
        if cat_name == "":
            errormsg = "Please enter a category to add"
            return render_template('newcategory.html', errormsg=errormsg)
        else:
            # check to see if that category already exists
            ya = session.query(Category).filter_by(name=cat_name).first()
            if ya:
                if ya.name == cat_name:
                    errormsg = cat_name + " already exists!"
                    return render_template('newcategory.html',
                                           errormsg=errormsg)
            newCategory = Category(name=cat_name,
                                   creator_id=login_session['user_id'])
            # login_session['user_id'] not being set....
            session.add(newCategory)
            session.commit()
            flash("New category " + cat_name + " created!")
            return redirect(url_for('categoryList'))
    else:
        return render_template('newcategory.html')


@app.route('/catalog/<category_name>/')
def byCategoryMenu(category_name):
    categories = session.query(Category).all()
    category = session.query(Category).filter_by(name=category_name).first()
    items = session.query(Item).filter_by(category_id=category.id).all()

    # check to see if user owns the item
    if not login_session['user_id'] == category.creator_id:
        buttons = False
    else:
        buttons = True

    if 'username' not in login_session:
        if items:
            return render_template('category_public.html', category=category,
                                   items=items, categories=categories)
        else:
            return render_template('category_public.html', category=category,
                                   categories=categories)
    else:
        if items:
            return render_template('category.html', category=category,
                                   items=items, categories=categories,
                                   buttons=buttons)
        else:
            return render_template('category.html', category=category,
                                   categories=categories,
                                   buttons=buttons)


@app.route('/catalog/<category_id>/edit', methods=['GET', 'POST'])
def editCategory(category_id):
    if 'username' not in login_session:
        return redirect('/login')
    category = session.query(Category).filter_by(id=category_id).first()
    if not login_session['user_id'] == category.creator_id:
        flash("You must own a category to edit it.")
        return redirect('/catalog/' + category.name + '/')
    if request.method == 'POST':
        # change db entry
        if request.form['name']:
            category.name = request.form['name']
            name_now = request.form['name']
            session.add(category)  # updates the existing entry
            session.commit()
            flash(name_now + " has been edited")
            return redirect('catalog/' + name_now + '/')
        else:  # empty form, prompt to fix
            errormsg = "Please enter a category description"
            return render_template('editcategory.html',
                                   category=category, errormsg=errormsg)
    elif category:  # it's GET; initial setup
        return render_template('editcategory.html', category=category)
    else:
        return "program crashing"


@app.route('/catalog/<category_id>/delete', methods=['GET', 'POST'])
def deleteCategory(category_id):
    if 'username' not in login_session:
        return redirect('/login')
    deletedCategory = session.query(Category).filter_by(id=category_id).first()
    if not login_session['user_id'] == deletedCategory.creator_id:
        flash("You must own a category to delete it.")
        return redirect('/catalog/' + deletedCategory.name + '/')
    nmdel = deletedCategory.name
    if request.method == 'POST':
        # delete it
        session.delete(deletedCategory)
        session.commit()
        # delete items associated with the category
        itemsDel = session.query(Item).filter_by(category_id=category_id)
        for i in itemsDel:
            session.delete(i)
            session.commit()
        flash(nmdel + " has been deleted")
        return redirect('/catalog/')
    else:
        return render_template('deletecategory.html',
                               category=deletedCategory.name,
                               category_id=category_id)

##############################################################################
# End categories
##############################################################################


##############################################################################
# Items
##############################################################################

@app.route('/catalog/<category_id>/newitem', methods=['GET', 'POST'])
def newItem(category_id):
    if 'username' not in login_session:
        return redirect('/login')
    category = session.query(Category).filter_by(id=category_id).first()
    catname = category.name
    if request.method == 'POST':
        item_name = request.form['name']
        item_description = request.form['description']
        if item_name == "" or item_description == "":
            errormsg = "Please fill out both name and description"
            return render_template('newitem.html',
                                   errormsg=errormsg,
                                   name=item_name,
                                   description=item_description,
                                   category_name=catname,
                                   category_id=category_id)
        else:
            newitem = Item(category_id=category_id,
                           title=item_name,
                           description=item_description,
                           creator_id=login_session['user_id'])
            session.add(newitem)
            session.commit()
            flash("New item " + item_name + " created!")
            return redirect("catalog/" + catname)
    else:
        return render_template('newitem.html',
                               category_name=catname,
                               category_id=category_id)


@app.route('/catalog/<category_name>/<item_id>')
def itemDescription(category_name, item_id):
    item = session.query(Item).filter_by(id=item_id).first()
    if 'username' not in login_session:
        return render_template('item_public.html', category_name=category_name,
                               item=item)
    else:
        # check to see if user owns the item
        if not login_session['user_id'] == item.creator_id:
            buttons = False
        else:
            buttons = True
        if item:
            return render_template('item.html', category_name=category_name,
                                   item=item, buttons=buttons)


@app.route('/catalog/<category_name>/<item_id>/edit', methods=['GET', 'POST'])
def editItem(category_name, item_id):
    if 'username' not in login_session:
        return redirect('/login')
    item = session.query(Item).filter_by(id=item_id).first()
    # make sure user owns item before they can edit it
    if not login_session['user_id'] == item.creator_id:
        flash("You must own an item to edit it.")
        return render_template('item.html', category_name=category_name,
                               item=item)
    categories = session.query(Category).all()
    if request.method == 'POST':
        # change db entry
        if request.form['name'] and request.form['description']:
            item.title = request.form['name']
            editedItem = item.title
            item.description = request.form['description']
            # find category id chosen
            item.category_id = request.form['cID']
            session.add(item)  # updates the existing entry
            session.commit()
            flash(editedItem + " has been edited")
            return redirect('catalog/' + category_name + '/' + item_id)
        else:  # empty form, prompt to fix
            errormsg = "Please enter a title and description"
            return render_template('edititem.html',
                                   category_name=category_name,
                                   item=item, errormsg=errormsg,
                                   categories=categories)
    elif item:  # it's GET; initial setup
        return render_template('edititem.html',
                               category_name=category_name, item=item,
                               categories=categories)
    else:
        return "program crashing"


@app.route('/catalog/<category_name>/<item_id>/delete',
           methods=['GET', 'POST'])
def deleteItem(category_name, item_id):
    if 'username' not in login_session:
        return redirect('/login')
    deletedItem = session.query(Item).filter_by(id=item_id).first()
    if not login_session['user_id'] == deletedItem.creator_id:
        flash("You must own an item to delete it.")
        return render_template('item.html', category_name=category_name,
                               item=deletedItem)
    if request.method == 'POST':
        nmdel = deletedItem.title
        # delete it
        session.delete(deletedItem)
        session.commit()
        flash(nmdel + " has been deleted")
        return redirect('/catalog/' + category_name)
    else:
        return render_template('deleteitem.html', category_name=category_name,
                               deletedItem=deletedItem)

##############################################################################
# End items
##############################################################################

##############################################################################
# Login stuff
##############################################################################


# Create anti-forgery state token
@app.route('/login')
def showLogin():
    state = ''.join(random.choice(string.ascii_uppercase + string.digits)
                    for x in xrange(32))
    login_session['state'] = state
    # return "The current session state is %s" % login_session['state']
    return render_template('login.html', STATE=state)
    # return render_template('login.html')


@app.route('/gconnect', methods=['POST'])
def gconnect():
    # Validate state token
    if request.args.get('state') != login_session['state']:
        response = make_response(json.dumps('Invalid state parameter.'), 401)
        # response.headers['Content-Type'] = 'application/json'
        response.headers['Content-Type'] = 'application-json'  # heather
        return response
    # Obtain authorization code
    code = request.data

    try:
        # Upgrade the authorization code into a credentials object
        oauth_flow = flow_from_clientsecrets('client_secrets.json', scope='')
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
            json.dumps("Token client ID does not match app."), 401)
        print "Token client ID does not match app."
        response.headers['Content-Type'] = 'application/json'
        return response

    stored_credentials = login_session.get('credentials')
    stored_gplus_id = login_session.get('gplus_id')
    if stored_credentials is not None and gplus_id == stored_gplus_id:
        response = make_response(json.dumps('Current user is already connected.'),  # NOQA
                                 200)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Store the access token in the session for later use.
    # login_session['credentials'] = credentials
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

    # see if user exists, if it doesn't make a new one
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
    output += ' " style = "width: 300px; height: 300px;border-radius: 150px;-webkit-border-radius: 150px;-moz-border-radius: 150px;"> '    # NOQA
    flash("You are now logged in as %s" % login_session['username'])
    print "done!"
    return output

##############################################################################
# End login
##############################################################################

##############################################################################
# Logout
##############################################################################


@app.route('/gdisconnect')
def gdisconnect():
    access_token = login_session['access_token']
    print 'In gdisconnect access token is %s', access_token
    print 'User name is: '
    print login_session['username']
    if access_token is None:
        print 'Access Token is None'
        response = make_response(json.dumps('Current user not connected.'), 401)  # NOQA
        response.headers['Content-Type'] = 'application/json'
        return response
    url = 'https://accounts.google.com/o/oauth2/revoke?token=%s' % login_session['access_token']  # NOQA
    h = httplib2.Http()
    result = h.request(url, 'GET')[0]
    print 'result is '
    print result
    if result['status'] == '200':
        del login_session['access_token']
        del login_session['gplus_id']
        del login_session['username']
        del login_session['email']
        del login_session['picture']
        flash("You are now logged out.")
        return redirect('/')
        # return response
    else:
        response = make_response(json.dumps('Failed to revoke token.', 400))
        response.headers['Content-Type'] = 'application/json'
        return response


##############################################################################
# End Logout
##############################################################################


##############################################################################
# Encryption key
##############################################################################

if __name__ == '__main__':
    app.secret_key = "super_secret_key"
    app.debug = True
    app.run(host='0.0.0.0', port=5000)

##############################################################################
# End encryption key
##############################################################################
