import asyncio
import logging

from aiohttp.web_app import Application

import app_config_key
from components.dashboard_relay import send_activity
from services import twitch_api_service

"""
This module listens on the Twitch API (i.e. continuously sends requests and checks for changes) to get real-time updates
"""


# Setup:

async def start_loop(app: Application):
    async def wait_and_recurse():
        await asyncio.sleep(1)
        await start_loop(app)

    try:
        if not twitch_api_service.is_ready(app):
            await wait_and_recurse()

        # add listeners:
        await listen_for_followers(app)

        # here we go again:
        await wait_and_recurse()

    except asyncio.CancelledError:
        pass
    except BaseException as ex:
        logging.error(f'{ex.__class__.__name__} at loop of Twitch Chat. Details: {str(ex)}')


# Actual listeners:

async def listen_for_followers(app: Application):
    # Note: This has a delay of about one minute, but idk what to do against it
    #       see https://discuss.dev.twitch.tv/t/how-to-get-followers-in-real-time/9898/2

    # uses https://dev.twitch.tv/docs/api/reference/#get-users-follows

    try:
        user_id = app.get(app_config_key.TWITCH_USER_ID, None)
        if not user_id:
            return  # not ready yet, abort
        data = await twitch_api_service.get(app, 'users/follows', {'to_id': user_id})
    except ValueError as ex:
        logging.error(f'Error at checking Followers. Details: {str(ex)}')
        return  # error, abort

    old_followers = app.get(app_config_key.FOLLOWERS_STORE)
    current_followers = {}
    for follower in data.get('data', []):
        follower_id = follower.get('from_id')
        follower_name = follower.get('from_name')
        current_followers.update({follower_id: follower_name})

        if old_followers is not None and follower_id not in old_followers:
            await send_activity(app,
                app[app_config_key.JINJA_ENV].get_template('activity/follow.jinja2').render(name=follower_name)
            )

    if old_followers is not None:
        for old_follower_id in set(old_followers.keys()).difference(set(current_followers.keys())):
            old_follower_name = old_followers.get(old_follower_id)
            await send_activity(app,
                app[app_config_key.JINJA_ENV].get_template('activity/unfollow.jinja2').render(name=old_follower_name)
            )

    app[app_config_key.FOLLOWERS_STORE] = current_followers.copy()
