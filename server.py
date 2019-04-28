import socket

from aiohttp import web

from handlers import handle_hello


# init aiohttp server
app = web.Application()


# setup associations between routes and appropriate handlers
app.add_routes([
    # dummy for testing
    web.get('/', handle_hello),
    web.get('/{name}', handle_hello)
])


# determine own ip address to give a nicer startup message
s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
s.connect(('1.1.1.1', 80))
own_ip = s.getsockname()[0]


# start server
web.run_app(app, host=own_ip)
