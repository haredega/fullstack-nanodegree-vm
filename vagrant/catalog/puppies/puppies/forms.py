from wtforms import Form, IntegerField, TextField, PasswordField, validators, SelectField
from wtforms.fields.html5 import DateField


class puppyForm(Form):
    shelter = SelectField('shelter', coerce=int)
    name = TextField('name', [validators.Required(), validators.Length(min=2, max=35)])
    dateOfBirth = DateField('dateOfBirth',[validators.Required()])
    gender = TextField('gender', [validators.Required()])
    weight = IntegerField('weight')
    picture = TextField('picture')

class shelterForm(Form):
    shelter = TextField('name', [validators.Required(), validators.Length(min=4, max=140)])
    address = TextField('address')
    city = TextField('city', [validators.Required()])
    state = TextField('state', [validators.Required()])
    zipCode = TextField('zipCode')
    website = TextField('website')

class ownerForm(Form):
    name = TextField('name', [validators.Required(), validators.Length(min=4, max=40)])
    surname = TextField('surname', [validators.Required(), validators.Length(min=4, max=40)])
    gender = TextField('gender', [validators.Required()])
    age = IntegerField('age', [validators.Required()] )
