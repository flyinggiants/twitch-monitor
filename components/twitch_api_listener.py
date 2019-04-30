import asyncio
import logging

from aiohttp.web_app import Application

import app_config_key
from services import twitch_api_service
from services.dashboard_relay import send_activity


async def start_loop(app: Application):
    async def wait_and_recurse():
        await asyncio.sleep(10)
        await start_loop(app)

    try:
        if not twitch_api_service.is_ready(app):
            await wait_and_recurse()

        await ping_followers(app)
        await wait_and_recurse()

    except asyncio.CancelledError:
        pass
    except BaseException as ex:
        logging.error(f'Error at loop of Twitch API Listener. Details: {str(ex)}')


async def ping_followers(app: Application):
    # Note: This has a delay of about one minute, but idk what to do against it
    #       see https://discuss.dev.twitch.tv/t/how-to-get-followers-in-real-time/9898/2

    try:
        user_id = app.get(app_config_key.TWITCH_USER_ID, None)
        if not user_id:
            return  # not ready yet
        data = await twitch_api_service.get('users/follows', app, {'to_id': user_id})
    except ValueError as ex:
        logging.error(f'Error at pinging Followers. Details: {str(ex)}')
        return

    old_followers = app.get(app_config_key.FOLLOWERS_STORE)
    current_followers = {}
    for follower in data.get('data', []):
        follower_id = follower.get('from_id')
        follower_name = follower.get('from_name')
        current_followers.update({follower_id: follower_name})

        if old_followers is not None and follower_id not in old_followers:
            await send_activity(f'New Follower: {follower_name}')

    if old_followers is not None:
        for old_follower_id in set(old_followers.keys()).difference(set(current_followers.keys())):
            await send_activity(f'Lost Follower: {old_followers.get(old_follower_id)}')

    app[app_config_key.FOLLOWERS_STORE] = current_followers.copy()
