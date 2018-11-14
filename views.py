# database modules to create session and engine
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# get the models.
from models import Base, User, Item, Category

# import flask modules for the web application
from flask import Flask, url_for, redirect, flash, request,\
 render_template, jsonify, make_response

from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError


from flask import session as login_session
import httplib2, requests
import random, string, json


# setting things up...
app = Flask(__name__)
engine = create_engine('sqlite:///catalog.db')
Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)


# =======================================================================
# ======================== User Operations ==============================
# =======================================================================
CLIENT_ID = json.loads(open('google-client-secrets.json', 'r').read())['web']['client_id']


@app.route('/login')
def showLogin():

    if 'username' in login_session:
        flash('You are already logged in.')
        return redirect('/')
    # show login page..
    state = ''.join(random.choice(string.ascii_lowercase + string.ascii_uppercase + string.digits) for x in range(32))
    login_session['state'] = state

    return render_template('login-page.html', STATE=state, CLIENT_ID=CLIENT_ID)


def createUser(login_session):
    newUser = User(name=login_session['username'],
                   email=login_session['email'])

    session = DBSession()
    session.add(newUser)
    session.commit()

    user = session.query(User).filter_by(email=login_session['email']).one()
    return user.id


def getUserInfo(user_id):
    session = DBSession()
    user = session.query(User).filter_by(id=user_id).one()
    return user


def getUserID(email):
    session = DBSession()

    try:
        user = session.query(User).filter_by(email=email).one()
        return user.id
    except:
        return None


