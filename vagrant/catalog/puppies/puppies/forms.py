from wtforms import Form, IntegerField, TextField, PasswordField, validators, SelectField, DecimalField, RadioField
from wtforms.fields.html5 import DateField
from wtforms.validators import ValidationError
import datetime

def data_check(form, field):
    if field.data > datetime.date.today():
        raise ValidationError('Date not be after today.')

class puppyForm(Form):
    shelter = SelectField('shelter', coerce=int)
    name = TextField('name', [validators.Required(), validators.Length(min=2, max=35)])
    dateOfBirth = DateField('dateOfBirth',[validators.Required(), data_check])
    gender = RadioField('gender', [validators.Required()],  choices=[('male', 'Male'), ('female', 'Female')] )
    weight = DecimalField('weight', places = 2)
    picture = TextField('picture', [validators.URL()])

class shelterForm(Form):
    name = TextField('name', [validators.Required(), validators.Length(min=4, max=140)])
    address = TextField('address')
    city = TextField('city', [validators.Required()])
    state = TextField('state', [validators.Required()])
    zipCode = TextField('zipCode')
    website = TextField('website', [validators.URL()])

class ownerForm(Form):
    name = TextField('name', [validators.Required(), validators.Length(min=4, max=40)])
    surname = TextField('surname', [validators.Required(), validators.Length(min=4, max=40)])
    gender = RadioField('gender', [validators.Required()], choices=[('male', 'Male'), ('female', 'Female')])
    age = IntegerField('age', [validators.Required(), validators.NumberRange(min =0, max = 130)] )
