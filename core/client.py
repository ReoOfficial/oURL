import requests

from core.response import Response

from utils.errors import (
    RequestTimeoutException, 
    ConnectionException,
    TooManyRedirectsException,
)

class Client:

    def send(self, request):
        
        headers = request.headers.copy()

        headers["User-Agent"] = (
            request.user_agent
            if request.user_agent
            else "MyCurl/2.0"
        )

        if (
            request.body is not None
            and not request.form_data
            and not request.form_files
            and not any(key.lower() == "content-type" for key in headers)
        ):
            headers["Content-Type"] = "application/x-www-form-urlencoded"

        auth = request.auth

        method = request.method

        if request.head:
            method = "HEAD"

        try:
            response = requests.request(

                method=method,
                url=request.url,
                headers=headers,

                data=request.form_data if request.form_data else request.body,
                files=request.form_files,

                timeout=request.timeout,
                verify=not request.insecure,
                allow_redirects=request.follow_redirects,

                auth=auth,
                cookies=request.cookies 
            )

            return Response(
                response,
                sent_headers=response.request.headers,
            )
        
        except requests.exceptions.Timeout as error:
            raise RequestTimeoutException(
                "Request timed out"
            ) from error
        
        except requests.exceptions.TooManyRedirects as error:
            raise TooManyRedirectsException(
                "Too many redirects"
            ) from error
    
        except requests.exceptions.ConnectionError as error:
            raise ConnectionException(
                "Connection failed"
            ) from error
        
        finally:
            if request.form_files:
                for file in request.form_files.values():
                    file.close()