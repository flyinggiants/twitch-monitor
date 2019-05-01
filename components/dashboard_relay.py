import asyncio
import logging

import aiohttp
from aiohttp import web
from aiohttp.web_app import Application
from aiohttp.web_request import Request

import app_config_key
from services import twitch_api_service


def get_routes():
    return [
        ('/ws/activity', handle_activity_sub)
    ]


async def handle_activity_sub(request: Request):
    while not twitch_api_service.is_ready(request.app):
        await asyncio.sleep(10)

    ws = web.WebSocketResponse()
    await ws.prepare(request)

    if app_config_key.WEBSOCKET_ACTIVITY_CLIENTS not in request.app:
        request.app[app_config_key.WEBSOCKET_ACTIVITY_CLIENTS] = []
    request.app[app_config_key.WEBSOCKET_ACTIVITY_CLIENTS].append(ws)

    logging.info('Activity-Web Socket opened')

    async for msg in ws:
        # noinspection PyUnresolvedReferences
        if msg.type == aiohttp.WSMsgType.ERROR:
            logging.info(f'Activity-Web Socket closed with exception {ws.exception()}')
            break

    logging.info('Activity-Web Socket closed')
    return ws


async def send_activity(app: Application, data: str):
    for client in app.get(app_config_key.WEBSOCKET_ACTIVITY_CLIENTS, []):
        await client.send_str(data)
