#!/usr/bin/env python
#
# Copyright 2007 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
import webapp2
import jinja2
import os
from model import Location, Tapin, User
from google.appengine.api import users
from google.appengine.ext import db
import logging as log
import time
import json

jinja_environment = jinja2.Environment(
	loader=jinja2.FileSystemLoader(os.path.dirname(__file__) + "/templates/"))

def format_date(datetime):
	return datetime.strftime('%d/%m/%Y')

def format_time(datetime):
	return datetime.strftime('%H:%M')

def format_date_iso(datetime):
	return datetime.isoformat()

jinja_environment.filters['date'] = format_date
jinja_environment.filters['time'] = format_time
jinja_environment.filters['iso'] = format_date_iso
jinja_environment.globals.update(zip=zip)

class MainHandler(webapp2.RequestHandler):
	def get(self):
		if users.get_current_user():
			template = jinja_environment.get_template("index.html")
			self.response.out.write(template.render({"username":users.get_current_user().nickname()}))
		else:
			self.redirect(users.create_login_url("/"))


class LocationHandler(webapp2.RequestHandler):
	def get(self, slug):
		people = []

		q = Location.gql("WHERE slug = :slug", slug = slug)

		location = q.get()
		if location:
			tapins = Tapin.gql("WHERE location = :location ORDER BY date", location = location)

			from collections import defaultdict
			grouped = defaultdict(list)
			for tapin in tapins: 
				grouped[tapin.date.date()].append(tapin)

			tapin = self.request.get('tapin')
			
			template = jinja_environment.get_template("location.html")
			self.response.out.write(template.render({
				"user": users.get_current_user(),
				"location": location,
				"tapins": grouped,
				"tapin": tapin
			}))
		else:
			self.redirect("/new-location?slug=%s&message=not-found" % slug)


class DeleteHandler(webapp2.RequestHandler):
	def get(self):
		for x in [Location, Tapin]:
			query = x.all()
			entries = query.fetch(1000)
			db.delete(entries)


class UserHandler(webapp2.RequestHandler):
	def get(self):
		user = users.get_current_user()
		if user:
			tapins = Tapin.gql("WHERE user = :user ORDER BY date DESC", user = user)
			locations = []
			for loc in filter(None, map(lambda x: x.geolocation, tapins)):
				locations.append([loc.lat(), loc.lan()])
			pointjson = json.dumps(locations)

			template = jinja_environment.get_template("user.html")
			self.response.out.write(template.render({"user": user, "tapins": tapins, "pointjson": pointjson}))
		else:
			self.redirect(users.create_login_url("/"))


class TapHandler(webapp2.RequestHandler):
	def get(self, slug):
		if users.get_current_user():
			q = Location.gql("WHERE slug = :slug", slug=slug)
			location = q.get()
			if location:
				tapin = Tapin()
				tapin.user = users.get_current_user()
				tapin.location = location.key()
				tapin.put()
				self.redirect("/location/" + slug + "?tapin=" + str(tapin.key()))
		else:
			self.redirect(users.create_login_url("/tapin/%s" % slug))


class ProgressHandler(webapp2.RequestHandler):
	def get(self):
		tapins = Tapin.gql("ORDER BY date")
		template = jinja_environment.get_template("tapins.html")
		self.response.out.write(template.render({"tapins":tapins}))


class NewLocationHandler(webapp2.RequestHandler):
	def post(self):
		slug = self.request.get('slug')
		name = self.request.get('name')
		description = self.request.get('description')
		location = Location.gql("WHERE slug = :slug", slug=slug).get()
		if location:
			self.error(500)
			self.response.out.write('Slug already used')
		else:
			location = Location()
			location.slug = slug
			location.name = name
			location.description = description
			location.put()
			self.redirect("/location/%s" % slug)

	def get(self):
		slug = self.request.get('slug')
		message = self.request.get('message')
		if message == 'not-found':
			message = 'Slug has not been registered, please provide the details'
		template = jinja_environment.get_template("new-location.html")
		self.response.out.write(template.render({"slug":slug, "message":message}))

class GeolocationHandler(webapp2.RequestHandler):
	def post(self):
		tapin_key = self.request.get('tapin')
		latitude = self.request.get('latitude')
		longitude = self.request.get('longitude')
		if tapin_key:
			tapin_key = db.Key(tapin_key)
			tapin = Tapin.get(tapin_key)
			if tapin:
				tapin.geolocation = db.GeoPt(latitude, longitude)
				self.response.out.write('Location recorded')
			else:
				self.response.set_status(400)
				self.response.out.write('400 - Tapin not found')
		else:
			self.response.set_status(400)
			self.response.out.write('400 - Tapin not provided')

def handle_404(request, response, exception):
	response.set_status(404)
	response.out.write('404 - Not found')

app = webapp2.WSGIApplication([
	('/', MainHandler),
	('/location/(.+)', LocationHandler),
	('/user', UserHandler),
	('/tapin/(.+)', TapHandler),
	('/tapins', ProgressHandler),
	('/__delete', DeleteHandler),
	('/new-location', NewLocationHandler),
	('/geolocation', GeolocationHandler),
	], debug=True)

app.error_handlers[404] = handle_404
