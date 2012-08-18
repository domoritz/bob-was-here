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
from model import Location, Tapin
from google.appengine.api import users
from google.appengine.ext import db

class MainHandler(webapp2.RequestHandler):
	def get(self):
		if users.get_current_user():
			pass
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

			self.response.out.write(slug + " " + location.name + " " + people)
		else:
			self.error(404)
			self.response.out.write("Not found")


class NotFoundPageHandler(webapp.RequestHandler):
    def get(self):
        self.error(404)
        self.response.out.write('Not found')


app = webapp2.WSGIApplication([
	('/', MainHandler),
	('/location/(.*)', LocationHandler),
	('/.*', NotFoundPageHandler)
	], debug=True)
