import aiohttp

from aiohttp import web
from aiohttp.web_app import Application

from components.auth import auth_refresh


def ensure_token(app:Application) -> str:
    token = app.get('twitch_access_token')
    if not token:
        raise web.HTTPFound('/auth-start')
    return token


# noinspection PyDefaultArgument
async def get(path: str, app: Application, params={}, retry=False):
    headers = {
        'Authorization': f'Bearer {ensure_token(app)}'
    }
    path = f'https://api.twitch.tv/helix/{path}'

    async with app['aiohttp_session'].post(path, params=params, headers=headers) as resp:
        if resp.status == 401:
            if retry:
                raise ValueError('Twitch-API gave back an Unauthorized error!')
            await auth_refresh(app)
            await get(path, app, params, True)
        elif resp.status != 200:
            resp_text = await resp.text()
            raise ValueError(f'Twitch-API gave back an error! Status: {resp.status}, Details: {resp_text}')
        resp_data = await resp.json()

    return resp_data
