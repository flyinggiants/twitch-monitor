import itertools
import logging
import os
import socket

import aiohttp
import aiohttp_jinja2
import jinja2
from aiohttp import web

import app_config_key
import components
from services.settings_service import Settings


class TwitchMonitor:
    def __init__(self):
        # setup nice logging
        logging.basicConfig(level=logging.INFO, format='%(asctime)s | %(levelname)s | %(name)s | %(message)s')
        logging.info('Starting Server...')

        # init aiohttp server
        app = web.Application()
        self.app = app

        # init settings helper
        try:
            app[app_config_key.SETTINGS] = Settings()
        except BaseException:
            raise Exception(
                'Failed when trying to load settings. Make sure you have setup a settings.yaml file.' + '\n' +
                'Refer to the settings-example.yaml file for its structure.'
            )

        # init http client
        app[app_config_key.AIOHTTP_SESSION] = aiohttp.ClientSession()

        # init templating
        jinja_loader = jinja2.FileSystemLoader('views/templates')
        aiohttp_jinja2.setup(app, loader=jinja_loader)
        app['static_root_url'] = '/static'
        app.router.add_static('/static/', path=os.path.dirname(os.path.abspath(__file__)) + '/views/static', name='static')

        app[app_config_key.JINJA_ENV] = jinja2.Environment(
            loader=jinja_loader
        )

        # init listeners
        listeners = [getattr(component, 'start_loop', None) for component in components.all_components]

        async def start_background_tasks(_app):
            for listen in listeners:
                if listen is not None:
                    _app.loop.create_task(listen(_app))

        app.on_startup.append(start_background_tasks)

        # setup associations between routes and appropriate handlers
        routes = [getattr(component, 'get_routes', lambda: [])() for component in components.all_components]
        for path, handler in list(itertools.chain(*routes)):
            app.router.add_get(path, handler)

    def start(self):
        # determine own ip address to give a nicer startup message
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(('1.1.1.1', 80))
        own_ip = s.getsockname()[0]

        # do the actual start-up
        print(f'open website on http://{own_ip}:8080/')
        web.run_app(self.app, access_log=None)  # blocks until shut-down


# run it for real
TwitchMonitor().start()
