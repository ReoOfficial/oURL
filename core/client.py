import requests

from core.response import Response


class Client:

    def send(self, request):

        response = requests.request(
            method=request.method,
            url=request.url,
            headers=request.headers,
            data=request.body,
            timeout=request.timeout
        )

        return Response(response)