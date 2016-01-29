from sqlalchemy import Table, Column, ForeignKey, Integer, String, Date, Float, MetaData
from sqlalchemy.orm import relationship
from migrate.changeset.constraint import ForeignKeyConstraint

meta = MetaData()


#owner_id = Column('owner_id', Integer)
owner = ForeignKeyConstraint('owner_id', 'owner.id', 'puppy')

def upgrade(migrate_engine):
    meta.bind = migrate_engine
    puppy = Table('puppy', meta, autoload=True)
#    owner_id.create(puppy)
    owner.create(puppy)



def downgrade(migrate_engine):
    meta.bind = migrate_engine
    puppy = Table('puppy', meta, autoload=True)
#    owner_id.drop(puppy)
    owner.create(puppy)
