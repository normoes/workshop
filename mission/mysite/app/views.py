from rest_framework.views import APIView
from rest_framework.renderers import JSONRenderer
# from rest_framework.response import Response
from rest_framework import status

from django.shortcuts import render
from django.conf import settings
from django.http import JsonResponse

from monerorpc.authproxy import AuthServiceProxy, JSONRPCException

from .serializers import InfoPostSerializer
from .exceptions import RpcConnectionError

import requests
import logging

logging.basicConfig()
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


TESTNET_INFO_HOST = 'http://localhost:8081'
TESTNET_INFO_ENDPOINT = '/get_info/'
TIMEOUT = 5


def index(request):
    return render(request,
                  'app/index.html',
                  {
                    'node_url': settings.NODE_URL,
                  })


def get_more_node_info(url, node_url):

    headers = dict({
        "Content-Type": "application/json"
    })

    data = dict({
        "node_url": node_url
    })

    response = requests.post(url=url,
                             json=data,
                             headers=headers,
                             timeout=TIMEOUT)

    logger.warn('{}: {}'.format(response.status_code, response.reason))
    response.raise_for_status()

    return response.json()


class InfoApiView(APIView):
    """Provide dameon info to the client.
    """

    renderer_classes = (JSONRenderer, )

    def post(self, request):
        """Requests services and gathers information on daemons.
        """

        serializer = InfoPostSerializer(data=request.data)
        if serializer.is_valid():
            # get the current balance
            rpc_connection = AuthServiceProxy('http://{0}:{1}/json_rpc'.format(
                serializer.data.get('node_url'),
                settings.WHICH_DAEMON_PORT))

            result = None
            try:
                result = rpc_connection.which_method()
            except (requests.HTTPError,
                    requests.ConnectionError,
                    JSONRPCException) as e:
                logger.error('RPC Error ' + str(e))

            response_info = dict({
                "nettype": result.get("nettype"),
                "offline": result.get("offline"),
                "status": result.get("status"),
                "height": result.get("height"),
                "top_block_hash": result.get("top_block_hash"),
                "rpc_connections_count": result.get("rpc_connections_count"),
            })

            result = None
            try:
                result = rpc_connection.which_method()
            except (requests.HTTPError,
                    requests.ConnectionError,
                    JSONRPCException) as e:
                logger.error('RPC Error ' + str(e))

            response_fee = dict({
                "fee": result.get("fee"),
            })

            result = None
            try:
                result = rpc_connection.which_method()
            except (requests.HTTPError,
                    requests.ConnectionError,
                    JSONRPCException) as e:
                logger.error('RPC Error ' + str(e))

            response_version = dict({
                "version": result.get("version"),
            })

            response = dict()
            response[settings.DAEMON_MAINNET_PORT] = dict()
            response[settings.DAEMON_MAINNET_PORT].update(response_info)
            response[settings.DAEMON_MAINNET_PORT].update(response_fee)
            response[settings.DAEMON_MAINNET_PORT].update(response_version)

            try:
                response.update(get_more_node_info(
                    url=TESTNET_INFO_HOST+TESTNET_INFO_ENDPOINT,
                    node_url=serializer.data.get('node_url')))
            except (requests.HTTPError,
                    requests.ConnectionError,
                    requests.RequestException) as e:
                logger.warn(str(e))

            return JsonResponse(response)
        logger.error(serializer.errors)
        return JsonResponse(serializer.errors,
                            status=status.HTTP_400_BAD_REQUEST)
