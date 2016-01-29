from flask import Flask, render_template, url_for, request, redirect, flash, jsonify
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database_setup import Base, Puppy, PuppyPage, Shelter, Owner, dbConnect
import datetime
from sqlalchemy import func
from numpy import size
import string
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
        q1 = session.query(Puppy, Shelter, Owner).filter(Puppy.id==item_id, Puppy.shelter_id==Shelter.id, Puppy.owner_id==Owner.id).first()
        q2 = session.query(Puppy, Shelter, Owner).filter(Puppy.id==item_id, Shelter.id==1, Puppy.owner_id==Owner.id).first()
        q3 =session.query(Puppy, Shelter, Owner).filter(Puppy.id==item_id, Puppy.shelter_id==Shelter.id, Owner.id==1).first()
        #If there's no corresponding Shelter, we'll send whatever shelter to the template
        if q1 is not None:
            item = q1
        elif q2 is not None:
            item = q2
        elif q3 is not None:
            item = q3
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
    shelter_occupancy = dict()
    #Creates a dictionnary with shelter.id x currente_occupancy and calculates the average population
    i = 0
    avg_occupancy = 0
    for shelter in shelters:
        occupancy = session.query(func.count(Puppy.id)).filter(Puppy.shelter_id==shelter.id).scalar()
        shelter_occupancy.update( {shelter.id: occupancy} )
        print str(shelter.id), str(occupancy)
        i += 1
        avg_occupancy+=occupancy
    if i > 0 :
        avg_occupancy = round(avg_occupancy/i, 0)
    else:
        avg_occupancy=0
    # Creates 2 dict with: the list of over populated shelters; list of under populated shelters
    over_charged = dict()
    vacant = dict()
    for shelter, occupancy  in shelter_occupancy.items():
        print 'Current occ: '+str(shelter)+'--> '+str(occupancy)
        if occupancy > avg_occupancy :
            over_charged.update({shelter: (occupancy-avg_occupancy) })
        elif occupancy < avg_occupancy :
            vacant.update({ shelter: (avg_occupancy-occupancy) })
        else:
            pass
    # Creates a tuple with the changes to be made between the shelters
    exchange = []
    for over_id, over_occ in over_charged.items():
        print 'Over: '+str(over_id)+'--> '+str(over_occ)
        if over_occ == 0:
            pass
        elif over_occ > 0:
            for under_id, under_occ in vacant.items():
                print 'Under check:'+str(under_id)+'-->'+str(under_occ)
                if under_occ == 0 :
                    pass
                elif over_occ > under_occ:
                    item = ( over_id, under_id, under_occ )
                    exchange.append(item)
                    vacant[under_id] = 0
                    over_charged[over_id] = over_occ - under_occ
                elif over_occ < under_occ:
                    item = ( over_id, under_id, over_occ )
                    exchange.append(item)
                    vacant[under_id] = under_occ - over_occ
                    over_charged[over_id] = 0
                elif over_occ == under_occ:
                    item = ( over_id, under_id, over_occ )
                    exchange.append(item)
                    vacant[under_id] = 0
                    over_charged[over_id] = 0
    print 'Exchange'
    print exchange
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



#Starts Server
if __name__ == '__main__':
    app.secret_key = 'super_secret_key'
    app.debug = True
    app.run(host='0.0.0.0', port=5000)
