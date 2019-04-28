import aiohttp_jinja2
from aiohttp.web_request import Request

from services import twitch_api_service


def get_routes():
    return [
        ('/', handle_dashboard)
    ]


@aiohttp_jinja2.template('dashboard.html')
async def handle_dashboard(request: Request):
    twitch_api_service.ensure_token(request.app)  # will redirect if no token ready

    return {
        'login': request.app['twitch_login'],
        'id': request.app['twitch_user_id']
    }
