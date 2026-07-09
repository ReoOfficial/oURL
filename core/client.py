import requests

from core.response import Response

from utils.errors import RequestTimeoutException, ConnectionException

class Client:

    def send(self, request):
        
        headers = request.headers.copy()

        if request.user_agent:
            headers["User-Agent"] = request.user_agent

        auth = None

        if request.auth:
            username, password = request.auth.split(":", 1)
            auth = (username, password)

        method = request.method

        if request.head:
            method = "HEAD"

        try:
            response = requests.request(
                method=request.method,
                url=request.url,
                headers=request.headers,
                data=request.body,
                timeout=request.timeout,
                verify=not request.insecure,
                allow_redirects=request.follow_redirects,
                auth=auth,
                cookies=request.cookies 
            )

            return Response(response)
        
        except requests.exceptions.Timeout:
            raise RequestTimeoutException(
                "Request timed out"
            )
    
        except requests.exceptions.ConnectionError:
            raise ConnectionException(
                "Connection failed"
            )