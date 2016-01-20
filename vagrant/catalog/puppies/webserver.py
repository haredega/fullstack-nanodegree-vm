from flask import Flask, render_template, url_for, request, redirect, flash, jsonify
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database_setup import Base, Puppy, PuppyPage, Shelter, Owner, dbConnect
import datetime
from time import strftime
from numpy import size
app = Flask(__name__)

engine = create_engine('sqlite:///puppyshelter.db')
Base.metadata.bind=engine
DBSession = sessionmaker(bind = engine)
session = DBSession()

@app.route('/')
@app.route('/index')
def index():
    ans = render_template('index.html')
    return ans

@app.route('/<string:list_type>/list')
def list_view(list_type):
    if list_type == 'puppies':
        items = session.query(Puppy).all()
    elif list_type == 'shelters':
        items = session.query(Shelter).all()
    elif list_type == 'owners':
        items = session.query(Owner).all()
    else:
        #TODO - create error 404 template
        return render_template('error404.html')
    ans = render_template('list_view.html', list_type = list_type, items = items, now=datetime.date.today() )
    return ans

@app.route('/<string:list_type>/<int:item_id>')
def item_view(list_type, item_id):
    if list_type == 'puppies':
        item = session.query(Puppy).filter(id=item_id).first()
    elif list_type == 'shelters':
        item = session.query(Shelter).filter(id=item_id).first()
    elif list_type == 'owners':
        item = session.query(Owner).filter(id=item_id).first()
    else:
        #TODO - create error 404 template
        return render_template('error404.html')
    if item is None:
        flash("Could not find the "+list_type+"!")
        return redirect(url_for('/'+list_type+'/list'))
    else:
        ans = render_template('item_view.html', list_type=list_type, item_id = item_id, item = item)
        return ans

@app.route('/<string:list_type>/new', methods=['GET', 'POST'])
def item_new(list_type):
    if request.method == 'GET':
        return render_template('item_add.html', type=list_type)
    #TODO - Find out how I can get the columns of a table
    #TODO - Make getters to complete all of the item types
    #TODO - Make a template for the add page
    if request.method == 'POST':
        item.name = request.form['edit-menu-name']
        item.description=request.form['edit-menu-description']
        item.price=request.form['edit-menu-price']
        session.add(item)
        session.commit()
        flash("Succesfully edited the menu item!")
        return redirect(url_for('restaurantMenu', restaurant_id=restaurant_id))

#Starts Server
if __name__ == '__main__':
    app.secret_key = 'super_secret_key'
    app.debug = True
    app.run(host='0.0.0.0', port=5000)
