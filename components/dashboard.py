import aiohttp_jinja2
from aiohttp import web
from aiohttp.web_request import Request

import app_config_key
from services import twitch_api_service


def get_routes():
    return [
        ('/', handle_dashboard)
    ]


@aiohttp_jinja2.template('dashboard.html')
async def handle_dashboard(request: Request):
    try:
        twitch_api_service.ensure_token(request.app)
    except ValueError:
        raise web.HTTPFound('/auth-start')

    return {
        'name': request.app[app_config_key.TWITCH_NAME],
        'id': request.app[app_config_key.TWITCH_USER_ID]
    }
