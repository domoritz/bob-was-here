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
from model import Location, Tapin
from google.appengine.api import users
from google.appengine.ext import db
import logging as log

jinja_environment = jinja2.Environment(
	loader=jinja2.FileSystemLoader(os.path.dirname(__file__) + "/templates/"))

def format_datetime(datetime):
	return datetime.strftime('%d/%m/%Y')

jinja_environment.filters['datetime'] = format_datetime
jinja_environment.globals.update(zip=zip)

class MainHandler(webapp2.RequestHandler):
	def get(self):
		loc = Location(slug="foo", name="FOO", description="a nice foo bar")
		loc.put()

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
			print location.name

			q = Tapin.gql("WHERE location = :location", location = location)

			for tapin in q:
				people.append(tapin.user)

			template = jinja_environment.get_template("location.html")
			self.response.out.write(template.render({
				"username":users.get_current_user().nickname(),
				"location": location,
				"people": people
			}))
		self.abort(404)


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
			tapins = Tapin.gql("WHERE user_id = :user", user = user.user_id()) 

			template = jinja_environment.get_template("user.html")
			self.response.out.write(template.render({"user": user, "tapins": tapins}))
		else:
			self.redirect(users.create_login_url("/"))


class TapHandler(webapp2.RequestHandler):
	def get(self, slug):
		if users.get_current_user():
			q = Location.gql("WHERE slug = :slug", slug=slug)
			location = q.get()
			if location:
				tapin = Tapin()
				tapin.user_id = users.get_current_user().user_id()
				tapin.location = location.key()
				tapin.put()
				self.redirect("/location/" + slug)
		else:
			self.redirect(users.create_login_url("/tapin/%s" % slug))


class ProgressHandler(webapp2.RequestHandler):
	def get(self):
		tapins = Tapin.gql("ORDER BY date")
		template = jinja_environment.get_template("tapins.html")
		self.response.out.write(template.render({"tapins":tapins}))


def handle_404(request, response, exception):
	response.set_status(404)
	response.out.write('404 - Not found')


app = webapp2.WSGIApplication([
	('/', MainHandler),
	('/location/(.+)', LocationHandler),
	('/user', UserHandler),
	('/tap/(.+)', TapHandler),
	('/tapins', ProgressHandler),
	('/__delete', DeleteHandler)
	], debug=True)

app.error_handlers[404] = handle_404
