import logging
import os
import ssl

from aiohttp import (
    ClientSession,
    web
)

log = logging.getLogger(__name__)


class Api():
    """ API class. """
    def __init__(self):
        self.sslcontext = ssl.create_default_context(
            purpose=ssl.Purpose.CLIENT_AUTH
        )

    def _query_str(self, params_dict):
        """ Convert a dict to a URI query component.

            Args:
                 params_dict (dict): The url params as a python dict

            Returns:
                (str): A URI query string
        """
        return '&'.join([f'{key}={val}' for key, val in params_dict.items()])

    async def _make_get_request(self, endpoint, params):
        """ Make an async GET request using an aiohttp.ClientSession.

            Args:
                endpoint (str): Target endpoint url
                params (dict): A dict of a GET request params

            Returns:
                A dict representation of the JSON response
        """
        try:
            async with ClientSession() as session:
                async with session.get(
                    endpoint,
                    params=params,
                    ssl=self.sslcontext
                ) as resp:
                    log.info(
                        f'Request: GET {endpoint}?{self._query_str(params)}'
                    )
                    return await resp.json()

        except Exception as e:
            msg = 'TFL Api request failed'
            log.error(f'{msg}: {str(e)}')
            raise web.HTTPInternalServerError(text='Oops! something went wrong')

        else:
            if resp.status != 200:
                msg = 'TFL Api request failed with status'
                log.error(f'{msg}: {resp.status}')
                raise web.HTTPInternalServerError(text='Oops! something went wrong')

class TflApi(Api):
    """ TFL API class """
    def __init__(self):
        super().__init__()
        self.stops_endpoint = 'https://api.tfl.gov.uk/StopPoint'
        self.predictions_endpoint = 'https://api.tfl.gov.uk/StopPoint/{}/Arrivals'
        self.app_id = os.environ['APP_ID']
        self.app_key = os.environ['APP_KEY']

    async def make_predictions_request(self, json_dict):
        """ Make a predictions requests to TFL Unified API

            Example request:
                https://api.tfl.gov.uk/StopPoint/490007705L/Arrivals?mode=bus

            Args:
                json_dict (dict): The incoming JSON request data

            Returns:
                predictions (list): A list of dicts containing buses information
        """
        try:
            naptan_id = json_dict['stop']['naptanId']

        except KeyError:
            msg = 'Invalid parameters for GET /predictions.'
            log.error(f'{msg}: {self._query_str(json_dict)}')
            raise web.HTTPBadRequest(text=msg)

        predictions_endpoint = self.predictions_endpoint.format(naptan_id)

        params = {
            'mode': 'bus',
            'app_id': self.app_id,
            'app_key': self.app_key,
        }

        tfl_resp = await self._make_get_request(predictions_endpoint, params)

        # Filter the response and return only required fields
        # lineName, timeToStation
        predictions = list()
        for prediction in tfl_resp:
            node = {
                'lineName': prediction['lineName'],
                'timeToStation': prediction['timeToStation'],
            }
            predictions.append(node)

        return predictions

    async def make_stops_request(self, json_dict):
        """ Make a stops request to TFL Unified API

            Args:
                json_dict (dict): The incoming JSON request data

            Returns:
                stop_points (dict): A dict mapping a list of stop
                                    dicts to the 'stopPoints' key
        """
        try:
            params = {
                'lat': json_dict['location']['latitude'],
                'lon': json_dict['location']['longtitude'],
                'radius': json_dict['location']['radius'],
                'stopTypes': json_dict['location']['stopTypes'],
                'returnLines': json_dict['location']['returnLines'],
                'app_id': self.app_id,
                'app_key': self.app_key,
            }

        except KeyError:
            msg = 'Invalid parameters for GET /stops.'
            log.error(f'{msg}: {self._query_str(json_dict)}')
            raise web.HTTPBadRequest(text=msg)

        tfl_resp = await self._make_get_request(self.stops_endpoint, params)

        # Filter the response and return only required fields
        # stopLetter, naptanId, distance
        stop_points = dict(stopPoints=list())
        for sp in tfl_resp['stopPoints']:
            try:
                node = {
                    'stopLetter': sp['stopLetter'],
                    'naptanId': sp['naptanId'],
                    'distance': sp['distance'],
                }
                stop_points['stopPoints'].append(node)
            except KeyError:
                # Unfortunately some stopPoints are inconsistent. Ignore them for now.
                log.warning(f'Skipping inconsistent stop_point: {sp}')
                continue

        return stop_points
