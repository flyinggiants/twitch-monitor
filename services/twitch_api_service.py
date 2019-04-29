from aiohttp.web_app import Application

import app_config_key
from components.auth import auth_refresh


def ensure_token(app: Application) -> str:
    token = app.get(app_config_key.TWITCH_ACCESS_TOKEN)
    if not token:
        raise ValueError('No Token available!')
    return token


def is_ready(app: Application) -> bool:
    return app.get(app_config_key.TWITCH_READY) is not None


# noinspection PyDefaultArgument
async def get(path: str, app: Application, params={}, retry=False):
    headers = {
        'Authorization': f'Bearer {ensure_token(app)}'
    }
    path = f'https://api.twitch.tv/helix/{path}'

    async with app[app_config_key.AIOHTTP_SESSION].get(path, params=params, headers=headers) as resp:
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
