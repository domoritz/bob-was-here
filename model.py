from google.appengine.ext import db
from google.appengine.api.users import User

class Location(db.Model):
	slug = db.StringProperty()
	name = db.StringProperty()
	description = db.StringProperty(multiline=True)
	

class Tapin(db.Model):
	user_id = db.StringProperty()
	location = db.ReferenceProperty(Location)
	date = db.DateTimeProperty(auto_now_add=True)