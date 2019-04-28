from urllib import parse

from aiohttp import web
from aiohttp.web_app import Application
from aiohttp.web_request import Request

_REDIRECT_URI = parse.quote('http://localhost:8080/auth-done')


def get_routes():
    return [
        ('/auth-start', handle_auth_start),
        ('/auth-done', handle_auth_done)
    ]


def handle_auth_start(request: Request):
    client_id = request.app['settings'].get_twitch_client_id()
    scopes = ['bits:read', 'channel:read:subscriptions', 'user:read:broadcast', 'chat:read', 'whispers:read']
    scopes_encoded = parse.quote(' '.join(scopes))

    raise web.HTTPFound(
        f'https://id.twitch.tv/oauth2/authorize?client_id={client_id}&redirect_uri={_REDIRECT_URI}&response_type=code'
        f'&response_type=code&scope={scopes_encoded}'
    )


async def handle_auth_done(request: Request):
    code = request.query.get('code')
    if not code:
        raise web.HTTPBadRequest(reason="Didn't get back a code from Twitch")

    params = {
        'code': code,
        'grant_type': 'authorization_code',
        'redirect_uri': _REDIRECT_URI
    }
    await _acquire_tokens(params, request.app)

    raise web.HTTPFound('/')  # redirect back to dashboard


async def auth_refresh(app: Application):
    params = {
        'refresh_token': app['twitch_refresh_token'],
        'grant_type': 'refresh_token'
    }
    await _acquire_tokens(params, app)


async def _acquire_tokens(params: dict, app: Application):
    params.update({
        'client_id': app['settings'].get_twitch_client_id(),
        'client_secret': app['settings'].get_twitch_client_secret()
    })

    aiohttp_session = app['aiohttp_session']

    async with aiohttp_session.post('https://id.twitch.tv/oauth2/token', params=params) as token_resp:
        try:
            token_resp_data = await token_resp.json()
            if 'access_token' not in token_resp_data or 'refresh_token' not in token_resp_data:
                raise ValueError()
        except BaseException:
            raise web.HTTPBadRequest(reason=f"Didn't get back tokens from Twitch. Details: {token_resp_data}")

    access_token = token_resp_data['access_token']
    app['twitch_access_token'] = access_token
    app['twitch_refresh_token'] = token_resp_data['refresh_token']

    headers = {
        'Authorization': f'OAuth {access_token}'
    }
    async with aiohttp_session.get('https://id.twitch.tv/oauth2/validate', headers=headers) as validate_resp:
        try:
            validate_resp_data = await validate_resp.json()
            if 'login' not in validate_resp_data or 'user_id' not in validate_resp_data:
                raise ValueError()
        except BaseException:
            raise web.HTTPBadRequest(reason=f"Couldn't validate login with Twitch. Details: {validate_resp_data}")

    app['twitch_login'] = validate_resp_data['login']
    app['twitch_user_id'] = validate_resp_data['user_id']
