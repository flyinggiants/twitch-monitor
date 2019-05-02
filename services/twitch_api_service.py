from aiohttp.web_app import Application

import app_config_key
from components.twitch_auth import auth_refresh

"""
This module eases getting data from the main Twitch API
"""


# Helpers to check app state related to Twitch API

def ensure_token(app: Application) -> str:
    token = app.get(app_config_key.TWITCH_ACCESS_TOKEN)
    if not token:
        raise ValueError('No Token available!')
    return token


def is_ready(app: Application) -> bool:
    return app.get(app_config_key.TWITCH_READY) is not None


# Helpers to interact with the Twitch API
# see https://dev.twitch.tv/docs/api/reference/ for usage info (path and params)

# noinspection PyDefaultArgument
async def get(app: Application, path: str, params={}, is_retry=False):
    headers = {
        'Authorization': f'Bearer {ensure_token(app)}'
    }
    path = f'https://api.twitch.tv/helix/{path}'

    async with app[app_config_key.AIOHTTP_SESSION].get(path, params=params, headers=headers) as resp:
        if resp.status == 401:
            if is_retry:
                raise ValueError('Twitch-API gave back an Unauthorized error!')
            await auth_refresh(app)
            await get(app, path, params, True)
        elif resp.status != 200:
            resp_text = await resp.text()
            raise ValueError(f'Twitch-API gave back an error! Status: {resp.status}, Details: {resp_text}')
        resp_data = await resp.json()

    return resp_data
