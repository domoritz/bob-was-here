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

jinja_environment = jinja2.Environment(
	loader=jinja2.FileSystemLoader(os.path.dirname(__file__) + "/templates/"))

def format_datetime(datetime):
	pass

jinja_environment.filters['datetime'] = format_datetime


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
			print location.name

			q = Tapin.gql("WHERE location = :location", location = location)

			for tapin in q:
				people.append(tapin.user)

			template = jinja_environment.get_template("location.html")
			self.response.out.write(template.render({
				"username":users.get_current_user().nickname(),
				"location": location.name,
				"people": people
			}))

		else:
			self.error(404)
			self.response.out.write("Not found")


class NotFoundPageHandler(webapp2.RequestHandler):
	def get(self):
		self.error(404)
		self.response.out.write('Not found')


class TapHandler(webapp2.RequestHandler):
	def get(self, slug):
		if users.get_current_user():
			locations = Location.gql("WHERE slug = :slug", slug=slug)
			if locations:
				location[0].key()
				pass
		else:
			self.redirect(users.create_login_url("/tap/%s" % slug))


app = webapp2.WSGIApplication([
	('/', MainHandler),
	('/location/(.*)', LocationHandler),
	('/.*', NotFoundPageHandler),
	('/tap/(.*)',TapHandler)
	], debug=True)
