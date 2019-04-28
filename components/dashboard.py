from aiohttp import web
from aiohttp.web_request import Request

from services import twitch_api_service


def get_routes():
    return [
        ('/', handle_dashboard)
    ]


async def handle_dashboard(request: Request):
    twitch_api_service.ensure_token(request.app)  # will redirect if no token ready

    text = f"Hey {request.app['twitch_login']} (ID: {request.app['twitch_user_id']})!"
    return web.Response(text=text)
