#!/usr/bin/env python
#

import os.path
import sys
import time

from twisted.python import log
from twisted.internet import reactor, task

import cyclone.escape
import cyclone.web
import cyclone.websocket
import subprocess32

from subprocess32 import Popen, PIPE, STDOUT
from twisted.internet.threads import deferToThread

from autobahn.twisted.websocket import WebSocketServerProtocol, \
                                       WebSocketServerFactory


class MyServerProtocol(WebSocketServerProtocol):
	#singleclient = 0
	waiters = set()

	def onConnect(self, request):
		print("Client connecting: {0}".format(request.peer))
		#MyServerProtocol.singleclient = self

	def onOpen(self):
		print("WebSocket connection open.")
		MyServerProtocol.waiters.add(self)

	def onMessage(self, payload, isBinary):
		log.msg("msp: got message %s" % payload)
		msg = ("server received: %s" % payload)
		command = {
					'msg': msg
		}
		#log.msg("sending received message")
		#UpdateSocketHandler.send_updates(command)
		UpdateSocketHandler.send_updates(command)

	def onClose(self, wasClean, code, reason):
		print("WebSocket connection closed: {0}".format(reason))
		MyServerProtocol.waiters.remove(self)

	@classmethod
	def send_updates(cls, msg):
		log.msg("msp:sending message to %d waiters" % len(cls.waiters))
		#singleclient.sendMessage(command)
		#cls.sendMessage(command)

		for waiter in cls.waiters:
			try:
				waiter.sendMessage(msg, False)
			except Exception, e:
				log.err("msp: Error sending message. %s" % str(e))


class Application(cyclone.web.Application):
	def __init__(self):

		handlers = [
			(r"/", MainHandler),
			(r"/updatesocket", UpdateSocketHandler),
		]
		settings = dict(
			cookie_secret="dYJtPMkeTm6v9IDl6xxzPLrRgI5kWkoeuw/ybu//0ic=",
			template_path=os.path.join(os.path.dirname(__file__), "templates"),
			static_path=os.path.join(os.path.dirname(__file__), "static"),
			xsrf_cookies=True,
			autoescape=None,
		)
		cyclone.web.Application.__init__(self, handlers, **settings)


class MainHandler(cyclone.web.RequestHandler):
	def initialize(self):
		pass

	def get(self):
		self.render("index.html")


class UpdateSocketHandler(cyclone.websocket.WebSocketHandler):
	waiters = set()

	def initialize(self):
		pass

	def connectionMade(self):
		log.msg("new connection")
		UpdateSocketHandler.waiters.add(self)

	def connectionLost(self, reason):
		UpdateSocketHandler.waiters.remove(self)

	@classmethod
	def send_updates(cls, command):
		log.msg("ush:sending message to %d waiters" % len(cls.waiters))
		for waiter in cls.waiters:
			try:
				waiter.sendMessage(command)
			except Exception, e:
				log.err("ush: Error sending message. %s" % str(e))

	@classmethod
	def notify_updated_image(cls):
		command = {
					'cmd': 'photoUpdated'
				  }
		UpdateSocketHandler.send_updates(command)

	def messageReceived(self, message):
		log.msg("ush: got message %s" % message)
		msg = ("server received: %s" % message)
		#parsed = cyclone.escape.json_decode(message)
		command = {
					'msg': msg
		}
		#log.msg("sending received message")
		#UpdateSocketHandler.send_updates(command)
		MyServerProtocol.send_updates(msg)

		#MyServerProtocol.passMessage(globalfactory.protocol, command)
		# Would do something with "parsed" dict here if we wanted to receive messages



def main():
	globalfactory = WebSocketServerFactory("ws://localhost:9090", debug = False)
	globalfactory.protocol = MyServerProtocol
	reactor.listenTCP(9090, globalfactory)

	reactor.listenTCP(8080, Application())
	reactor.run()


if __name__ == "__main__":
	log.startLogging(sys.stdout)
	main()

