from database_setup import *
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database_setup import Base, Puppy, PuppyPage, Shelter, Owner, dbConnect
import datetime
from sqlalchemy import func
from numpy import size
import string

engine = create_engine('sqlite:///puppyshelter.db')
Base.metadata.bind=engine
DBSession = sessionmaker(bind = engine)
session = DBSession()

def population_balancing( shelters ):
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
    return [exchange, avg_occupancy]

def view_puppy(item_id):
    q1 = session.query(Puppy, Shelter, Owner).filter(Puppy.id==item_id, Puppy.shelter_id==Shelter.id, Puppy.owner_id==Owner.id).first()
    q2 = session.query(Puppy, Shelter, Owner).filter(Puppy.id==item_id, Shelter.id==1, Puppy.owner_id==Owner.id).first()
    q3 =session.query(Puppy, Shelter, Owner).filter(Puppy.id==item_id, Puppy.shelter_id==Shelter.id, Owner.id==1).first()
    q4 = session.query(Puppy, Shelter, Owner).filter(Puppy.id==item_id, Shelter.id==1, Owner.id==1).first()
    #If there's no corresponding Shelter, we'll send whatever shelter to the template
    if q1 is not None:
        item = q1
    elif q2 is not None:
        item = q2
    elif q3 is not None:
        item = q3
    else:
        item = q4
    return item
