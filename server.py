###############################################################################
##
##  Copyright (C) 2011-2013 Tavendo GmbH
##
##  Licensed under the Apache License, Version 2.0 (the "License");
##  you may not use this file except in compliance with the License.
##  You may obtain a copy of the License at
##
##      http://www.apache.org/licenses/LICENSE-2.0
##
##  Unless required by applicable law or agreed to in writing, software
##  distributed under the License is distributed on an "AS IS" BASIS,
##  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
##  See the License for the specific language governing permissions and
##  limitations under the License.
##
###############################################################################

import sys

from autobahn.twisted.websocket import WebSocketServerFactory, \
													WebSocketServerProtocol

from autobahn.twisted.resource import WebSocketResource, \
												  HTTPChannelHixie76Aware
from twisted.internet import reactor
from twisted.python import log
from twisted.web.server import Site
from twisted.web.static import File

class WebsiteProtocol(WebSocketServerProtocol):
	waiters = set()

	def onConnect(self, request):
		print("Website: WebSocket client connecting: {}".format(request)) #TODO: what's in request?

	def onOpen(self):
		print("Website: connection open.")
		WebsiteProtocol.waiters.add(self)

	def onMessage(self, payload, isBinary): #TODO: isBinary?
		log.msg("Website: got message %s" % payload)
		msg = ("Website server received: %s" % payload)
		WebsocketProtocol.send_updates(msg)

	def onClose(self, wasClean, code, reason):
		print("WebSocket: connection closed: {0}".format(reason))
		WebsiteProtocol.waiters.remove(self)

	@classmethod
	def send_updates(cls, msg):
		log.msg("Website: sending messages to %d waiters" % len(cls.waiters))
		for waiter in cls.waiters:
			try:
				waiter.sendMessage(msg, False)
			except Exception, e:
				log.err("Website: Error sending message. %s" % str(e))

class WebsocketProtocol(WebSocketServerProtocol):
	waiters = set()

	def onConnect(self, request):
		print("Websocket: Websocket client connecting: {0}".format(request.peer))

	def onOpen(self):
		print("WebSocket: connection open.")
		WebsocketProtocol.waiters.add(self)

	def onMessage(self, payload, isBinary):
		log.msg("Websocket: got message %s" % payload)
		msg = ("Websocket server received: %s" % payload)
		WebsiteProtocol.send_updates(msg)

	def onClose(self, wasClean, code, reason):
		print("WebSocket: connection closed: {0}".format(reason))
		WebsocketProtocol.waiters.remove(self)

	@classmethod
	def send_updates(cls, msg):
		log.msg("Websocket: sending message to %d waiters" % len(cls.waiters))

		for waiter in cls.waiters:
			try:
				waiter.sendMessage(msg, False)
			except Exception, e:
				log.err("Websocket: Error sending message. %s" % str(e))

if __name__ == '__main__':

	log.startLogging(sys.stdout)

	#### Website reactor setup 
	#factory = WebSocketServerFactory("ws://localhost:8080", debug = debug, debugCodePaths = True)
	websiteFactory = WebSocketServerFactory("ws://localhost:8080", debug = False)
	websiteFactory.protocol = WebsiteProtocol
	websiteFactory.setProtocolOptions(allowHixie76 = True) # needed if Hixie76 is to be supported
	websiteResource = WebSocketResource(websiteFactory)
	root = File(".") # server static files under "/" ..
	root.putChild("ws", websiteResource) # WebSocket server under "/ws"
	site = Site(root)  # both under one Twisted Web Site
	site.protocol = HTTPChannelHixie76Aware # needed if Hixie76 is to be supported
	reactor.listenTCP(8080, site)

	#### Websocket reactor setup
	websocketFactory = WebSocketServerFactory("ws://localhost:9090", debug = False)
	websocketFactory.protocol = WebsocketProtocol
	reactor.listenTCP(9090, websocketFactory)

	reactor.run()
