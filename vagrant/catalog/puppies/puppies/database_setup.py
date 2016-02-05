#database setup file
import sys
from sqlalchemy import Column, ForeignKey, Integer, String, Date, Float, ForeignKeyConstraint
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

Base = declarative_base()

def dbConnect():
    #connecting db
    engine = create_engine('sqlite:///puppyshelter.db')
    Base.metadata.bind=engine
    DBSession = sessionmaker(bind = engine)
    session = DBSession()
    return session

#Class setup
class Shelter(Base):
    __tablename__ = 'shelter'
    name = Column(String(80), nullable=False)
    address = Column(String(250))
    city = Column(String(60))
    state = Column(String(60))
    zipCode = Column(String(15))
    website = Column(String(250))
    id = Column(Integer, primary_key=True)

    #V1 adds ocuppancy check for the shelters
    def current_occupancy(self, session):
        return session.query(Puppy).join("shelter").filter(Puppy.shelter_id==self.id).count()

class Puppy(Base):
    __tablename__ = 'puppy'
    name = Column(String(80), nullable=False)
    id = Column(Integer, primary_key=True)
    dateOfBirth = Column(Date)
    picture = Column(String)
    gender = Column(String(6), nullable=False)
    weight = Column(Float(precision=2))
    shelter_id = Column(Integer, ForeignKey('shelter.id'))
    shelter = relationship(Shelter)
    owner_id = Column(Integer, ForeignKey('owner.id'))
    owner = relationship("Owner")

#V1 adds puppy page  and owner table to the database schema
class PuppyPage(Base):
    __tablename__ = 'puppypage'
    id = Column(Integer, primary_key=True)
    url = Column(String(), nullable=False)
    puppy_description = Column(String(140))
    special_needs = Column(String(250))
    #puppy_id = Column(Integer, ForeignKey('puppy.id'), primary_key=True)
    #puppy = relationship(Puppy)
    puppy_id = ForeignKeyConstraint('puppy_id', 'puppy.id', Puppy)

class Owner(Base):
    __tablename__ = 'owner'
    id = Column(Integer, primary_key=True)
    name = Column(String(40), nullable=False)
    surname = Column(String(60), nullable=False)
    gender =  Column(String(2), nullable=False)
    age = Column(Integer, nullable=False)
    puppy= relationship("Puppy")


#insert at end of file
engine = create_engine('sqlite:///puppyshelter.db')
Base.metadata.create_all(engine)
