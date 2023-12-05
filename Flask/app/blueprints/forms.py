from wtforms import Forms,StringField,EmailField,validators

class UserForm(Form):
    name=StringField('name',[validators.length(min=4,max=10)])
    email=EmailField('email',[validators.Email()])