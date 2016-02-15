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
from forms import *

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
        puppies = session.query(Puppy).all()
        shelters = session.query(Shelter).all()
        owners = session.query(Owner).all()
        if list_type =='puppies':
            template = 'puppies_add.html'
            form = puppyForm()
            form.shelter.choices = [ (g.id, g.name) for g in session.query(Shelter).all() ]
        elif list_type =='shelters':
            template = 'shelters_add.html'
            form = shelterForm()
        elif list_type == 'owners':
            template = 'owners_add.html'
            form = ownerForm()
        else:
            template = 'error404.html'
            form = puppyForm()
            list_type = 'puppies'
        return render_template( template, list_type=list_type, puppies = puppies, shelters = shelters, owners = owners, form = form)
#handles POST
    elif request.method == 'POST':
        if list_type == 'puppies':
            form = puppyForm(request.form)
            form.shelter.choices = [ (g.id, g.name) for g in session.query(Shelter).all() ]
            if form.validate():
                thisshelter = session.query(Shelter).filter(Shelter.id==form.shelter.data).first()
                newItem = Puppy(name=form.name.data, dateOfBirth=form.dateOfBirth.data, gender=form.gender.data,
                     weight=form.weight.data, picture=form.picture.data, shelter_id=thisshelter.id )
            else:
                for fieldName, errorMessages in form.errors.iteritems():
                    for err in errorMessages:
                        flash('Error in '+fieldName+' field. '+err)
                return redirect(url_for('item_new', list_type = list_type))
        elif list_type =='shelters':
            form = shelterForm(request.form)
            if form.validate():
                newItem = Shelter(name=form.name.data, address=form.address.data, city = form.city.data,
                    state = form.state.data, zipCode = form.zipCode.data, website = form.website.data)
            else:
                for fieldName, errorMessages in form.errors.iteritems():
                    for err in errorMessages:
                        flash('Error in '+fieldName+' field. '+err)
                return redirect(url_for('item_new', list_type = list_type))
        elif list_type == 'owners':
            form = ownerForm(request.form)
            if form.validate():
                newItem = Owner(name=form.name.data, surname=form.surname.data,
                     gender =form.gender.data, age = form.age.data)
            else:
                for fieldName, errorMessages in form.errors.iteritems():
                    for err in errorMessages:
                        flash('Error in '+fieldName+' field. '+err)
                return redirect(url_for('item_new', list_type = list_type))
        session.add(newItem)
        session.commit()
        flash("Succesfully added "+form.name.data+"!")
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
        form = puppyForm()
        item = session.query(Puppy).filter(Puppy.id==item_id).first()
        form.shelter.choices = [ (g.id, g.name) for g in session.query(Shelter).order_by(Shelter.id).all() ]
        form.shelter.choices.append([0, ''])
        form.name.default = item.name
        form.gender.default = item.gender
        form.weight.default = item.weight
        form.picture.default = item.picture
        form.dateOfBirth.default = item.dateOfBirth
        if item.shelter_id is not None:
            form.shelter.default = item.shelter_id
        else:
            form.shelter.default = 0
        form.process()
        template = 'puppies_edit.html'
    elif list_type == 'shelters':
        form = shelterForm()
        item = session.query(Shelter).filter(Shelter.id==item_id).first()
        form.name.default = item.name
        form.address.default = item.address
        form.city.default = item.city
        form.state.default = item.state
        form.zipCode.default = item.zipCode
        form.website.default = item.website
        form.process()
        template = 'shelters_edit.html'
    elif list_type == 'owners':
        form = ownerForm()
        item = session.query(Owner).filter(Owner.id==item_id).first()
        form.name.default = item.name
        form.surname.default = item.surname
        form.age.default = item.age
        form.gender.default = item.gender
        form.process()
        template = 'owners_edit.html'
    else:
        return render_template('error404.html')

    shelters = session.query(Shelter).all()

    if request.method == 'GET':
        ans = render_template( template, list_type=list_type, item_id = item_id, item = item, shelters=shelters, form=form)
        return ans
    elif request.method == 'POST':
        if list_type == 'puppies':
            form = puppyForm(request.form)
            form.shelter.choices = [ (g.id, g.name) for g in session.query(Shelter).order_by(Shelter.id).all() ]
            form.shelter.choices.append([0, ''])
            if not form.validate():
                for fieldName, errorMessages in form.errors.iteritems():
                    for err in errorMessages:
                        flash('Error in '+fieldName+' field. '+err)
                return redirect(url_for('item_edit', list_type = list_type, item_id=item_id))
            item.name=form.name.data
            item.dateOfBirth=form.dateOfBirth.data
            item.gender=form.gender.data
            if form.weight.data is None:
                pass
            else:
                item.weight=form.weight.data
            item.picture=form.picture.data
            if form.shelter.data ==0:
                item.shelter_id = None
            else:
                item.shelter_id = form.shelter.data
        elif list_type =='shelters':
            form = shelterForm(request.form)
            if not form.validate():
                for fieldName, errorMessages in form.errors.iteritems():
                    for err in errorMessages:
                        flash('Error in '+fieldName+' field. '+err)
                return redirect(url_for('item_edit', list_type = list_type, item_id=item_id))
            item.name=form.name.data
            item.address=form.address.data
            item.city = form.city.data
            item.state = form.state.data
            item.zipCode = form.zipCode.data
            item.website = form.website.data
        elif list_type == 'owners':
            form = ownerForm(request.form)
            if not form.validate():
                for fieldName, errorMessages in form.errors.iteritems():
                    for err in errorMessages:
                        flash('Error in '+fieldName+' field. '+err)
                return redirect(url_for('item_edit', list_type = list_type, item_id=item_id))
            item.name=form.name.data
            item.surname=form.surname.data
            item.gender =form.gender.data
            item.age = form.age.data
        session.add(item)
        session.commit()
        flash("Succesfully edited "+form.name.data+"!")
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
