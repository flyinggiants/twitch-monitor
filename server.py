import aiohttp
import itertools
import socket

from aiohttp import web

from services.settings_service import Settings
from components import auth, dashboard


# init aiohttp server
app = web.Application()
app['aiohttp_session'] = aiohttp.ClientSession()
try:
    app['settings'] = Settings()
except BaseException:
    raise Exception(
        'Failed when trying to load settings. Make sure you have setup a settings.yaml file.' + '\n' +
        'Refer to the settings-example.yaml file for its structure.'
    )


# setup associations between routes and appropriate handlers
routes = [auth.get_routes(), dashboard.get_routes()]
for path, handler in list(itertools.chain(*routes)):
    app.router.add_get(path, handler)

# determine own ip address to give a nicer startup message
s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
s.connect(('1.1.1.1', 80))
own_ip = s.getsockname()[0]


# start server
print(f'open website on http://{own_ip}:8080/')
web.run_app(app)
