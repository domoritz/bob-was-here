from google.appengine.ext import db

class Location(db.Model):
	slug = db.StringProperty()
	name = db.StringProperty()
	description = db.StringProperty(multiline=True)


class Tapin(db.Model):
	user = db.UserProperty()
	location = db.ReferenceProperty(Location)
	date = db.DateTimeProperty(auto_now_add=True)