@app.route('/gconnect', methods=['POST'])
def gconnect():
# sign in with google function..
    # check for the state parameter
    if request.args.get('state') != login_session['state']:
        response = make_response('Invalid state parameter!')
        response.headers['content-type'] = 'text/html'
        return response
    # get the code from the request.. which is the one-time access code.
    code = request.data

    # try to upgrade the code into a cardential object.
    try:
        # Upgrade the authorization code into a credentials object
        oauth_flow = flow_from_clientsecrets('google-client-secrets.json', scope='')
        oauth_flow.redirect_uri = 'postmessage'
        credentials = oauth_flow.step2_exchange(code)
    except FlowExchangeError:
        response = make_response(
            json.dumps('Failed to upgrade the authorization code.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Check that the access token is valid.
    access_token = credentials.access_token
    url = ('https://www.googleapis.com/oauth2/v1/tokeninfo?access_token=%s' % access_token)
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

    # check if the user is already connected..
    stored_access_token = login_session.get('access_token')
    stored_gplus_id = login_session.get('gplus_id')
    if stored_access_token is not None and gplus_id == stored_gplus_id:
        response = make_response(json.dumps('Current user is already connected.'), 200)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Store the access token in the session for later use.
    login_session['provider'] = 'google'
    login_session['access_token'] = credentials.access_token
    login_session['gplus_id'] = gplus_id

    # Get user info
    userinfo_url = "https://www.googleapis.com/oauth2/v1/userinfo"
    params = {'access_token': credentials.access_token, 'alt': 'json'}
    answer = requests.get(userinfo_url, params=params)
    # get the data from answer obj.
    data = answer.json()
    print data
    login_session['username'] = data['name']
    login_session['email'] = data['email']

    # here we go ...
    user_id = getUserID(login_session['email'])

    if not user_id:
        user_id = createUser(login_session)

    login_session['user_id'] = user_id
    flash("you are now logged in as %s" % login_session['username'])
    return ""


@app.route('/gdisconnect')
def gdisconnect():
    access_token = login_session.get('access_token')
    if access_token is None:
        response = make_response(json.dumps("User is not logged in"), 401)
        response.headers['content-type'] = 'application/json'
        return response

    url = 'https://accounts.google.com/o/oauth2/revoke?'
    url += 'token=%s' % login_session['access_token']
    h = httplib2.Http()

    result = h.request(url, 'GET')[0]
    print result

    if result['status'] == '200':
        del login_session['access_token']
        del login_session['gplus_id']
        del login_session['username']
        del login_session['email']
        response = make_response(json.dumps('Successfully disconnected.'), 200)
        response.headers['Content-Type'] = 'application/json'
        return redirect('/')
    else:
        response = make_response(json.dumps('Failed to revoke token for \
        given user.', 400))
        response.headers['Content-Type'] = 'application/json'
        return response


@app.route('/fbconnect', methods=['POST'])
def fbconnect():
    if request.args.get('state') != login_session['state']:
        response = make_response(json.dumps('Invalid State Parameter'), 401)
        response.headers['content-type'] = 'application/json'
        return response

    access_token = request.data
    app_id = json.loads(open('fb_client_secrets.json', 'r').read())['web']['app_id']
    app_secret = json.loads(open('fb_client_secrets.json').read())['web']['app_secret']

    url = 'https://graph.facebook.com/oauth/access_token?grant_type=fb_exchange_token&'
    url += 'client_id=%s&client_secret=%s&fb_exchange_token=%s' % (app_id, app_secret, access_token)

    h = httplib2.Http()
    result = h.request(url, 'GET')[1]

    userinfo_url = 'https://graph.facebook.com/v2.8/me'

    token = result.split(',')[0].split(':')[1].replace('"', '')

    url = 'https://graph.facebook.com/v2.8/me?access_token=%s&fields=name,id,email' % token

    h = httplib2.Http()
    result = h.request(url, 'GET')[1]

    data = json.loads(result)
    print data

    if 'error' in data:
        response = make_response(json.dumps('Invalid access token!'), 401)
        response.headers['content-type'] = 'application/json'
        return response

    login_session['provider'] = 'facebook'
    login_session['username'] = data['name']
    login_session['email'] = data['email']
    login_session['facebook_id'] = data['id']

    login_session['access_token'] = token

    # see if user exists.
    user_id = getUserID(login_session['email'])

    if not user_id:
        user_id = createUser(login_session)

    login_session['user_id'] = user_id

    output = 'logged in successfully..'
    flash("you are now logged in as %s" % login_session['username'])
    print "done!"
    return output


@app.route('/fbdisconnect')
def fbdisconnect():
    facebook_id = login_session['facebook_id']
    url = 'https://graph.facebook.com/%s/permissions' % facebook_id
    h = httplib2.Http()
    result = h.request(url, 'DELETE')[1]

    del login_session['username']
    del login_session['email']
    del login_session['user_id']
    del login_session['facebook_id']

    return 'You have been logged out'


@app.route('/disconnect')
def disconnect():
    if 'provider' in login_session:
        if login_session['provider'] == 'facebook':
            fbdisconnect()

        if login_session['provider'] == 'google':
            gdisconnect()

        flash('You have successfully logged out.')

        return redirect('/')
    else:
        flash('You are not logged in')
        return redirect('/')


@app.route('/users/new', methods=['POST'])
def newUser():
    # create new user
    session = DBSession()
    name = request.json.get('name')
    email = request.json.get('email')
    username = request.json.get('username')
    newUser = User(name=name, email=email, username=username)
    session.add(newUser)
    session.commit()
    return redirect('/')


@app.route('/users')
def getUsersJson():
    # view all users json
    session = DBSession()
    users = session.query(User).all()
    return jsonify(users=[user.serialize for user in users])


# =======================================================================
# ======================== Category Operations ==========================
# =======================================================================
@app.route('/')
@app.route('/catalog')
@app.route('/categories')
def catalog():
    # show main page ...
    session = DBSession()
    categories = session.query(Category).limit(6).all()
    latestItems = session.query(Item).all()
    if len(latestItems) > 10:
        latestItems = reversed(latestItems[len(latestItems) - 10:])
    else:
        latestItems = reversed(session.query(Item).limit(10).all())

    return render_template('catalog.html', categories=categories, latestItems=latestItems, login_session=login_session)


@app.route('/categories/<int:category_id>')
@app.route('/categories/<int:category_id>/items')
def category(category_id):
    # the category page for specifec 'id'
    session = DBSession()
    category = session.query(Category).filter_by(id=category_id).first()
    items = session.query(Item).filter_by(category=category).all()
    categories = session.query(Category).all()
    return render_template('catalog-items.html', category=category, categories=categories, items=items, login_session=login_session)


@app.route('/categories/new', methods=['POST'])
def addCategory():
    # Add a new Category.
    name = request.json.get('name')
    picture = request.json.get('picture')

    newCateg = Category(name=name, picture=picture)
    session = DBSession()
    session.add(newCateg)
    session.commit()
    return redirect('/', 200)


# =======================================================================
# =========================== Item Operations ===========================
#========================================================================
@app.route('/categories/<int:category_id>/items/<int:item_id>')
def itemPage(category_id, item_id):
    # Show Item Page..
    session = DBSession()
    item = session.query(Item).filter_by(category_id=category_id, id=item_id).one()
    if item:
        return render_template('item-page.html', item=item, login_session=login_session)
    return None


@app.route('/addItem', methods=['POST', 'GET'])
def addItem():
    # add item page..
    if not login_session['username']:
        flash('You have to login first.')
        return redirect('/')

    session = DBSession()
    if request.method == 'GET':
        categories = session.query(Category).all()
        return render_template('create-item.html', categories=categories)
    else:
        name = request.form['name']
        description = request.form['description']
        category_id = request.form['category_id']
        picture = request.form['picture']

        if not name:
            flash('No name found')
            return redirect('/addItem')

        if not description:
            flash('No description found')
            return redirect('/addItem')

        if not picture:
            flash('No picture found')
            return redirect('/addItem')

        newItem = Item(name=name, description=description, category_id=category_id, picture=picture, user_id=1)

        print 'created item'

        session.add(newItem)
        session.commit()

        flash('item added successfully')
        return redirect('/categories/' + str(newItem.category_id))


@app.route('/categories/<int:category_id>/items/<int:item_id>/edit', methods=['POST', 'GET'])
def editItem(category_id, item_id):
    # edit item
    if 'username' not in login_session:
        flash('You have to login first.')
        return redirect('/')

    session = DBSession()
    item = session.query(Item).filter_by(id=item_id).first()

    if request.method == 'POST':
        if request.form['name']:
            item.name = request.form['name']

        if request.form['description']:
            item.description = request.form['description']

        if request.form['category_id']:
            item.category_id = request.form['category_id']

        if request.form['picture']:
            item.picture = request.form['picture']

        session.add(item)
        session.commit()
        return redirect('/categories/' + str(item.category_id) + '/items/' + str(item.id))

    categories = session.query(Category).all()
    return render_template('edit-item.html', item=item, categories=categories)


@app.route('/categories/<int:category_id>/items/<int:item_id>/delete', methods=['POST', 'GET'])
def deleteItem(category_id, item_id):

    if 'username' not in login_session:
        flash('You have to login first.')
        return redirect('/')

    session = DBSession()

    item = session.query(Item).filter_by(id=item_id).first()
    if request.method == 'GET':
        return render_template('delete-item.html', item=item)
    else:
        session.delete(item)
        session.commit()
        flash('item deleted successfully.')
        return redirect('/categories/' + str(category_id))


@app.route('/categories/<int:category_id>/items/new', methods=['POST'])
def addItemJson(category_id):
    # Add a new Item.
    session = DBSession()
    name = request.json.get('name')
    picture = request.json.get('picture')
    description = request.json.get('description')
    user_id = request.json.get('user_id')

    item = Item(name=name, picture=picture, description=description,user_id=user_id, category_id=category_id)
    session.add(item)
    session.commit()
    return redirect('/categories')


# =======================================================================
# ======================== Test Operations ==============================
# =======================================================================
# this route to delete something.
@app.route('/del')
def deleteCat():
    session = DBSession()
    obj = session.query(Item).filter_by(name='hello').first()
    session.delete(obj)
    session.commit()
    return redirect('/categories/3')


if __name__ == '__main__':
    app.secret_key = 'secret_key'
    app.debug = True
    app.run(host='0.0.0.0', port=8000)
