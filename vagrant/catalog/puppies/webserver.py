from flask import Flask, render_template, url_for, request, redirect, flash, jsonify
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database_setup import Base, Puppy, PuppyPage, Shelter, Owner, dbConnect
import datetime
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
        return render_template('error404.html')
    ans = render_template('list_view.html', list_type = list_type, items = items, now=datetime.date.today() )
    return ans

@app.route('/<string:list_type>/<int:item_id>')
def item_view(list_type, item_id):
    if list_type == 'puppies':
        item = session.query(Puppy, Shelter).filter(Puppy.id==item_id, Puppy.shelter_id==Shelter.id).first()
        template='puppy_view.html'
    elif list_type == 'shelters':
        item = session.query(Shelter).filter(Shelter.id==item_id).first()
        template = 'shelter_view.html'
    elif list_type == 'owners':
        item = session.query(Owner).filter(Owner.id==item_id).first()
        template= 'owner_view.html'
    else:
        return render_template('error404.html')
    if item is None:
        flash("Could not find the "+list_type+"!")
        return redirect(url_for('list_view', list_type=list_type))
    else:
        ans = render_template(template, list_type=list_type, item_id = item_id, item = item)
        return ans

@app.route('/<string:list_type>/new', methods=['GET', 'POST'])
def item_new(list_type):
    if request.method == 'GET':
        if list_type in ['puppies', 'shelters', 'owners'] :
            template = list_type +'_add.html'
            puppies = session.query(Puppy).all()
            shelters = session.query(Shelter).all()
            owners = session.query(Owner).all()
            return render_template( template, list_type=list_type, puppies = puppies, shelters = shelters, owners = owners)
        else:
            return render_template('error404.html')
    elif request.method == 'POST':
        if list_type == 'puppies':
            thisshelter = session.query(Shelter).filter(Shelter.name==request.form['shelter']).first()
            newItem = Puppy(name=request.form['name'], dateOfBirth=datetime.datetime.strptime(request.form['dateOfBirth'], '%Y-%m-%d').date(), gender=request.form['gender'],
                 weight=request.form['weight'], picture=request.form['link'], shelter_id=thisshelter.id )
        elif list_type =='shelters':
            newItem = Shelter(name=request.form['name'], address=request.form['address'], city = request.form['city'],
                state = request.form['state'], zipCode = request.form['zipCode'], website = request.form['website'])
        elif list_type == 'owners':
            newItem = Owner(name=request.form['name'], surname=request.form['surname'],
                 gender =request.form['gender'], age = request.form['age'])
        session.add(newItem)
        session.commit()
        flash("Succesfully added the new item!")
        return redirect(url_for('list_view', list_type=list_type))

@app.route('/<string:list_type>/del/<int:item_id>', methods=['GET', 'POST'])
def item_delete(list_type, item_id):
    if list_type == 'puppies':
        item = session.query(Puppy).filter(Puppy.id==item_id).first()
    elif list_type == 'shelters':
        item = session.query(Shelter).filter(Shelter.id==item_id).first()
    elif list_type == 'owners':
        item = session.query(Owner).filter(Owner.id==item_id).first()
    else:
        return render_template('error404.html')
    if request.method == 'GET':
        if item is None:
            flash("Could not find the "+list_type+"!")
            return redirect(url_for('list_view', list_type=list_type))
        else:
            ans = render_template('item_delete.html', list_type=list_type, item_id = item_id, item = item)
            return ans
    elif request.method =='POST':
        session.delete(item)
        session.commit()
        return redirect(url_for('list_view', list_type=list_type))


@app.route('/<string:list_type>/edit/<int:item_id>', methods=['GET', 'POST'])
def item_edit(list_type, item_id):
    if list_type == 'puppies':
        item = session.query(Puppy).filter(Puppy.id==item_id).first()
        template = 'puppies_edit.html'
    elif list_type == 'shelters':
        item = session.query(Shelter).filter(Shelter.id==item_id).first()
        template = 'shelters_edit.html'
    elif list_type == 'owners':
        item = session.query(Owner).filter(Owner.id==item_id).first()
        template = 'owners_edit.html'
    else:
        return render_template('error404.html')

    shelters = session.query(Shelter).all()

    if request.method == 'GET':
        ans = render_template( template, list_type=list_type, item_id = item_id, item = item, shelters=shelters)
        return ans
    elif request.method == 'POST':
        if list_type == 'puppies':
            item.name=request.form['name']
            item.dateOfBirth=datetime.datetime.strptime(request.form['dateOfBirth'], '%Y-%m-%d').date()
            item.gender=request.form['gender']
            item.weight=request.form['weight']
            item.picture=request.form['link']
            item.shelter_id = request.form['shelter']
            print 'post 132'
        elif list_type =='shelters':
            item.name=request.form['name']
            item.address=request.form['address']
            item.city = request.form['city']
            item.state = request.form['state']
            item.zipCode = request.form['zipCode']
            item.website = request.form['website']
        elif list_type == 'owners':
            item.name=request.form['name']
            item.surname=request.form['surname']
            item.gender =request.form['gender']
            item.age = request.form['age']
        print '3'
        session.add(item)
        session.commit()
        print '4'
        flash("Succesfully edited the item!")
        print '5'
        return redirect(url_for('list_view', list_type=list_type))



#Starts Server
if __name__ == '__main__':
    app.secret_key = 'super_secret_key'
    app.debug = True
    app.run(host='0.0.0.0', port=5000)
