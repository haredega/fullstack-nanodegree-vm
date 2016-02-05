from puppies import app
from flask import render_template, url_for, request, redirect, flash, jsonify
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database_setup import Base, Puppy, PuppyPage, Shelter, Owner, dbConnect
import datetime
from sqlalchemy import func
from numpy import size
import string
import logic

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
    alphabet = string.ascii_lowercase
    if list_type == 'puppies':
        items = session.query(Puppy).all()
    elif list_type == 'shelters':
        items = session.query(Shelter).all()
    elif list_type == 'owners':
        items = session.query(Owner).all()
    else:
        return render_template('error404.html')
    ans = render_template('list_view.html', list_type = list_type, items = items, now=datetime.date.today(), alphabet=alphabet )
    return ans

@app.route('/<string:list_type>/<int:item_id>')
def item_view(list_type, item_id):
    if list_type == 'puppies':
        item = logic.view_puppy(item_id)
        template='puppy_view.html'
    elif list_type == 'shelters':
        item = session.query(Shelter).filter(Shelter.id==item_id).first()
        template = 'shelter_view.html'
    elif list_type == 'owners':
        item = session.query(Owner).filter(Owner.id==item_id).first()
        pets = session.query(Puppy).filter(Puppy.owner_id==item.id).all()
        template= 'owner_view.html'
        return render_template(template, list_type=list_type, item_id = item_id, item = item, pets=pets)
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

@app.route('/<string:list_type>/adopt/<int:item_id>')
def adopt(list_type, item_id):
    if list_type == 'puppies':
        puppy = session.query(Puppy).filter(Puppy.id==item_id).first()
        if puppy is not None:
            owners = session.query(Owner).all()
            return render_template('adopt.html', puppy=puppy, owners = owners, item_id=item_id, list_type=list_type)
        else:
            return render_template('error404.html')
    else:
        return render_template('error404.html')

@app.route('/<string:list_type>/adopt/<int:item_id>/<int:owner_id>/confirm', methods=['GET', 'POST'])
def adopt_confirm(list_type, item_id, owner_id):
    puppy = session.query(Puppy).filter(Puppy.id==item_id).first()
    owner = session.query(Owner).filter(Owner.id==owner_id).first()
    if list_type =='puppies' and puppy is not None and owner is not None:
        if request.method =='GET':
            return render_template('adopt_confirm.html', puppy=puppy, owner = owner, item_id=item_id, list_type=list_type)
        elif request.method == 'POST':
            puppy.owner_id = owner_id
            puppy.shelter_id =None
            session.add(puppy)
            session.commit()
            return redirect(url_for('item_view', list_type=list_type, item_id=item_id))
    else:
        return render_template('error404.html')

@app.route('/puppies/<int:item_id>/return/<int:owner_id>', methods=['GET', 'POST'])
def return_puppy(item_id, owner_id):
    puppy= session.query(Puppy).filter(Puppy.id==item_id).first()
    owner = session.query(Owner).filter(Owner.id==owner_id).first()
    shelters= session.query(Shelter).all()
    if puppy is None or owner is None:
        return render_template('error404.html')
    elif request.method =='GET':
        return render_template('return_puppy.html', puppy=puppy, owner = owner, shelters=shelters)
    elif request.method=='POST':
        puppy.owner_id=None
        puppy.shelter_id = request.form['shelter']
        session.add(puppy)
        session.commit()
        return redirect(url_for('item_view', list_type = 'owners', item_id=owner.id))


@app.route('/balance_population')
def balance_population():
    shelters= session.query(Shelter).all()
    result = logic.population_balancing(shelters)
    exchange = result[0]
    avg_occupancy = result[1]
    return render_template('balance_population.html', shelters = shelters, exchanges = exchange, avg_occupancy=avg_occupancy)

@app.route('/puppies/list/filter_by_shelter/<int:item_id>')
def puppies_filtered(item_id):
    ashelter = session.query(Shelter).filter(Shelter.id==item_id).first()
    if ashelter is not None:
        items = session.query(Puppy).filter(Puppy.shelter_id==item_id).order_by(Puppy.name).all()
        ans = render_template('list_view.html', list_type = 'puppies', items = items, now=datetime.date.today() )
        return ans
    else:
        return render_template('error404.html')

@app.route('/puppies/filter/<string:letter>')
def puppies_aZ(letter):
    items = session.query(Puppy).filter(Puppy.name.like(letter+'%')).order_by(Puppy.name).all()
    alphabet = string.ascii_lowercase
    print items
    if not items:
        return redirect(url_for('list_view', list_type= 'puppies'))
    else:
        ans = render_template('list_view.html', list_type = 'puppies', items = items, now=datetime.date.today(), alphabet=alphabet )
        return ans
