from flask import Flask, render_template, request
from flask import redirect, url_for, flash, jsonify
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database_setup import Base, Creator, Category, Item

app = Flask(__name__)

engine = create_engine('sqlite:///categories.db')
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()


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
    items = session.query(Item).order_by(Item.title).all()
    #list to hold category names
    g = []
    l = []
    for i in items:
        #get category name
        catname = session.query(Category).filter_by(id=i.category_id).one()
        g.append(i.title)
        g.append(catname.name)
        # add to new list
        l.append(g)
        g = []  # reset g for next name value pair
    d = dict(l)  # make dictionary of name/value pairs
    return render_template('index.html', categories=categories,
                           items=items, cats=d)
    # return render_template('index.html', categories=categories, items=items)


@app.route('/catalog/new/', methods=['GET', 'POST'])
def newCategory():
    if request.method == 'POST':
        cat_name = request.form['name']
        if cat_name == "":
            errormsg = "Please enter a category to add"
            return render_template('newcategory.html', errormsg=errormsg)
        else:
            newCategory = Category(name=cat_name)
            session.add(newCategory)
            session.commit()
            # flash("New menu item created!")
            return redirect(url_for('categoryList'))
    else:
        return render_template('newcategory.html')


@app.route('/catalog/<category_name>/')
def byCategoryMenu(category_name):
    categories = session.query(Category).all()
    category = session.query(Category).filter_by(name=category_name).first()
    items = session.query(Item).filter_by(category_id=category.id)
    return render_template('category.html', category=category,
                           items=items, categories=categories)


@app.route('/catalog/<category_id>/edit', methods=['GET', 'POST'])
def editCategory(category_id):
    category = session.query(Category).filter_by(id=category_id).first()
    if request.method == 'POST':
        # change db entry
        if request.form['name']:
            category.name = request.form['name']
            session.add(category)  # updates the existing entry
            session.commit()
            name_now = category.name
#           flash(editedItem.name + " has been edited")
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
    deletedCategory = session.query(Category).filter_by(id=category_id).first()
    if request.method == 'POST':
        # delete it
        session.delete(deletedCategory)
        session.commit()
        # delete items associated with the category
        itemsDel = session.query(Item).filter_by(category_id=category_id)
        for i in itemsDel:
            session.delete(i)
            session.commit()
        # flash(deletedItem.name + " has been deleted")
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
                                   catname=catname)
        else:
            newitem = Item(category_id=category_id,
                           title=item_name,
                           description=item_description)
            session.add(newitem)
            session.commit()
            # flash("New menu item created!")
            return redirect("catalog/" + catname + "/")
    else:
        return render_template('newitem.html',
                               category_name=catname,
                               category_id=category_id)


@app.route('/catalog/<category_name>/<item_id>')
def itemDescription(category_name, item_id):
    item = session.query(Item).filter_by(id=item_id).first()
    if item:
        return render_template('item.html', category_name=category_name,
                               item=item)
    else:
        return "nothing here"


@app.route('/catalog/<category_name>/<item_id>/edit', methods=['GET', 'POST'])
def editItem(category_name, item_id):
    item = session.query(Item).filter_by(id=item_id).first()
    if request.method == 'POST':
        # change db entry
        if request.form['name'] and request.form['description']:
            item.title = request.form['name']
            item.description = request.form['description']
            session.add(item)  # updates the existing entry
            session.commit()
#           flash(editedItem.name + " has been edited")
            return redirect('catalog/' + category_name + '/' + item_id)
        else:  # empty form, prompt to fix
            errormsg = "Please enter a title and description"
            return render_template('edititem.html',
                                   category_name=category_name,
                                   item=item, errormsg=errormsg)
    elif item:  # it's GET; initial setup
        return render_template('edititem.html',
                               category_name=category_name, item=item)
    else:
        return "program crashing"


@app.route('/catalog/<category_name>/<item_id>/delete',
           methods=['GET', 'POST'])
def deleteItem(category_name, item_id):
    deletedItem = session.query(Item).filter_by(id=item_id).first()
    if request.method == 'POST':
        # delete it
        session.delete(deletedItem)
        session.commit()
        # flash(deletedItem.name + " has been deleted")
        return redirect('/catalog/' + category_name)
    else:
        return render_template('deleteitem.html', category_name=category_name,
                               deletedItem=deletedItem)

##############################################################################
# End items
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


##############################################################################
# User Helper Functions - from class notes
##############################################################################


# def createUser(login_session):
#     newUser = Creator(name=login_session['username'], email=login_session[
#                    'email'], picture=login_session['picture'])
#     session.add(newUser)
#     session.commit()
#     user = session.query(Creator).filter_by(email=login_session['email']).one()
#     return user.id


# def getUserInfo(user_id):
#     user = session.query(Creator).filter_by(id=user_id).one()
#     return user


# def getUserID(email):
#     try:
#         user = session.query(Creator).filter_by(email=email).one()
#         return user.id
#     except:
#         return None

##############################################################################
# End User Helper Functions
##############################################################################
