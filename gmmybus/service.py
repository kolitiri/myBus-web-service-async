import logging
import os
import sys

from aiohttp import web

from apis import TflApi


logging.basicConfig(
    stream=sys.stdout,
    format='%(asctime)-15s %(levelname)s %(message)s',
    level=logging.INFO
)
log = logging.getLogger(__name__)

@web.middleware
async def assert_json(request, handler):
    """ Assert that we only process JSON requests """
    try:
        json = await request.json()
    except Exception as e:
        msg = 'Invalid JSON format'
        log.error(f'{msg}')
        raise web.HTTPBadRequest(text=msg)

    log.info(f'({handler.__name__}) Receive: {json}')
    response = await handler(request)
    log.info(f'({handler.__name__}) Respond: {response.body}')

    return response

async def get_stops(request):
    """ Handle stops requests by instantiating an apis.Api object. """
    json_dict = await request.json()

    api = TflApi()
    log.info(api)
    stop_points = await api.make_stops_request(json_dict)

    return web.json_response(stop_points)

async def get_predictions(request):
    """ Handle predictions requests by instantiating an apis.Api object. """
    json_dict = await request.json()

    api = TflApi()
    predictions = await api.make_predictions_request(json_dict)

    return web.json_response(predictions)

async def factory():
    app = web.Application()
    app.add_routes([
        web.post('/stops', get_stops),
        web.post('/predictions', get_predictions)
    ])
    return app
